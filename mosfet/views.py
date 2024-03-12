from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FileUploadParser
from mosfet.serializer import PDFSerializer, CoordinatesTableSerializer, MosfetSerializer
import os
from mosfet.models import MosfetRawData, MosfetData
from mosfet.scripts.myscript_graph_ext import allextract_images_with_file
from mosfet.scripts.coordinates_handler import CoordinatesHandler
from mosfet.scripts.table_extraction import table_extractor_main
from utility.StandardResponse import StandardResponse
from mosfet.scripts.mosfet_calculate import MosfetCalculator
import logging
# Create your views here.


logger = logging.getLogger(__name__)


class TakeCoordinates(APIView):
    """
            Mosfet raw data Handle
             : post request to create mosfet raw data
        """

    permission_classes = [IsAuthenticated]

    def parse_for_createdby_and_coordinate_data(self, req, coordinate_data = {}):
        """
                Parse the created & update_by in request data
                & set data in request.data
                param: request
                param: coordinates_data (dict): dict of the coordinates
                return: (dict)
        """

        parse_data = {'created_by': req.user.id,
                      'updated_by': req.user.id,
                      'coordinates_data': coordinate_data}

        parse_data.update(req.data.get('table_data', None))
        return parse_data


    def post(self, request):
        """
                    Post request of the API
                    :param request: (request) from the API
                    :return: (response) json response to the API
        """
        try:
            # get the Actual coordinates with the help of CoordinatesHandler class
            c_handler = CoordinatesHandler(request.data.get('bounding_box'), request.data.get('scale_data'), request.data.get('coordinates'))
            # getting original coordinates
            data = c_handler.original_coordinates()
            # serialize the data
            slzr = CoordinatesTableSerializer(data=self.parse_for_createdby_and_coordinate_data(request, data), context= {'request': request})
            if slzr.is_valid():
                slzr.save()
                return StandardResponse(status.HTTP_201_CREATED,data = slzr.data)
            return StandardResponse(status.HTTP_400_BAD_REQUEST, error = slzr.errors, message='Something went wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message="something went wrong or Image url or coordinates data")


class TakeCoordinateBYId(APIView):
    """
      Mosfet raw data Create Handler
    """
    permission_classes = [IsAuthenticated]
    _soft_delete = True

    def get_coordinate_data_by_id(self, cord_id):
        """
                 Get any object based on the primary key
                :param cord_id:(uuid) primary key of mosfetrawdata the instance to get
                :return: mosfetrawdata model instance
        """

        try:
            cord_data = MosfetRawData.objects.get(mosfet_raw_id= cord_id, is_active = True)
            return cord_data
        except:
            return None

    def parse_for_updatedby_and_coordinate_data(self, req, coordinate_data={}):
        """
                        Parse the  update_by in request data
                        & set data in request.data
                        param: request
                        param: coordinates_data (dict): dict of the coordinates
                        return: (dict)
        """

        parse_data = {'updated_by': req.user.id,
                      'coordinates_data': coordinate_data}

        parse_data.update(req.data.get('table_data', None))
        return parse_data

    @staticmethod
    def has_permission_URD(request, object):
        """
                Check the permission for the update, read and delete by user
                :param request: (request) To get the user
                :param object: (model instance) to see the ownership
                :return:(bool) True or False based on the user
        """

        if request.user and (request.user.is_superuser or request.user.is_staff):
            return True
        elif request.user and request.user.id == object.created_by_id:
            return True
        else:
            return False
    def get(self, request, mosfet_raw_id):
        """
                Get request
                :param request:(request) Request from the API URL
                :param mosfet_raw_id (uuid) mosfet_raw_id  or the primary key of the mosfet_raw_data model instance
                :return: (response) json response
        """

        try:
            mosfet_raw = self.get_coordinate_data_by_id(mosfet_raw_id)
            if mosfet_raw and self.has_permission_URD(request, mosfet_raw ):
                slzr = CoordinatesTableSerializer(mosfet_raw)
                return StandardResponse(status.HTTP_200_OK, data = slzr.data, message='Successfully get the coordinates data')
            raise Exception('Coordinates Data is not found or something wrong')

        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, error=str(e), message='something went wrong')


    def patch(self, request, mosfet_raw_id):
        """
            Patch request
             :param request:(request) Request from the API URL
             :param mosfet_raw_id (uuid) mosfet_raw_id  or the primary key of the mosfet_raw_data model instance
             :return: (response) json response
        """
        try:
            mosfet_raw = self.get_coordinate_data_by_id(mosfet_raw_id)
            if mosfet_raw and self.has_permission_URD(request, mosfet_raw):
                # for update calculate new coordinates data based on new request data
                c_handler = CoordinatesHandler(request.data.get('bounding_box'), request.data.get('scale_data'),
                                       request.data.get('coordinates'))
                data = c_handler.original_coordinates()
                # new data and old data send to serializer
                slzr = CoordinatesTableSerializer(mosfet_raw, data = self.parse_for_updatedby_and_coordinate_data(request, data), context= {'request': request},partial=True)
                if slzr.is_valid():
                    slzr.save()
                    return StandardResponse(status.HTTP_200_OK, data = slzr.data, message='Coordinates data is updated and Again calculate Mosfet')
                return StandardResponse(status.HTTP_400_BAD_REQUEST, error=slzr.errors, message='Something went wrong')
            raise Exception("Wrong mosfet calculation data request or something went wrong")
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong', error=str(e))

    def delete(self, request, mosfet_raw_id):
        """
                    Delete request
                     :param request:(request) Request from the API URL
                     :param mosfet_raw_id (uuid) mosfet_raw_id  or the primary key of the mosfet_raw_data model instance
                     :return: (response) json response
        """
        try:
            mosfet_raw = self.get_coordinate_data_by_id(mosfet_raw_id)
            if mosfet_raw and self.has_permission_URD(request, mosfet_raw):
                if self._soft_delete:
                    mosfet_raw.is_active = False
                    mosfet_raw.save()
                else:
                    mosfet_raw.delete()
                return StandardResponse(status.HTTP_200_OK, message='Data is deleted')
            raise Exception("Wrong mosfet calculation data request or something went wrong")
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, error='Something went wrong or Id is not matched', message=str(e))


