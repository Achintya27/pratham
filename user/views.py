from django.core.mail import send_mail
from django.conf import settings
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializer import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializer import MyTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from django.http.request import QueryDict
from rest_framework_simplejwt.views import TokenBlacklistView
import logging
from user.models import User, OTPModel
from utility.email_handler import OPT_Template
from utility.helper_func import generate_otp
from utility.StandardResponse import StandardResponse
# Create your views here.

logger = logging.getLogger(__name__)

# Creating User view
class CreateUser(APIView):
    """
        Create User view handle
         : Post request to create the user
    """

    @staticmethod
    def send_email(receiver_id, receiver_name, otp, subject = 'Email Verification'):
        """
        :param receiver_id: (str) user email id
        :param receiver_name: (str) user name
        :param otp: (str) otp
        :param subject: (str) default Email Verification
        :return:(1 0r 0) email  send response
        """
        if receiver_id and receiver_name and otp:
            email_res = send_mail(
                subject=subject,
                message=f'Your OTP is {otp}',
                from_email= settings.DEFAULT_FROM_EMAIL,
                recipient_list=[receiver_id],
                html_message= OPT_Template(receiver_name, otp)
            )
            return email_res
        raise Exception('Something went wrong')

    def user_exist(self, request):
        """
        check for user is existed or not
        :param request: request from API URL
        :return:(bool)
        """
        try:
            user = User.objects.get(email = request.data.get('email'), is_active = False)
            otp_data = OTPModel.objects.get(user=user.email)
            if user and otp_data:
                otp = generate_otp()
                if self.send_email(user.email,user.first_name, otp):
                    otp_data.otp = otp
                    otp_data.save()
                    return True
                return False
        except:
            return False

    def post(self, request):
        """
         Post request of the API
            :param request: (request) from the API
            :return: (response) json response to the API
        """
        try:
            if self.user_exist(request):
                return StandardResponse(status.HTTP_200_OK, message='OTP is send to the email , Please Varify')
            user_slzr = UserSerializer(data = request.data)
            if user_slzr.is_valid():
                otp = generate_otp()
                if self.send_email(user_slzr.validated_data.get('email', None), user_slzr.validated_data.get('first_name', None) , otp):
                    # Afet complete the email send, save user data
                    user_instance = user_slzr.save()
                    user_otp = OTPModel(user = user_instance.email, otp = otp)
                    user_otp.save()
                    return StandardResponse(status.HTTP_201_CREATED, data= user_slzr.data, message='User is created and otp is send to email')

                return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Please enter correct email', error='May be email is not receive Otp')
            return StandardResponse(status.HTTP_400_BAD_REQUEST, error=user_slzr.errors, message='some fields are invalid')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Invalid fields',error='Something went wrong')


class OTPView(APIView):
    """
            OTP verification view
             : Post request for otp verification
    """

    def post(self, request):
        """
                 Post request of the API
                    :param request: (request) from the API
                    :return: (response) json response to the API
        """
        try:
            if request.data:
                user_data = OTPModel.objects.get(user = request.data.get('email'))
                if user_data.otp == request.data.get('otp'):
                    user = User.objects.get(email = user_data.user)
                    user.is_active = True
                    user.save()
                    user_data.delete()
                    return StandardResponse(status.HTTP_200_OK, message='Your account is verified, Please Login')
                return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Incorrect otp or something went wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, error="Something went wrong")

class ResetPassword(APIView):
    """
                Reset password view
                 : Post request for reset password
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
             Post request of the API
                  :param request: (request) from the API
                  :return: (response) json response to the API
        """
        try:
            user_instance = request.user
            if user_instance.check_password(request.data.get('old_password')):
                user_instance.set_password(request.data.get('new_password'))
                user_instance.save()
                return StandardResponse(status.HTTP_200_OK, message='Password is changed')
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Old password is not matched')

        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong')

