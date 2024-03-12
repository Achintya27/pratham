from django.db import models
from uuid import uuid4
from elitpowertool.models import CommonInfoBaseModel, model_float_fields_with_minmax, unit_foreinkey
# Create your models here.

class MosfetRawData(CommonInfoBaseModel):
    """
        Mosfet Raw  Model
         : Inherit the common info class model from elitpowertool.models.py
         : customize the table name with meta Class db_table name
    """
    mosfet_raw_id = models.UUIDField(primary_key=True, default= uuid4, editable=False)
    gate_threshold_voltage = model_float_fields_with_minmax(min_val=0, max_val=50)
    gate_threshold_voltage_unit = unit_foreinkey("gate_threshold_unit")
    gate_plateau_voltage = model_float_fields_with_minmax(min_val=0, max_val=50)
    gate_plateau_voltage_unit = unit_foreinkey("gate_plateau_unit")
    gate_resistance = model_float_fields_with_minmax(min_val=0, max_val=100000)
    gate_resistance_unit = unit_foreinkey("gate_resistance_unit")
    input_capacitance = model_float_fields_with_minmax(min_val=0, max_val=100000)
    input_capacitance_unit = unit_foreinkey("input_capacitance_unit")
    gate_drain_charge = model_float_fields_with_minmax(min_val=0, max_val=100000)
    gate_drain_charge_unit = unit_foreinkey("gate_drain_charge_unit")
    diode_forward_voltage = model_float_fields_with_minmax(min_val=0, max_val=100000)
    diode_forward_voltage_unit = unit_foreinkey("diode_forward_voltage_unit")
    reverse_recovery_time = model_float_fields_with_minmax(max_val=100000)
    reverse_recovery_time_unit = unit_foreinkey("reverse_recovery_time_unit")
    thermal_resistance_junction = model_float_fields_with_minmax(min_val=0, max_val=50)
    thermal_resistance_junction_unit = unit_foreinkey("thermal_resistance_junction_unit")
    reverse_recovery_charge = model_float_fields_with_minmax(max_val=100000)
    reverse_recovery_charge_unit = unit_foreinkey('reverse_recovery_charge_unit')
    reverse_trans_cap = model_float_fields_with_minmax(max_val=100000)
    reverse_trans_cap_unit = unit_foreinkey('reverse_trans_cap_unit')
    internal_gate_resistance = model_float_fields_with_minmax(max_val=100000)
    internal_gate_resistance_unit = unit_foreinkey('internal_gate_resistance_unit')
    coordinates_data = models.TextField(max_length=1024)
    pdfimage_url = models.CharField(max_length=255)
    class Meta:
        db_table = 'mosfet_raw'

class MosfetData(CommonInfoBaseModel):
    """
            Mosfet  Model
             : Inherit the common info class model from elitpowertool.models.py
             : customize the table name with meta Class db_table name
    """
    mosfet_id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    power_loss = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    power_loss_unit = unit_foreinkey('power_loss_unit')
    swon_power_loss = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    swon_power_loss_unit = unit_foreinkey('swon_power_loss_unit')
    swoff_power_loss = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    swoff_power_loss_unit = unit_foreinkey('swoff_power_loss_unit')
    cond_power_loss = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    cond_power_loss_unit = unit_foreinkey('cond_power_loss')
    final_temp = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    final_temp_unit = unit_foreinkey('final_temp_unit')
    final_resistance = model_float_fields_with_minmax(min_val=-1e12, max_val=1e12)
    final_resistance_unit = unit_foreinkey('final_resistance_unit')

    class Meta:
        db_table = 'mosfet'






