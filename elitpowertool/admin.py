from django.contrib import admin
from elitpowertool.models import Order , UnitsModel, DevicesCategories, DeviceThermalInfo, VoltagePower, CircuitParamBuck, CircuitParamBoost, CircuitParamFlybackForword, CircuitParamActiveFlybackForword,CircuitParamACDC, CircuitParamCukSepic,CircuitParamHalfFullPush

# Register your models here.
admin.site.register(Order)
admin.site.register(UnitsModel)
admin.site.register(DevicesCategories)
admin.site.register(DeviceThermalInfo)
admin.site.register(CircuitParamBuck)
admin.site.register(CircuitParamBoost)
admin.site.register(CircuitParamFlybackForword)
admin.site.register(CircuitParamActiveFlybackForword)
admin.site.register(CircuitParamACDC)
admin.site.register(CircuitParamCukSepic)
admin.site.register(CircuitParamHalfFullPush)
