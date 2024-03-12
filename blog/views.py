from blog.models import Blog
from blog.serializers import BlogSerializer, ImageFileSerializer, BlogListSerializer
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
import logging
from utility.StandardResponse import StandardResponse
from elitpowertool.views import BaseIdView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.filters import SearchFilter
from django.http.request import QueryDict


logger = logging.getLogger(__name__)


class BlogView(APIView):
    permission_classes = [IsAuthenticated]
    class_serializer = BlogSerializer
    class_model = Blog
    def staff_and_admin_permission(self, request):
        """
                Check the permission for the update, read and delete by user is admin or staff
                :param request: (request) To get the user
                :return:(bool) True or False based on the user
        """

        if request.user and (request.user.is_superuser or request.user.is_staff):
            return True
        else:
            return False
    def parse_for_createdby(self, req):
        """
                Parse the created_by and update_by in request data
                & set data in request.data
                param: requesst
                return: None
        """
        if isinstance(req.data, QueryDict):
            req.data._mutable = True
        parse_data = {'created_by': req.user.id,'updated_by': req.user.id}
        req.data.update(parse_data)
        return

    def post(self, request):
        """
                    Post request of the API
                    :param request: (request) from the API
                    :return: (response) json response to the API
        """

        try:
            if self.staff_and_admin_permission(request):
                self.parse_for_createdby(request)
                serializer = BlogSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response({
                        'error': serializer.errors,
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Something went wrong'
                    }, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({
                    'data': {},
                    'status': status.HTTP_201_CREATED,
                    'message': 'Blog created Successfully'
                }, status=status.HTTP_201_CREATED)
            raise Exception('Something went wrong Or You are not authorized')
        except Exception as e:
            logger.error(str(e))
            return Response({
                'error': 'Please check fields',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Something went wrong'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlogbyId(APIView):
    """
                Blog view by id
                  : GET request to get the blog
                  : Patch request to update the blog
                  : Delete request to delete the blog
    """
    permission_classes = [IsAuthenticated]
    def getblogbyid(self, blog_id):
        """
                 Get blog instance based on the primary key
                :param blog_id:(uuid) primary key of the instance to get
                :return: blog model instance
        """

        try:
            blog = Blog.objects.get(pk=blog_id, is_active=True)
            return blog
        except Exception as e:
            return None

    def get(self, request, blog_id):
        """
                Get request
                :param request:(request) Request from the API URL
                :param blog_id: (uuid) blog id of the blog model instance
                :return: (response) json response
        """

        try:
            blog = self.getblogbyid(blog_id)
            if not blog:
                return Response({"status": status.HTTP_204_NO_CONTENT,
                                 "message": "No blog"
                                 }, status=status.HTTP_204_NO_CONTENT)
            blog_slzr = BlogSerializer(blog)
            return Response( {
                'data': blog_slzr.data,
                'status': status.HTTP_200_OK,
                'message': 'Blog fetched successfully'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response({
                'error': 'Blog id is not correct',
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'Something went wrong'
            }, status=status.HTTP_400_BAD_REQUEST)

    def staff_and_admin_permission(self, request):
        """
                Check the permission for the  user is admin or staff
                :param request: (request) To get the user
                :return:(bool) True or False based on the user
        """
        if request.user and (request.user.is_superuser or request.user.is_staff):
            return True
        else:
            return False
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

    def patch(self, request, blog_id):
        """
                        Patch request
                        :param request:(request) Request from the API URL
                        :param blog_id: (uuid) blog id of the blog model instance
                        :return: (response) json response
        """
        blog = self.getblogbyid(blog_id)
        try:
            self.parse_for_updatedby(request)
            if blog and self.staff_and_admin_permission(request):
                if request.data == {}:
                    return Response({'message': 'Send some data'}, status = status.HTTP_400_BAD_REQUEST)
                if blog:
                    blog_slzr = BlogSerializer(blog, data=request.data, partial=True)
                    if blog_slzr.is_valid():
                        blog_slzr.save()
                        return Response({'data': blog_slzr.data,
                                              'status': status.HTTP_205_RESET_CONTENT,
                                              'message': 'Blog Updated Successfully'
                                         }, status=status.HTTP_205_RESET_CONTENT)
                    return Response({'error': blog_slzr.errors,
                                              'status': status.HTTP_400_BAD_REQUEST,
                                              'message': 'Fields are not correct'
                                         }, status=status.HTTP_400_BAD_REQUEST)
            raise Exception("You are not authorized")
        except Exception as e:
            logger.error(e)
            return Response({
                    'error': 'Please check the fields',
                    'status': status.HTTP_400_BAD_REQUEST,
                    'message': 'Something went wrong'
                }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, blog_id):
        """
                        Delete request
                        :param request:(request) Request from the API URL
                        :param blog_id: (uuid) blog id of the blog model instance
                        :return: (response) json response
        """
        try:
            blog = self.getblogbyid(blog_id)
            if self.staff_and_admin_permission(request):
                if not blog:
                    return Response({
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'Invalid blog id'
                    }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    blog.is_active = False
                    blog.save()
                    return Response({
                            'data': {},
                            'status': status.HTTP_200_OK,
                            'message': 'Blog deleted successfully'
                        }, status=status.HTTP_200_OK)
            else:
                return Response({'User': "User is not found or bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'data': {},
                'message': 'Something went wrong'
            }, status=status.HTTP_400_BAD_REQUEST)


class UploadImageForBlog(CreateAPIView):
    """
                    Blogs images uploading
                    Inherit base create api view from django
                      : Post request to upload the blog image
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ImageFileSerializer
    parser_classes = (MultiPartParser, FileUploadParser)

    def post(self, request, *args, **kwargs):
        """
                Post request of the API
                :param request: (request) from the API
                :return: (response) json response to the API
        """
        try:
            slzr = self.get_serializer(data = request.data)
            if slzr.is_valid(raise_exception=True):
                # get the path where image saved
                pathname = slzr.save()
                # Make path url
                return StandardResponse(status.HTTP_200_OK, message='Image is uploaded', data={'url': request.build_absolute_uri(f'/media/blogs/{pathname}')})
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='File is not valid or something went wrong')
        except Exception as e:
            logger.error(e)
            StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, error=str(e), message='Something went wrong')






class SingleBlogBYID(BaseIdView):
    """
            Single Blogs view by id
            Inherit base baseviewid from elitpowertool.views.py
                : Post request to upload the blog image
    """
    permission_classes = [AllowAny]
    has_permission_need = False
    class_model = Blog
    class_serializer = BlogSerializer
    class_name = 'Blog'
    custom_message = 'Blog is not found'
    def get(self, request, blog_id):
        """
            Get request
              :param request:(request) Request from the API URL
              :param blog_id: (uuid) blog id of the blog model instance
              :return: (response) json response
        """
        return super().get(request, blog_id)
    def patch(self, request, blog_id):
        # block this request
        return StandardResponse(status.HTTP_404_NOT_FOUND)
    def delete(self, request, blog_id):
        # blog this request
        return StandardResponse(status.HTTP_404_NOT_FOUND)





class CustomPagination(PageNumberPagination):
    """
        customize the pagination for the blog list
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

#Blog list
class QuerySearchListView(generics.ListAPIView):
    """
        Blog lists
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = BlogListSerializer
    filter_backends = [SearchFilter]
    # Add searching parameter
    search_fields = ['blog_title']

    def get_queryset(self):
        # customer user blog list
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            return Blog.objects.filter(is_active = True, status = 'published').order_by('-updated_at')
        # for admin user blog list
        if self.request.query_params.get('status'):
            return Blog.objects.filter(is_active = True, status = self.request.query_params.get('status')).order_by('-updated_at')
        return Blog.objects.filter(is_active = True, ).order_by('-updated_at')