class UploadMosfetPDF(CreateAPIView):
    """
            Upload mosfet pdf uploading
            Inherit base create api view from django
             : Post request to upload the mosfet pdf
    """

    serializer_class = PDFSerializer
    parser_classes = (MultiPartParser,FileUploadParser)

    def post(self, request, *args, **kwargs):
        """
           Post request of the API
            :param request: (request) from the API
            :return: (response) json response to the API
        """
        try:
            slzr = self.get_serializer(data = request.data)
            slzr.is_valid(raise_exception=True)
            # get the file name , file path and base file path when saving the pdf in media/pdfs/
            file_name_uuid, file_path, base_file_path = slzr.save()
            # Extract image from the pdf
            allextract_images_with_file(file_path, os.path.join(base_file_path, 'output'))
            # Table Extraction from pdf
            table_data =table_extractor_main(file_path)
            # internal folder names where images are savings
            first_graph_choice = '1st_Pass_Graphs'
            final_graph_choice = 'FInal_Graph_Required'
            # Convert image paths to the URLs
            first_graph_list = [request.build_absolute_uri(f'/media/pdfs/output/{file_name_uuid}/{first_graph_choice}/{each_file}') for each_file in os.listdir(os.path.join(base_file_path, 'output', file_name_uuid, first_graph_choice))]
            final_graph_list = [request.build_absolute_uri(f'/media/pdfs/output/{file_name_uuid}/{final_graph_choice}/{each_file}') for each_file in os.listdir(os.path.join(base_file_path, 'output', file_name_uuid, final_graph_choice))]
            # delete the pdf after graphs and table extractions
            if True and os.path.isfile(file_path):
                os.remove(file_path)
            return StandardResponse(status.HTTP_200_OK,data = {
                                   'final_path': final_graph_list,
                                    'other_path': first_graph_list,
                                     'table_data': table_data}, message='file Uploaded and Graph extracted' )
        except Exception as e:
            print(e)
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong')



