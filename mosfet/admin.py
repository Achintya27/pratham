from django.contrib import admin
from mosfet.models import MosfetRawData, MosfetData
# Register your models here.
admin.site.register(MosfetData)
admin.site.register(MosfetRawData)
