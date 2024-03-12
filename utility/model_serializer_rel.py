from collections import OrderedDict
from elitpowertool.models import CircuitParamBuck, CircuitParamBoost, CircuitParamFlybackForword, CircuitParamActiveFlybackForword,CircuitParamACDC, CircuitParamCukSepic,CircuitParamHalfFullPush,UnitsModel, VoltagePower, DeviceThermalInfo
from elitpowertool.serializer import  CPBuckSerializer, CPBoostSerializer, CPACDCSerializer,CPFlybackForwordSerializer, CPActiveFlybackForwordSerializer, CPCukSepicSerializer, CPHalfFullPushSerializer,VoltagePowerSerializer, UnitSerializer, DeviceThermalInfoSerializer

allSerializerModel = OrderedDict({
        'buck': (CPBuckSerializer, CircuitParamBuck),
        'boost': (CPBoostSerializer, CircuitParamBoost),
        "active flyback": (CPActiveFlybackForwordSerializer, CircuitParamActiveFlybackForword),
        "active forward": (CPActiveFlybackForwordSerializer, CircuitParamActiveFlybackForword),
        "flyback": (CPFlybackForwordSerializer, CircuitParamFlybackForword),
        "forward": (CPFlybackForwordSerializer, CircuitParamFlybackForword),
        'active front end rectifier( 1 phase, 2 level)': (CPACDCSerializer, CircuitParamACDC),
        'active front end rectifier( 3 phase, 2 level)': (CPACDCSerializer, CircuitParamACDC),
        'inverter ( 3 phase, 3 level)': (CPACDCSerializer, CircuitParamACDC),
        'inverter ( 3 phase, 2 level)': (CPACDCSerializer, CircuitParamACDC),
        "cuk": (CPCukSepicSerializer, CircuitParamCukSepic),
        "sepic": (CPCukSepicSerializer, CircuitParamCukSepic),
        "half bridge": (CPHalfFullPushSerializer, CircuitParamHalfFullPush),
        "full bridge": (CPHalfFullPushSerializer, CircuitParamHalfFullPush),
        "push pull": (CPHalfFullPushSerializer, CircuitParamHalfFullPush)
    })
