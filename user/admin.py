from django.contrib import admin
from user.models import User, OTPModel
# Register your models here.

admin.site.register(User)
admin.site.register(OTPModel)

