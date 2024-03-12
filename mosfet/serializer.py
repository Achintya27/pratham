import os.path
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from utility.keyword_args import keyword_args
from uuid import uuid4
import json
from mosfet.models import MosfetRawData, MosfetData
from elitpowertool.serializer import UnitSerializer
from utility.file_move import file_move_with_url

class PDFSerializer(serializers.Serializer):
    """
        PDF  Serializer for pdf upload
        We modify the save method to save pdf in particular file

    """
    pdf = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def save(self):
        pdf = self.validated_data['pdf']
        base_file_path = os.path.join('media', 'pdfs')
        file_name = str(uuid4())
        # path to save file
        file_path = os.path.join(base_file_path, file_name)
        # if path not exist create
        if not os.path.exists(base_file_path):
            os.makedirs(base_file_path)
        # save file at destinations
        with open(file_path, 'wb') as destination:
            for chunk in pdf.chunks():
                destination.write(chunk)

        return (file_name, file_path,base_file_path)


class CoordinatesTableSerializer(serializers.ModelSerializer):
    """
        Mosfet raw data Serializer
        We modify the create method and update method  to change the coordinate json data to string
        We modify the to_represent method  to change the coordinate string data to json
        Add some more fields as giving the actual unit instead of the unit id
        & hide the unit_ids variable
        & Used extra keyword args to hide the other details
    """
    gate_threshold_voltage_unit_data = UnitSerializer(source='gate_threshold_voltage_unit', read_only=True)
    gate_plateau_voltage_unit_data = UnitSerializer(source='gate_plateau_voltage_unit', read_only=True)
    gate_resistance_unit_data = UnitSerializer(source='gate_resistance_unit', read_only=True)
    input_capacitance_unit_data = UnitSerializer(source='input_capacitance_unit', read_only=True)
    gate_drain_charge_unit_data = UnitSerializer(source='gate_drain_charge_unit', read_only=True)
    diode_forward_voltage_unit_data = UnitSerializer(source='diode_forward_voltage_unit', read_only=True)
    reverse_recovery_time_unit_data = UnitSerializer(source='reverse_recovery_time_unit', read_only=True)
    thermal_resistance_junction_unit_data = UnitSerializer(source='thermal_resistance_junction_unit', read_only=True)
    reverse_recovery_charge_unit_data = UnitSerializer(source='reverse_recovery_charge_unit', read_only=True)
    reverse_trans_cap_unit_data = UnitSerializer(source='reverse_trans_cap_unit', read_only=True)
    internal_gate_resistance_unit_data = UnitSerializer(source='internal_gate_resistance_unit', read_only=True)

    coordinates_data = serializers.DictField()
    class Meta:
        model = MosfetRawData
        fields = '__all__'
        extra_kwargs = keyword_args['mosfet_raw_data']
    def move_file_and_delete(self,image_url):
        """
        :param image_url:(str) image url we have to save
        :return: (str) new path
        """
        if not image_url:
            return None
        new_path = file_move_with_url(image_url)
        request = self.context.get('request')
        if new_path:
            return request.build_absolute_uri('/').split('?')[0] + '/'.join(new_path)

        raise Exception('pdfImage url is not correct')

    def to_representation(self, instance):
        # change coordinate string data to json
        coordinates_data = instance.coordinates_data
        instance.coordinates_data = json.loads(coordinates_data)
        return super().to_representation(instance)

    def create(self, validated_data):
        coordinates_data = validated_data.get('coordinates_data', None)
        pdfimage_url = self.move_file_and_delete(validated_data.get('pdfimage_url', None))
        if coordinates_data and pdfimage_url:
            # change from json to sting
            validated_data.update({'coordinates_data': json.dumps(coordinates_data),
                                   'pdfimage_url': pdfimage_url})
            return super().create(validated_data)

        raise Exception('Some data is missing')

    def update(self, instance, validated_data):
        coordinates_data = validated_data.get('coordinates_data', None)
        pdfimage_url = self.move_file_and_delete(validated_data.get('pdfimage_url', None))
        if coordinates_data:
            # change from json to string
            validated_data.update({'coordinates_data': json.dumps(coordinates_data)})
            if pdfimage_url:
                validated_data.update({'pdfimage_url': pdfimage_url})
            return super().update(instance, validated_data)

        raise Exception('Some data is missing')



class MosfetSerializer(serializers.ModelSerializer):
    """
            Mosfet data Serializer
            Add some more fields as giving the actual unit instead of the unit id
            & hide the unit_ids variable
            & Used extra keyword args to hide the other details
    """

    power_loss_unit_data = UnitSerializer(source='power_loss_unit', read_only=True)
    swon_power_loss_unit_data = UnitSerializer(source='swon_power_loss_unit', read_only=True)
    swoff_power_loss_unit_data = UnitSerializer(source='swoff_power_loss_unit', read_only=True)
    final_resistance_unit_data = UnitSerializer(source='final_resistance_unit', read_only=True)
    cond_power_loss_unit_data = UnitSerializer(source='cond_power_loss_unit', read_only=True)
    final_temp_unit_data = UnitSerializer(source='final_temp_unit', read_only=True)

    class Meta:
        model = MosfetData
        fields = '__all__'
        extra_kwargs = keyword_args['mosfet_data']
