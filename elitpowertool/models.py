from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from user.models import User
from utility.field import UnixTimestampField
from utility.malicious_validator import validate_no_malicious_content
from django.core.validators import FileExtensionValidator

# Create your models here.

class CommonInfoBaseModel(models.Model):
    """
      Common information for each of the models
      like:
         Create By: Creating user
         Update By: Updating user
         Is Active: Use for the soft delete
         Create At: Creating Time
         Update At: Updating Time

    """
    created_at = UnixTimestampField(auto_now_add=True, null=True)
    updated_at = UnixTimestampField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(class)s_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(class)s_updated_by")

    class Meta:
        """
        Not create table for this so make abstract
        """
        abstract = True



class DevicesCategories(CommonInfoBaseModel):
    """
    Devices categories Model
     : Inherit the common info class model
     : customize the table name with meta Class db_table name
    """
    device_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    Group_Choice = ((1, 1),
                    (2, 2),
                    (3, 3))
    name = models.CharField(max_length=128, unique=True, validators=[validate_no_malicious_content])
    image_url = models.FileField(max_length=256,upload_to="devicesCategories/",validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg', 'gif', 'tiff', 'tif', 'bmp', 'svg', 'webp', 'ico', 'psd', 'raw','avif'])])
    group_id = models.IntegerField(choices=Group_Choice)

    class Meta:
        db_table = 'device_category'


class UnitsModel(CommonInfoBaseModel):
    """
        Unit  Model
         : Inherit the common info class model
         : customize the table name with meta Class db_table name
    """
    unit_id = models.AutoField(primary_key=True, editable=False)
    unit = models.CharField(max_length=5, unique=True)
    unit_associated = models.CharField(max_length=50)

    class Meta:
        db_table = 'units'

def model_float_fields_with_minmax(min_val = 0.0, max_val = 10000.0):
    """
    Float model field customized with functions
    :param min_val:(float) minimum  values
    :param max_val: (float) maximum values
    :return: models.FloatFiled with validator
    """

    return models.FloatField(validators=[MinValueValidator(min_val) and MaxValueValidator(max_val)])
def unit_foreinkey(related_name):
    """
    Unit foreign key
    :param related_name: (str) name of the relation between them
    :return: (models.foreignkey) for the unit
    """
    return models.ForeignKey(UnitsModel, related_name= related_name,on_delete=models.DO_NOTHING)
class VoltagePower(CommonInfoBaseModel):
    """
         Voltage Power Model
         : Inherit the common info class model
         : customize the table name with meta Class db_table name
    """
    voltage_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    input_voltage = model_float_fields_with_minmax()
    output_voltage_current = model_float_fields_with_minmax()
    output_voltage_current_unit = unit_foreinkey('voltage_current_unit')
    output_power = model_float_fields_with_minmax(max_val=100000.0)
    output_power_unit = unit_foreinkey("power_unit")
    switching_freq = model_float_fields_with_minmax(max_val=100000.0)
    switching_unit = unit_foreinkey("switch_unit")
    gate_voltage = model_float_fields_with_minmax(min_val=0, max_val=50)
    gate_voltage_unit = unit_foreinkey("gate_voltage_unit")
    class Meta:
        db_table = 'voltage_power'

class CircuitParam(CommonInfoBaseModel):
    """
             Circuit Param Base Model
             : Inherit the common info class model
             : Abstract true means we not want to create table
    """
    circuit_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    duty = model_float_fields_with_minmax(max_val=1.0)
    mode = unit_foreinkey('%(class)s_mode')

    class Meta:
        abstract = True

class CircuitParamBuck(CircuitParam):
    """
             Circuit type buck Model
             : Inherit the circuit param class model
             : customize the table name with meta Class db_table name
    """
    output_inductor = model_float_fields_with_minmax(max_val=100000.0)
    inductor_unit = unit_foreinkey('%(class)s_inductor_unit')
    output_capacitor = model_float_fields_with_minmax(max_val=100000.0)
    capacitor_unit = unit_foreinkey('%(class)s_capacitor_unit')
    class Meta:
        db_table = 'cp_buck'

class CircuitParamBoost(CircuitParam):
    """
                 Circuit type boost  Model
                 : Inherit the circuit param class model
                 : customize the table name with meta Class db_table name
    """
    input_inductor = model_float_fields_with_minmax(max_val=100000.0)
    inductor_unit = unit_foreinkey('%(class)s_inductor_unit')
    output_capacitor = model_float_fields_with_minmax(max_val=100000.0)
    capacitor_unit = unit_foreinkey('%(class)s_capacitor_unit')
    class Meta:
        db_table = 'cp_boost'

class CircuitParamFlybackForword(CircuitParam):
    """
                 Circuit type Flyback and forward Model
                 : Inherit the circuit param class model
                 : customize the table name with meta Class db_table name
    """
    magnetising_inductor = model_float_fields_with_minmax(max_val=100000.0)
    magnetising_inductor_unit = unit_foreinkey('%(class)s_inductor_unit')
    output_capacitor = model_float_fields_with_minmax(max_val=100000.0)
    output_capacitor_unit = unit_foreinkey('%(class)s_capacitor_unit')
    turns_ratio = model_float_fields_with_minmax()

    class Meta:
        db_table = 'cp_flybackforward'

class CircuitParamActiveFlybackForword(CircuitParamFlybackForword):
    """
                 Circuit type Active Flyback and Active forward Model
                 : Inherit the circuit param flyback and forward class model
                 : customize the table name with meta Class db_table name
    """
    dead_time = model_float_fields_with_minmax(max_val=100000.0)
    dead_time_unit = unit_foreinkey('%(class)s_time_unit')

    class Meta:
        db_table = 'cp_active_ff'

class CircuitParamCukSepic(CircuitParam):
    """
                 Circuit type Cuk and Sepic  Model
                 : Inherit the circuit param class model
                 : customize the table name with meta Class db_table name
    """
    input_inductor = model_float_fields_with_minmax(max_val=100000.0)
    output_inductor = model_float_fields_with_minmax(max_val=100000.0)
    inductor_unit = unit_foreinkey('%(class)s_inductor_unit')
    input_capacitor = model_float_fields_with_minmax(max_val=100000.0)
    output_capacitor = model_float_fields_with_minmax(max_val=100000.0)
    output_capacitor_unit = unit_foreinkey('%(class)s_capacitor_unit')

    class Meta:
        db_table = 'cp_cuksepic'

class CircuitParamHalfFullPush(CommonInfoBaseModel):
    """
                 Circuit type  half ,full bridge and push-pull Model
                 : Inherit the common base info class model
                 : customize the table name with meta Class db_table name
    """
    circuit_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    leakage_inductor = model_float_fields_with_minmax(max_val=100000.0)
    leakage_inductor_unit = unit_foreinkey('%(class)s_inductor_unit')
    turns_ratio = model_float_fields_with_minmax()
    duty = model_float_fields_with_minmax(max_val=1.0)

    class Meta:
        db_table = 'cp_halffullpush'

class CircuitParamACDC(CommonInfoBaseModel):
    """
                     Circuit type AC/DC or DC/AC Model
                     : Inherit the common base info class model
                     : customize the table name with meta Class db_table name
    """

    circuit_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    grid_inductance = model_float_fields_with_minmax(max_val=100000.0)
    grid_inductance_unit = unit_foreinkey('%(class)s_inductance_unit')
    grid_frequency = model_float_fields_with_minmax(max_val=500)
    gird_frequency_unit = unit_foreinkey('%(class)s_frequency_unit')
    dead_time = model_float_fields_with_minmax(max_val=100000000.0)
    dead_time_unit = unit_foreinkey('%(class)s_time_unit')
    mode = unit_foreinkey('%(class)s_mode_acdc_unit')
    power_factor_cospi = model_float_fields_with_minmax(min_val=-1.0, max_val=1.0)
    modulation_index = model_float_fields_with_minmax(max_val=1.0)

    class Meta:
        db_table = 'cp_acdc'

class DeviceThermalInfo(CommonInfoBaseModel):
    """
        Device and thermal Model
          : Inherit the common base info class model
          : customize the table name with meta Class db_table name
    """

    device_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    number_of_parallel_devices = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    rgon = model_float_fields_with_minmax(max_val=1000.0)
    rgoff = model_float_fields_with_minmax(max_val=1000.0)
    resistance_unit = unit_foreinkey('%(class)s_resistances_unit')
    thermal_resistance = model_float_fields_with_minmax(max_val=100)
    thermal_resistance_unit = unit_foreinkey('%(class)s_thermal_resistance_unit')
    heat_sink_temp = models.TextField(max_length=256)

    class Meta:
        db_table = 'device_thermalinfo'




class Order(CommonInfoBaseModel):
    """
            Order Model
              : Inherit the common base info class model
              : customize the table name with meta Class db_table name
    """

    #Due to the Circular Import Issues
    from mosfet.models import MosfetData, MosfetRawData

    Status_Choices = (('placed', 'placed'),
                      ('save', 'save'),
                      ('shipped', 'shipped'))
    order_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, validators=[validate_no_malicious_content])
    category = models.ForeignKey(DevicesCategories, on_delete=models.DO_NOTHING)
    voltage_power = models.ForeignKey(VoltagePower, on_delete=models.CASCADE)
    device_thermal_info = models.ForeignKey(DeviceThermalInfo, on_delete=models.CASCADE)
    circuit_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    circuit_id = models.UUIDField()
    circuit_param = GenericForeignKey('circuit_type', 'circuit_id',)
    status = models.CharField(max_length=10, choices=Status_Choices)
    mosfet_raw = models.ForeignKey(MosfetRawData, on_delete=models.CASCADE)
    mosfet = models.ForeignKey(MosfetData, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'order'