from django.urls import path
from mosfet.views import TakeCoordinates, UploadMosfetPDF, MosfetCalculateAPI, TakeCoordinateBYId, MosfetCalculateBYId

app_name = 'mosfet'

urlpatterns = [
    path('upload/', UploadMosfetPDF.as_view()),
    path('coordinates/', TakeCoordinates.as_view()),
    path('coordinates/<uuid:mosfet_raw_id>', TakeCoordinateBYId.as_view()),
    path('calculate/<uuid:order_id>', MosfetCalculateAPI.as_view()),
    path('<uuid:mosfet_calc_id>', MosfetCalculateBYId.as_view())
]