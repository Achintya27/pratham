import json
from rest_framework import serializers
from elitpowertool.models import DevicesCategories, CircuitParamBoost, CircuitParamBuck, CircuitParamFlybackForword,CircuitParamActiveFlybackForword,CircuitParamCukSepic,CircuitParamACDC,CircuitParamHalfFullPush, Order, VoltagePower, UnitsModel,DeviceThermalInfo
from utility.keyword_args import keyword_args

class DevicesCategoriesSerializer(serializers.ModelSerializer):
    """
    Device Categories Serializer
    We modify the create method
    & Used extra keyword args to hide the other details
    """
    class Meta:
        model = DevicesCategories
        fields = "__all__"
        # hide some data at the time of represent
        extra_kwargs = keyword_args['device_categories']

    def create(self, validated_data):
        device_cat = super().create(validated_data)
        device_cat.is_active = True
        device_cat.save()
        return device_cat



class UnitSerializer(serializers.ModelSerializer):
    """
        Unit Serializer Serializer
        & Used extra keyword args to hide the other details
    """
    class Meta:
        model = UnitsModel
        fields = '__all__'
        extra_kwargs = keyword_args['units']

class CPBoostSerializer(serializers.ModelSerializer):
    """
        Circuit type boost Serializer
        Add some more fields as giving the actual unit instead of the unit id
        & hide the unit_ids variable
        & Used extra keyword args to hide the other details
    """
    mode_data = UnitSerializer(source="mode", read_only=True)
    inductor_unit_data = UnitSerializer(source="inductor_unit", read_only=True)
    capacitor_unit_data = UnitSerializer(source="capacitor_unit", read_only=True)
    class Meta:
        model = CircuitParamBoost
        fields = '__all__'
        extra_kwargs = keyword_args['buck_boost']

class CPBuckSerializer(serializers.ModelSerializer):
    """
            Circuit type Buck Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
        """

    mode_data = UnitSerializer(source="mode", read_only=True)
    inductor_unit_data = UnitSerializer(source="inductor_unit", read_only=True)
    capacitor_unit_data = UnitSerializer(source="capacitor_unit", read_only=True)
    class Meta:
        model = CircuitParamBuck
        fields = '__all__'
        extra_kwargs = keyword_args['buck_boost']

class CPFlybackForwordSerializer(serializers.ModelSerializer):
    """
            Circuit type flyback and forward Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    mode_data = UnitSerializer(source="mode", read_only=True)
    output_capacitor_unit_data = UnitSerializer(source="output_capacitor_unit", read_only=True)
    magnetising_inductor_unit_data = UnitSerializer(source="magnetising_inductor_unit", read_only=True)
    class Meta:
        model = CircuitParamFlybackForword
        fields = "__all__"
        extra_kwargs = keyword_args['flyback_forword']


class CPActiveFlybackForwordSerializer(serializers.ModelSerializer):
    """
            Circuit type Active flyback and Active Forward Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    mode_data = UnitSerializer(source="mode", read_only=True)
    output_capacitor_unit_data = UnitSerializer(source="output_capacitor_unit", read_only=True)
    magnetising_inductor_unit_data = UnitSerializer(source="magnetising_inductor_unit", read_only=True)
    dead_time_unit_data = UnitSerializer(source="dead_time_unit", read_only=True)

    class Meta:
        model = CircuitParamActiveFlybackForword
        fields = '__all__'
        extra_kwargs = keyword_args['active_flyback_forword']


class CPCukSepicSerializer(serializers.ModelSerializer):
    """
            Circuit type Cuc and sepic Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    mode_data = UnitSerializer(source="mode", read_only=True)
    output_capacitor_unit_data = UnitSerializer(source="output_capacitor_unit", read_only=True)
    inductor_unit_data = UnitSerializer(source="inductor_unit", read_only=True)

    class Meta:
        model = CircuitParamCukSepic
        fields = '__all__'
        extra_kwargs = keyword_args['cuk_sephic']


class CPACDCSerializer(serializers.ModelSerializer):
    """
            Circuit type AC/DC or DC/AC Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    dead_time_unit_data = UnitSerializer(source="dead_time_unit", read_only=True)
    gird_frequency_unit_data = UnitSerializer(source="gird_frequency_unit", read_only=True)
    grid_inductance_unit_data = UnitSerializer(source="grid_inductance_unit", read_only=True)
    mode_data = UnitSerializer(source="mode", read_only=True)
    class Meta:
        model = CircuitParamACDC
        fields = '__all__'
        extra_kwargs = keyword_args['ac_dc']


