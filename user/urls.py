from django.urls import path, include
from user.views import CreateUser, UserTokenObtainPairView, UserBYID, OTPView, ResetPassword, ForgetPassword, ResendOTP, UserLogout
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView
)

app_name = 'user'

urlpatterns = [
    path('create_user/', CreateUser.as_view()),
    path('verify_otp/', OTPView.as_view()),
    path('reset_password/', ResetPassword.as_view()),
    path('forget_password/', ForgetPassword.as_view()),
    path('resend_otp/', ResendOTP.as_view()),
    path('login/', UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', UserLogout.as_view(), name='token_blacklist'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<uuid:userid>', UserBYID.as_view(), name = 'User data')

]