class MosfetCalculateAPI(APIView):
    """
        Calculate mosfet data
         : Get request to calculate mosfet data with order id
    """
    permission_classes = [IsAuthenticated]

    def mosfet_handler(self, order, mosfet_final_data):
        """
        :param order: order instance
        :param mosfet_final_data:  mosfet data after calculation
        :return: (serializer) of the MosfetSerializer
        """
        # if mosfet is exist we have to update only
        if order.mosfet:
            mosfet_final_data.update({'updated_by': self.request.user.id})
            slzr = MosfetSerializer(order.mosfet, data=mosfet_final_data, partial=True)
            if slzr.is_valid():
                slzr.save()
            return slzr
        # we have to create new mosfet data and add the id to the order instance
        else:
            mosfet_final_data.update({'updated_by': self.request.user.id,
                                      'created_by': self.request.user.id})
            slzr = MosfetSerializer(data=mosfet_final_data)
            if slzr.is_valid():
                data_model = slzr.save()
                order.mosfet = data_model
                order.save()
            return slzr

    def get(self, request ,order_id):
        """
          Get request
            :param request:(request) Request from the API URL
            :param order_id (uuid) order  or the primary key of the order model instance
            :return: (response) json response
        """
        try:
            # calculate the mosfet data
            mosfet_calc = MosfetCalculator(order_id)
            # get order and mosfet calulated data
            order, mosfet_final_data = mosfet_calc.get_final_mosfet_data()
            if (not order) or (not mosfet_final_data):
                return StandardResponse(status.HTTP_400_BAD_REQUEST, message='You did some mistake in previous steps, You could place Order', error='Values are not correct')
            slzr = self.mosfet_handler(order, mosfet_final_data)
            if not slzr.errors:
                return StandardResponse(status.HTTP_200_OK, data = slzr.data, message='Final mosfet data is saved')
            return StandardResponse(status.HTTP_400_BAD_REQUEST, error = slzr.errors,message='Something is wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong')


class MosfetCalculateBYId(APIView):
    """
        Calculate mosfet data
          : Get request to calculate mosfet data with mosfet_id
          : Delete request to calculate mosfet data with mosfet_id
    """
    permission_classes = [IsAuthenticated]

    def get_mosfet_cal_data(self, calc_id):
        """
        Get the instance from database
        :param calc_id:(uuid)  of the mosfetdata
        :return: instance of mostetdata or None
        """
        try:
            calc_data = MosfetData.objects.get(mosfet_id= calc_id, is_active = True)
            return calc_data
        except:
            return None
    def delete(self, request, mosfet_calc_id):
        """
                Delete method
                :param request:(request) Request from the API URL
                :param mosfet_calc_id: (uuid) mosfetdata Object id or the primary key of the model instance
                :return: (response) json response
        """
        try:
            mosfet = self.get_mosfet_cal_data(mosfet_calc_id)
            if mosfet and TakeCoordinateBYId.has_permission_URD(request, mosfet):
                mosfet.delete()
                return StandardResponse(status.HTTP_200_OK, message='Data is deleted')
            raise Exception('Something went wrong')
        except Exception as e:
            logger.error(e)
            StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong ', error='Id is not found')

    def get(self, request, mosfet_calc_id):
        """
            Get method
              :param request:(request) Request from the API URL
              :param mosfet_calc_id: (uuid) mosfetdata Object id or the primary key of the model instance
              :return: (response) json response
        """
        try:
            mosfet = self.get_mosfet_cal_data(mosfet_calc_id)
            if mosfet and TakeCoordinateBYId.has_permission_URD(request, mosfet):
                slzr = MosfetSerializer(mosfet)
                return StandardResponse(status.HTTP_200_OK, data = slzr.data)
            raise Exception('Something went wrong')
        except Exception as e:
            logger.error(e)
            StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, error='Something went  wrong  ', message='Id is not found')