class CPHalfFullPushSerializer(serializers.ModelSerializer):
    """
            Circuit type half and full bridge & push pull Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    leakage_inductor_unit_data = UnitSerializer(source="leakage_inductor_unit", read_only=True)
    class Meta:
        model = CircuitParamHalfFullPush
        fields = '__all__'
        extra_kwargs = keyword_args['half_full_push']


class VoltagePowerSerializer(serializers.ModelSerializer):
    """
            Voltage and Power Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    switching_unit_data = UnitSerializer(source= "switching_unit",read_only=True)
    output_power_unit_data = UnitSerializer(source="output_power_unit", read_only=True)
    output_voltage_current_unit_data = UnitSerializer(source="output_voltage_current_unit",read_only=True)
    gate_voltage_unit_data = UnitSerializer(source="gate_voltage_unit",read_only=True)
    class Meta:
        model = VoltagePower
        fields = '__all__'
        extra_kwargs = keyword_args['voltage_power']


class DeviceThermalInfoSerializer(serializers.ModelSerializer):
    """
            Device & thermal data  Serializer
            Modify the create & update method: To change the heat sink  json data into string
            Modify the to_represent method to change heat sink string data to json
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """
    thermal_resistance_unit_data = UnitSerializer(source="thermal_resistance_unit", read_only=True)
    resistance_unit_data = UnitSerializer(source='resistance_unit', read_only=True)
    heat_sink_temp = serializers.DictField()
    class Meta:
        model = DeviceThermalInfo
        fields = '__all__'
        extra_kwargs = keyword_args['thermal_info']

    def to_representation(self, instance):
        """
        Modify the to_represent method to change heat sink string data to json
        return actual json data to send in response
        """
        heat_sink_data = instance.heat_sink_temp
        instance.heat_sink_temp = json.loads(heat_sink_data)
        return super().to_representation(instance)

    def create(self, validated_data):
        """
        Modify the create method: To change the heat sink  json data into string
        """
        heat_sink_data = validated_data.get('heat_sink_temp', None)
        if heat_sink_data:
            validated_data.update({'heat_sink_temp': json.dumps(heat_sink_data)})
            return super().create(validated_data)

    def update(self, instance, validated_data):
        """
                Modify the create & update method: To change the heat sink  json data into string
        """
        heat_sink_data = validated_data.get('heat_sink_temp', instance.heat_sink_temp)
        if heat_sink_data:
            validated_data.update({'heat_sink_temp': json.dumps(heat_sink_data)})
            return super().update(instance, validated_data)


class CircuitParamRelatedField(serializers.RelatedField):
    """
            Circuit Parameter related fields
            it is check in all which type of the model & map to same serializer
            & return json
    """
    # due to the circular import
    from utility.model_serializer_rel import allSerializerModel
    all_circuit_types = allSerializerModel
    def to_representation(self, value):
        # Circuit type Instance check and map to same serializer
        for circuit_name, circuit in self.all_circuit_types.items():
            if isinstance(value, circuit[1]):
                slzr = circuit[0](value)
                data = {'circuit_type': circuit_name}
                data.update(slzr.data)
                return data

        raise Exception("Unexpected type of tagged objects")





class OrderSerializer(serializers.ModelSerializer):
    """
            Order  Serializer
            Modify the update method we need to update only name and categories not others
            Add some more fields as giving the actual data of the foreign key  instead of the id
            & hide the foreign key ids in json
            & Used extra keyword args to hide the other details
    """
    # for circular import prevent
    from mosfet.serializer import CoordinatesTableSerializer, MosfetSerializer

    circuit_param = CircuitParamRelatedField(read_only=True)
    voltage_power_data = VoltagePowerSerializer(source='voltage_power', read_only=True)
    devices_thermal_info_data = DeviceThermalInfoSerializer(source='device_thermal_info', read_only=True)
    mosfet_raw_data = CoordinatesTableSerializer(source='mosfet_raw', read_only=True)
    device_categories = DevicesCategoriesSerializer(source='category', read_only=True)
    mosfet_data = MosfetSerializer(source='mosfet', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = keyword_args['order']


    def update(self, instance, validated_data):
        """
        Param: instance (Model)
        Param: validated data (from validator after request data)
        Modify the update method we need to update only name and categories not others
        """
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance


class DevicesCategoriesForList(serializers.ModelSerializer):
    """
        Device Categories list Serializer
        & Used extra keyword args to hide the other details
    """
    class Meta:
        model = DevicesCategories
        fields = ['name']

class OrderListSerializer(serializers.ModelSerializer):
    """
            Order list Serializer
            Device Categories list Serializer added to get only name not all data
            & Allowed only required fields in json
    """
    device_categories = DevicesCategoriesForList(source='category', read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'device_categories', 'name', 'created_at', 'updated_at', 'created_by', 'updated_by']