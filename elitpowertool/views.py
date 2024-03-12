from rest_framework.views import APIView
from utility.StandardResponse import StandardResponse
from rest_framework import status
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from elitpowertool.models import Order, UnitsModel, VoltagePower, DeviceThermalInfo, DevicesCategories
from elitpowertool.serializer import OrderListSerializer,OrderSerializer,VoltagePowerSerializer, UnitSerializer, DeviceThermalInfoSerializer,DevicesCategoriesSerializer
from utility.model_serializer_rel import allSerializerModel
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
import re
from django.http.request import QueryDict
from django.http import HttpResponse
import logging
from utility.summary_parse import OrderParser
import io
logger = logging.getLogger(__name__)


class CreateBaseView(APIView):
    """
    Create Base class is the main class of the creating any type of instance in database
    It has get and post method
    class_serializer(Serializer): Set the instance serializer
    class_name(str): Give the class name it is helpful to give the particular message in response
    custom_message(str): Custom message in order to Error message
    _allow_get_request(bool): default False, Get request is required or not for child class
    class_model(Model): Model of the instance for fetch data from database
    content_type(str): It is only used for the circuit type
    soft_delete(bool): default False, specify soft delete for model instance
    """
    class_serializer = ModelSerializer
    class_name = 'Class Name'
    custom_message = ''
    _allow_get_request = False
    class_model = Model
    content_type = None
    soft_delete = False
    def parse_for_createdby(self, req):
        """
        Parse the created_by and update_by in request data
        & set data in request.data
        param: request
        return: None
        """
        # change the dict to editable and can update
        if isinstance(req.data, QueryDict):
            req.data._mutable = True
        # parsing after mutable & update
        parse_data = {'created_by': req.user.id,
                      'updated_by': req.user.id}
        req.data.update(parse_data)
        return

    def get(self, request):
        """
         Get request of the API
        :param request: (request) from the API
        :return: (response) json response to the API
        """

        if self._allow_get_request:
            try:
                # if model is soft delete then get request
                if self.soft_delete:
                    all_object = self.class_model.objects.filter(is_active=True)
                # else get all values
                else:
                    all_object = self.class_model.objects.all()
                all_object_slzr = self.class_serializer(all_object, many=True)
                return StandardResponse(status.HTTP_200_OK, data=all_object_slzr.data)
            except Exception as e:
                logger.error(str(e))
                return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Bad request')
        else:
            return StandardResponse(status.HTTP_405_METHOD_NOT_ALLOWED, message='Method is not allowed')


    def post(self, request):
        """
            Post request of the API
            :param request: (request) from the API
            :return: (response) json response to the API
        """
        try:
            if request.user:
                self.parse_for_createdby(request)

            object_slzr = self.class_serializer(data=request.data)
            if object_slzr.is_valid():
                object_slzr.save()
                # it is used for the handling circuit type response change
                if self.content_type:
                    __cp_value = {'circuit_type': self.content_type}
                    __cp_value.update(object_slzr.data)
                    return StandardResponse(status.HTTP_201_CREATED, data= __cp_value)
                # Normal response
                return StandardResponse(status.HTTP_201_CREATED, data = object_slzr.data)
            return StandardResponse(status.HTTP_400_BAD_REQUEST, error=object_slzr.errors, message='Something is wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message= f"{self.custom_message if self.custom_message else self.class_name} or something went wrong")


class BaseIdView(APIView):
    """
        Base View of the objects by ids class is the main class of the get, update and delete any type of instance in database
        It has get, patch and delete method
        class_serializer(Serializer): Set the instance serializer
        class_name(str): Give the class name it is helpful to give the particular message in response
        class_model(Model): Model of the instance for fetch data from database
        custom_message(str): Custom message in order to Error message
        has_permission_need(bool): default True, any user type has permission to make the request
        content_type(str): It is only used for the circuit type
        soft_delete(bool): default False, specify soft delete for model instance

    """

    class_serializer = ModelSerializer
    class_model = Model
    class_name = "Custom name"
    custom_message = ''
    soft_delete = True
    content_type = None
    has_permission_need = True
    def get_object_byid(self,object_id):
        """
         Get any object based on the primary key
        :param object_id:(uuid or int) primary key of the instance to get
        :return: object model instance
        """
        try:
            if self.soft_delete:
                 object_with_id = self.class_model.objects.get(pk=object_id, is_active=True)
            else:
                object_with_id = self.class_model.objects.get(pk=object_id)
            return object_with_id
        except Exception as e:
            print(e)
            return None
    def parse_for_updatedby(self, req):
        """
            Parse the update_by in request data
            & set data in request.data
            param: request
            return: None
        """
        if isinstance(req.data, QueryDict):
            req.data._mutable = True
        parse_data = {'updated_by': req.user.id}
        req.data.update(parse_data)
        return
    def has_permission_URD(self, request, object):
        """
        Check the permission for the update, read and delete by user
        :param request: (request) To get the user
        :param object: (model instance) to see the ownership
        :return:(bool) True or False based on the user
        """
        if not self.has_permission_need:
            return True
        elif request.user and (request.user.is_superuser or request.user.is_staff):
            return True
        elif request.user and request.user.id == object.created_by_id:
            return True
        else:
            return False
    def get(self, request, object_id):
        """
        Get request
        :param request:(request) Request from the API URL
        :param object_id: (uuid or int) Object id or the primary key of the model instance
        :return: (response) json response
        """
        object_with_id = self.get_object_byid(object_id)
        if object_with_id and self.has_permission_URD(request, object_with_id):
            object_slzr = self.class_serializer(object_with_id)
            return StandardResponse(status.HTTP_200_OK, data = object_slzr.data)
        else:
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message=f"{self.custom_message} or something went wrong")


    def patch(self, request, object_id):
        """
        Patch request for the update
        :param request:(request) Request from the API URL
        :param object_id: (uuid or int) Object id or the primary key of the model instance
        :return: (response) json response
        """
        object_with_id = self.get_object_byid(object_id)
        if object_with_id and request.data and self.has_permission_URD(request, object_with_id):
            if request.user:
                self.parse_for_updatedby(request)
            object_slzr = self.class_serializer(object_with_id, data=request.data, partial=True)
            if object_slzr.is_valid():
                object_slzr.save()
                # for the circuit type response modify
                if self.content_type:
                    __cp_value = {'circuit_type': self.content_type}
                    __cp_value.update(object_slzr.data)
                    return StandardResponse(status.HTTP_200_OK, data = __cp_value)
                # General response
                return StandardResponse(status.HTTP_200_OK, data = object_slzr.data, message=f" {self.class_name} data is updated")
            else:
                return StandardResponse(status.HTTP_400_BAD_REQUEST, error=object_slzr.errors, message='Something is went worng')
        else:
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message= f"{self.custom_message} or something went wrong")

    def delete(self, request, object_id):
        """
        Delete method
        :param request:(request) Request from the API URL
        :param object_id: (uuid or int) Object id or the primary key of the model instance
        :return: (response) json response
        """

        object_with_id = self.get_object_byid(object_id)
        # for the hard delete
        if object_with_id and not self.soft_delete and self.has_permission_URD(request, object_with_id):
            object_with_id.delete()
            return StandardResponse(status.HTTP_200_OK, message=f"{self.class_name} is deleted")
        # for the soft delete
        elif object_with_id and self.soft_delete and self.has_permission_URD(request, object_with_id):
            object_with_id.is_active = False
            object_with_id.save()
            return StandardResponse(status.HTTP_200_OK, message=f"{self.class_name} is deleted")

        else:
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message = f"{self.custom_message} or something went wrong")