class ResendOTP(APIView):
    """
                OTP Resend view
                 : Post request for get otp on email
    """
    @staticmethod
    def exist_in_otp(email):
        try:
            otp_data = OTPModel.objects.get(user = email)
            return otp_data
        except:
            return None
    def post(self, request):
        try:
            otp = generate_otp()
            user = User.objects.get(email = request.data.get('email'))
            # send opt
            msg = CreateUser.send_email(user.email, user.first_name, otp)
            if msg:
                # check email exist in otp table
                otp_data = self.exist_in_otp(request.data.get('email'))
                if otp_data:
                    # change the otp
                    otp_data.otp = otp
                    otp_data.save()
                else:
                    # create new otp record
                    otp_data = OTPModel(user = user, otp = otp)
                    otp_data.save()
                return StandardResponse(status.HTTP_200_OK, message='OTP is send to email please verify')
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Something is went wrong')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='User not found or something went wrong', error=str(e))


class ForgetPassword(APIView):
    """
                Forget Password view
                 : Post request for change password based on otp
    """
    def post(self, request):
        try:
            if request.data:
                opt_data = ResendOTP.exist_in_otp(request.data.get('email'))
                if opt_data:
                    # print(opt_data.otp ,request.data.get('otp'))
                    if opt_data.otp == request.data.get('otp'):
                        user = User.objects.get(email = opt_data.user)
                        user.set_password(request.data.get('password'))
                        user.save()
                        opt_data.delete()
                        return StandardResponse(status.HTTP_200_OK, message='Password is changed. Please login again')
                    return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Provided OTP is incorrect')
            raise Exception('No data is provided')
        except Exception as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, message='Something went wrong', error=str(e))

class UserLogout(TokenBlacklistView):
    """
                Blacklist Token view
                 : Post request for block token
    """
    def post(self, request: Request, *args, **kwargs) -> Response:
        res = super().post(request, *args, **kwargs)
        if res.status_code == 200:
            return StandardResponse(status.HTTP_200_OK, message='User is logout')
        return res



class UserTokenObtainPairView(TokenObtainPairView):
    """
                User login view
                 : Post request for user login and get token
    """
    permission_classes = []
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except exceptions.AuthenticationFailed as e:
            logger.error(str(e))
            return StandardResponse(status.HTTP_401_UNAUTHORIZED,
                                    message='Invalid Email or Password',
                                    error="Credential invalid")

class UserBYID(APIView):
    """
     User view by id:
        : GET request to get the user
        : Patch request to update the user
        : Delete request to delete the user
    """
    permission_classes = [IsAuthenticated]

    def get_user_by_id(self, userid):
        try:
            user = User.objects.get(pk=userid)
            return user
        except Exception as e:
            logger.error(str(e))
            return None
    def remove_password(self, req):
        if isinstance(req.data, QueryDict):
            req.data._mutable = True
        req.data.pop('password')
        return

    def get(self, request, userid):
        user = self.get_user_by_id(userid)
        if user:
            user = UserSerializer(user)
            return StandardResponse(status.HTTP_200_OK, data = user.data)
        else:
            return StandardResponse(status.HTTP_204_NO_CONTENT, message='User is not found')


    def has_permission_for_update(self, request, userid):
        """
        :param request: request of the API URL
        :param userid: (uuid) of the user
        :return: (bool)
        """
        if request.user and (request.user.is_superuser or request.user.is_staff):
            return True
        elif request.user and request.user.id == userid:
            return True
        else:
            return False
    def patch(self, request, userid):
        user = self.get_user_by_id(userid)
        if user  and self.has_permission_for_update(request, userid):
            if request.data == {}:
                return StandardResponse(status.HTTP_400_BAD_REQUEST, message="Provide some data")
            # if they want to change password remove this
            if request.data.get('password'):
                self.remove_password(request)
            user_slzr = UserSerializer(user, data = request.data, partial=True)
            if user_slzr.is_valid():
                user_slzr.save()
                res = user_slzr.data
                return StandardResponse(status.HTTP_205_RESET_CONTENT, data = res)
            return StandardResponse(status.HTTP_400_BAD_REQUEST, message='Invalid fields', error = user_slzr.errors)
        else:
            return StandardResponse(status.HTTP_400_BAD_REQUEST,message =  'user is not found or bad request')

    def delete(self, request , userid):
        user = self.get_user_by_id(userid)
        if user and self.has_permission_for_update(request, userid):
            user.is_active = False
            user.save()
            return StandardResponse(status.HTTP_204_NO_CONTENT, message= "User is deleted")
        else:
            return StandardResponse(status.HTTP_400_BAD_REQUEST,message="User is not found or bad request")
