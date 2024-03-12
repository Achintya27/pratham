from django.urls import path

from elitpowertool.views import Summary,DownloadCSV,OrderListview, OrderBYID, CreateOrder, CreateCircuitParam, CircuitParamById,CreateVoltagePower, CreateUnit,UnitViewById, VoltagePowerById, CreateDeviceThermalInfo, DeviceThermalInfoById, CreateDevicesCategories, DeviesCategoriesByID

app_name = 'elitpowertool'
urlpatterns = [
    path('order/create', CreateOrder.as_view()),
    path('order/<uuid:order_id>', OrderBYID.as_view()),
    path('order/', OrderListview.as_view()),
    path('order/download/<uuid:order_id>', DownloadCSV.as_view()),
    path('order/summary/<uuid:order_id>', Summary.as_view()),
    path('categories/', CreateDevicesCategories.as_view()),
    path('categories/<uuid:category_id>', DeviesCategoriesByID.as_view()),
    path('create_circuitparam/', CreateCircuitParam.as_view()),
    path('circuit_param/<uuid:circuit_param_id>', CircuitParamById.as_view()),
    path('create_voltagepower/', CreateVoltagePower.as_view()),
    path('voltage_power/<uuid:voltage_power_id>', VoltagePowerById.as_view()),
    path('thermal_info/', CreateDeviceThermalInfo.as_view()),
    path('thermal_info/<uuid:device_thermal_id>', DeviceThermalInfoById.as_view()),
    path('create_unit/', CreateUnit.as_view()),
    path('unit/<int:unit_id>', UnitViewById.as_view())
]