class CreateDevicesCategories(CreateBaseView):
    """
       Create Base view handle for Create Device categories
        : Post request to create the device categories
        : Get request to get all device categories
    """
    permission_classes = [IsAuthenticated]
    class_serializer = DevicesCategoriesSerializer
    class_name = "Categories"
    _allow_get_request = True
    class_model = DevicesCategories
    soft_delete = True
    @staticmethod
    def is_admin_staff(request):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return False
    def post(self, request):
        if self.is_admin_staff(request):
            return super().post(request)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')




class CreateUnit(CreateBaseView):
    """
    Create Base view handle
      : Post request to create the Units
    """
    permission_classes = [IsAuthenticated]
    class_serializer = UnitSerializer
    class_name = 'Unit'
    _allow_get_request = True
    class_model = UnitsModel
    def post(self, request):
        if CreateDevicesCategories.is_admin_staff(request):
            return super().post(request)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')


class CreateVoltagePower(CreateBaseView):
    """
        Create Base view handle for
          : Post request to create voltage power
    """
    permission_classes = [IsAuthenticated]
    class_serializer = VoltagePowerSerializer
    class_name = 'Voltage Power'


class CreateCircuitParam(CreateBaseView):
    """
        Create Base view handle
          : Post request to create the Circuit Param
    """
    permission_classes = [IsAuthenticated]
    class_name = "Circuit Parameter"

    @staticmethod
    def to_lower(val):
        """
        for string change to lower string so matching is easy
        :param val: (any value)
        :return: (str) lower case
        """
        if isinstance(val, str):
            return val.lower()
        return str(val).lower()
    def post(self, request):
        try:
            slzr_type = self.to_lower(request.data.get('cp_type', None))
            request.data.update(request.data.get('cp_data', None))
            if slzr_type and request.data:
                # Base of the type of the circuit set the serializer and model class
                self.class_serializer , self.class_model = allSerializerModel.get(slzr_type, (ModelSerializer, Model))
                self.content_type = {'content_id': ContentType.objects.get_for_model(self.class_model).id,
                                     'circuit_type': slzr_type}
                # creating method from the parent class
                return super().post(request)
            else:
                raise Exception('Something went wrong')
        except Exception as e:
            logger.error(e)
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message="Looks like wrong circuit types")




class CreateDeviceThermalInfo(CreateBaseView):
    """
        Create Base view handle
          : Post request to create the device and thermal info
    """
    permission_classes = [IsAuthenticated]
    class_serializer = DeviceThermalInfoSerializer
    class_name = 'Device and Thermal info'

class CircuitParamById(BaseIdView):
    """
        Circuit Param
        BaseIdView view handle
          : GET request to get the circuit parameters
          : Patch request to update the circuit parameters
          : Delete request to delete the circuit parameters
    """
    permission_classes = [IsAuthenticated]
    class_name = "Circuit Parameter"
    custom_message = "Circuit details is not found"

    def model_slzr(self):
        all_slzr = []
        for vals in allSerializerModel.values():
            if vals in all_slzr:
                continue
            all_slzr.append(vals)
        return all_slzr
    def get(self, request, circuit_param_id):
        """
        Get request
        :param request:(request) Request from the API URL
        :param circuit_param_id: (uuid) circuit parameter object instance id
        :return: (response) json response
        """

        # based on the id search in all fields for circuit parameter
        for class_slzr , class_m in self.model_slzr():
            self.class_serializer, self.class_model = class_slzr, class_m
            res = super().get(request, circuit_param_id)
            if res.status_code == 200:
                content_type_id = ContentType.objects.get_for_model(self.class_model).id
                # getting the name of the model from class name to send the response to the user
                sentence = re.findall('[A-Z][^A-Z]*', str(self.class_model).replace(">", '').replace("'", ''))
                res.data.pop('status')
                return StandardResponse(status.HTTP_200_OK,data ={'circuit_type': {'circuit_type': sentence[-1].lower(), 'content_id': content_type_id}, 'cp_data': {**res.data['data']}})
        return res

    def patch(self, request, circuit_param_id):
        """
                Get patch request to update
                :param request:(request) Request from the API URL
                :param circuit_param_id: (uuid) circuit parameter object instance id
                :return: (response) json response
        """
        try:
            slzr_type = CreateCircuitParam.to_lower(request.data.get('cp_type', None))
            request.data.update(request.data.get('cp_data', None))
            if slzr_type and request.data:
                # select the serializer and model type based on the type of the circuit
                self.class_serializer, self.class_model = allSerializerModel.get(slzr_type, (ModelSerializer, Model))
                self.content_type = {'content_id': ContentType.objects.get_for_model(self.class_model).id,
                                     'circuit_type': slzr_type}
                # inherit the base patch method to update
                return super().patch(request, circuit_param_id)
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message= 'Something went wrong or bad request')


    def delete(self, request, circuit_param_id):
        """
                Delete request for delete
                :param request:(request) Request from the API URL
                :param circuit_param_id: (uuid) circuit parameter object instance id
                :return: (response) json response
        """
        try:
            # based on id searching circuit in all circuit param table
            for class_slzr , class_m in self.model_slzr():
                self.class_serializer, self.class_model = class_slzr, class_m
                res = super().delete(request, circuit_param_id)
                #if we delete based on it send the response
                if res.status_code == 200:
                    return res
            raise Exception('Circuit parameter is not found')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message= "Circuit parameter is not found or something went wrong")


class DeviesCategoriesByID(BaseIdView):
    """
            Device Categories
            BaseIdView view handle
              : GET request to get the device categories
              : Patch request to update the device categories
              : Delete request to delete the device categories
    """
    permission_classes = [IsAuthenticated]
    class_serializer = DevicesCategoriesSerializer
    class_name = "Devices Categories"
    class_model = DevicesCategories
    custom_message = "Device Category Not found"

    def get(self, request, category_id):
        return super().get(request, category_id)
    
    def patch(self, request, category_id):
        if CreateDevicesCategories.is_admin_staff(request):
            return super().patch(request, category_id)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')
    def delete(self, request, category_id):
        if CreateDevicesCategories.is_admin_staff(request):
            return super().delete(request, category_id)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')




class VoltagePowerById(BaseIdView):
    """
                Voltage Power
                BaseIdView view handle
                  : GET request to get the voltage power
                  : Patch request to update the voltage power
                  : Delete request to delete the voltage power
    """
    permission_classes = [IsAuthenticated]
    class_serializer = VoltagePowerSerializer
    class_name = 'Voltage_power'
    class_model = VoltagePower
    custom_message = 'Voltage Power is not found'

    def get(self, request, voltage_power_id):
        return super().get(request, voltage_power_id)
    def patch(self, request, voltage_power_id):
        return super().patch(request, voltage_power_id)
    def delete(self, request, voltage_power_id):
        return super().delete(request, voltage_power_id)


class UnitViewById(BaseIdView):
    """
                Units
                BaseIdView view handle
                  : GET request to get the unit
                  : Patch request to update the unit
                  : Delete request to delete the unit
    """
    permission_classes = [IsAuthenticated]
    class_serializer = UnitSerializer
    class_model = UnitsModel
    class_name = "Unit"
    custom_message = 'Unit is not Found'
    soft_delete = False
    has_permission_need = False
    def get(self, request, unit_id):
        return super().get(request, unit_id)
    def patch(self, request, unit_id):
        if CreateDevicesCategories.is_admin_staff(request):
            return super().patch(request, unit_id)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')
    def delete(self, request, unit_id):
        if CreateDevicesCategories.is_admin_staff(request):
            return super().delete(request, unit_id)
        else:
            return StandardResponse(status.HTTP_401_UNAUTHORIZED, message='Unauthorized')

# Device and thermal info integration by Id
class DeviceThermalInfoById(BaseIdView):
    """
                Device and thermal info
                BaseIdView view handle
                  : GET request to get the device and thermal info
                  : Patch request to update the device and thermal info
                  : Delete request to delete the device and thermal info
    """
    permission_classes = [IsAuthenticated]
    class_serializer = DeviceThermalInfoSerializer
    class_model = DeviceThermalInfo
    class_name = "Device and Thermal"
    custom_message = "Device and Thermal Data Not found"
    def get(self, request, device_thermal_id):
        return super().get(request, device_thermal_id)
    def patch(self, request, device_thermal_id):
        return super().patch(request, device_thermal_id)
    def delete(self, request, device_thermal_id):
        return super().delete(request, device_thermal_id)




class CreateOrder(CreateBaseView):

    permission_classes = [IsAuthenticated]
    class_serializer = OrderSerializer
    class_name = 'Order details'
    class_model = Order

#order creation view
class OrderBYID(BaseIdView):
    """
                Order
                BaseIdView view handle
                  : GET request to get the order
                  : Patch request to update the order
                  : Delete request to delete the order
    """
    permission_classes = [IsAuthenticated]
    class_serializer = OrderSerializer
    class_name = "Order details"
    class_model = Order
    custom_message = 'Order is not found'
    soft_delete = False

    def get(self, request, order_id):
        return super().get(request, order_id)

    def patch(self, request, order_id):
        return super().patch(request, order_id)

    def check_and_delete(self, instance):
        if instance:
            instance.delete()

    def delete(self, request, order_id):
        try:
            order = self.get_object_byid(order_id)
            self.check_and_delete(order.mosfet_raw)
            self.check_and_delete(order.voltage_power)
            self.check_and_delete(order.device_thermal_info)
            self.check_and_delete(order.circuit_param)
            self.check_and_delete(order.mosfet)
            return StandardResponse(status.HTTP_200_OK, message='data is deleted')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='order is not found', error='something went wrong')



class CustomPageNumberPagination(PageNumberPagination):
    """
    customize the pagination for the order list
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

class OrderListview(generics.ListAPIView):
    """
    Order lists
    """
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    serializer_class = OrderListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    def get_queryset(self):
        # super user can see all user list
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Order.objects.filter(is_active = True).order_by('-updated_at')
        # customer user can see only theirs
        return Order.objects.filter(is_active = True, created_by = self.request.user.id).order_by('-updated_at')


class DownloadCSV(APIView):
    """
    Download the Csv file based on the order
        Get: get request with order id download the csv file
    """
    permission_classes = [IsAuthenticated]
    def get(self, request,order_id):
        """
                Get request for the API URL
                :param request: (reqeust) Request from the API URL
                :param order_id: (uuid) order id is required to fetch the order
                :return: (response) CSV file
        """
        try:
            order = Order.objects.get(pk=order_id, is_active=True)
            if order and Summary.has_permission_URD(request, order):
                slzr = OrderSerializer(order)
                # parse the order in csv
                order_parser = OrderParser(slzr.data)
                df = order_parser.parser(csv= True)
                # Create an in-memory buffer to write the DataFrame to CSV
                buffer = io.StringIO()
                df.to_csv(buffer, index=False)
                response = HttpResponse(buffer.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="device-info.csv"'
                return response
            raise Exception('Something went wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='something went wrong', error='order is my not found')
class Summary(APIView):
    """
    Summary Parsing for the order
      Get: request for the summary of the order with order id
    """
    permission_classes = [IsAuthenticated]
    @staticmethod
    def has_permission_URD(request, object):
        """
                Check the permission for get by user
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
    def get(self, request, order_id):
        """
        Get request for the API URL
        :param request: (reqeust) Request from the API URL
        :param order_id: (uuid) order id is required to fetch the order
        :return: (response) json response
        """
        try:
            order = Order.objects.get(pk= order_id, is_active = True)
            if order and self.has_permission_URD(request, order):
                slzr = OrderSerializer(order)
                # parse the order into required json
                order_parser = OrderParser(slzr.data)
                data = order_parser.parser()
                # response
                return StandardResponse(status.HTTP_200_OK, data = data, message='summary of the order')
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='something went wrong', error='You are not authorized or Order is not found')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong')




