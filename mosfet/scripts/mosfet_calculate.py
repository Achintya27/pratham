import math
from elitpowertool.models import Order, UnitsModel
from elitpowertool.serializer import OrderSerializer
import re
from utility.unit_chnager import unit_change




class MosfetCalculator:
    def __init__(self, order_id):
        self.order_id = order_id
        self.all_values = None
    def get_unit_by_name(self, name):
        try:
            unit = UnitsModel.objects.get(unit = name)
            return unit.unit_id
        except:
            raise Exception('Unit has some errors')

    def get_order(self):
        try:
            order = Order.objects.get(pk = self.order_id, is_active= True)
            slzr = OrderSerializer(order)
            return slzr.data, order
        except:
            raise Exception('Order is not found')

    def change_to_number(self, string):
        if string:
             temp = re.compile(r"(\d+(?:\.\d+)?)([a-zA-Z/]+)")
             return float(temp.match(string).groups()[0])
        return 0

    def get_all_data(self):
        order, order_model = self.get_order()
        voltage_power = order.get('voltage_power_data', {})
        circuit_param = order.get('circuit_param', {})
        thermal_info = order.get('devices_thermal_info_data', {})
        mosfet_raw = order.get('mosfet_raw_data', {})
        self.all_values = {
            #buck
            'Vin': voltage_power.get('input_voltage', 0) ,
            'Vout': voltage_power.get('output_voltage_current', 0),
            'Po': voltage_power.get('output_power', 0) * unit_change(voltage_power.get('output_power_unit_data', {}).get('unit', 'W')),
            'L': circuit_param.get('output_inductor', 0) * unit_change(circuit_param.get('inductor_unit_data', {}).get('unit', 'mH')),
            'C': circuit_param.get('output_capacitor', 0) * unit_change(circuit_param.get('capacitor_unit_data', {}).get('unit', 'mF')),

            #acdc
            'I': voltage_power.get('output_voltage_current', 0),
            'Vdc': voltage_power.get('input_voltage', 0),
            # common voltage power
            'fsw': voltage_power.get('switching_freq', 0) * unit_change(voltage_power.get('switching_unit_data', {}).get('unit', 'hz')),
            'VG': voltage_power.get('gate_voltage', 0),
            # Device thermal info
            'n': thermal_info.get('number_of_parallel_devices', 0),
            'Rgon': thermal_info.get('rgon', 0) * unit_change(thermal_info.get('resistance_unit_data', {}).get('unit', 'ohm')),
            'Rgoff': thermal_info.get('rgoff', 0) * unit_change(thermal_info.get('resistance_unit_data', {}).get('unit', 'ohm')),
            'Ti': self.change_to_number(thermal_info.get('heat_sink_temp', {}).get('ambient_temperature', 0)),
            'Rthpaste': thermal_info.get('thermal_resistance', 0),
            # From raw mosfet data
            'Crss': mosfet_raw.get('reverse_trans_cap', 0) * unit_change(order.get('mosfet_raw_data', {}).get('reverse_trans_cap_unit_data', {}).get('unit', '')),
            'Ciss': mosfet_raw.get('input_capacitance', 0) * unit_change(order.get('mosfet_raw_data', {}).get('input_capacitance_unit_data', {}).get('unit', '')),
            'Qgd': mosfet_raw.get('gate_drain_charge', 0) * unit_change(mosfet_raw.get('gate_drain_charge_unit_data', {}).get('unit', '')),
            'Vth': mosfet_raw.get('gate_threshold_voltage', 0),
            'Vgp': mosfet_raw.get('gate_plateau_voltage', 0),
            'Rthjc': mosfet_raw.get('thermal_resistance_junction', 0),
            'Rgi': mosfet_raw.get('internal_gate_resistance', 0),
            # coefficient values
            'a':  mosfet_raw.get('coordinates_data', {}).get('actual_coordinates', {}).get('coefficients', {}).get('a', 0),
            'b': mosfet_raw.get('coordinates_data', {}).get('actual_coordinates', {}).get('coefficients', {}).get('b', 0),
            'c': mosfet_raw.get('coordinates_data', {}).get('actual_coordinates', {}).get('coefficients', {}).get('c', 0)
                    }
        # print(self.all_values)
        return order_model, self.all_values

    def calulate_for_buck(self):
        Io = self.all_values['Po'] / self.all_values['Vout']  # Output current
        Ro = self.all_values['Vout'] / Io
        D = self.all_values['Vout'] / self.all_values['Vin']
        Irip = self.all_values['Vin'] * (1 - D) * D / (self.all_values['fsw'] * self.all_values['L'])
        Il_max = Io + (Irip * 0.5)
        Il_min = Io - (Irip * 0.5)
        Isw_rms = (math.sqrt(((Il_min ** 2) + ((Irip ** 2) / 3) + Irip * Il_min) * D)) / self.all_values['n']
        Iavg = D * Io / self.all_values['n']
        Rth = self.all_values['Rthpaste'] + self.all_values['Rthjc']
        tir = self.all_values['Rgon'] * self.all_values['Ciss'] * (math.log((self.all_values['VG'] - self.all_values['Vth']) / (self.all_values['VG'] - self.all_values['Vgp'])))
        tvf = self.all_values['Rgon'] * self.all_values['Qgd'] / (self.all_values['VG'] - self.all_values['Vgp'])
        tif = self.all_values['Rgoff'] * self.all_values['Ciss'] * (math.log((self.all_values['Vgp']) / (self.all_values['Vth'])))
        tvr = self.all_values['Rgoff'] * self.all_values['Qgd'] / self.all_values['Vgp']
        Psw_on = self.all_values['Vin'] * Iavg * self.all_values['fsw'] * (tir + tvf)
        Psw_off = self.all_values['Vin'] * Iavg * self.all_values['fsw'] * (tif + tvr)
        Psw = (Psw_on + Psw_off)
        Tf_guess = self.all_values['Ti'] + 10  # You can adjust the initial guess as needed
        max_iterations = 100
        tolerance = 1e-3
        Ri = self.all_values['a'] * self.all_values['Ti'] ** 2 + self.all_values['b'] * self.all_values['Ti'] + self.all_values['c']
        # print(Ri)
        i = 0
        for _ in range(max_iterations):
            i = i + 1
            # Calculate delta T (final temperature - initial temperature)
            delta_T = Tf_guess - self.all_values['Ti']
            # Calculate initial resistance

            # Calculatce final resistance
            Rf = self.all_values['a'] * Tf_guess ** 2 + self.all_values['b'] * Tf_guess + self.all_values['c']
            # print(Rf*1000,math.floor(Tf_guess))
            # Calculate conduction  power loss per mosfet
            P_cond = Isw_rms ** 2 * Rf
            # print(P_loss)

            # P_loss= (Psw_on + Psw_off + P_cond)
            P_loss = (P_cond + Psw) * self.all_values['n']
            # Calculate final temperature using thermal resistance formula
            delta_T_final = (P_loss) / (self.all_values['n']) * Rth
            Tf_new = self.all_values['Ti'] + delta_T_final

            # Check for convergence
            if abs(Tf_new - Tf_guess) < tolerance:
                break

            Tf_guess = Tf_new
            # print('iterationss', i)

        power_unit_id = self.get_unit_by_name('W')
        req_data = {'power_loss': P_loss,
                    'power_loss_unit': power_unit_id,
                    'swon_power_loss': Psw_on,
                    'swon_power_loss_unit': power_unit_id,
                    'swoff_power_loss': Psw_off,
                    'swoff_power_loss_unit': power_unit_id,
                    'cond_power_loss': P_cond,
                    'cond_power_loss_unit': power_unit_id,
                    'final_temp': Tf_new,
                    'final_temp_unit': self.get_unit_by_name('Deg C'),
                    'final_resistance': Rf,
                    'final_resistance_unit': self.get_unit_by_name('Ohm'),

                    }
        return req_data



    def calculate(self):
        Rth = self.all_values['Rthpaste'] + self.all_values['Rthjc']
        tir = self.all_values['Rgon'] * self.all_values['Ciss'] * (math.log((self.all_values['VG'] - self.all_values['Vth']) / (self.all_values['VG'] - self.all_values['Vgp'])))
        tvf = self.all_values['Rgon'] * self.all_values['Qgd'] / (self.all_values['VG'] - self.all_values['Vgp'])
        tif = self.all_values['Rgoff'] * self.all_values['Ciss'] * (math.log((self.all_values['Vgp']) / (self.all_values['Vth'])))
        tvr = self.all_values['Rgoff'] * self.all_values['Qgd'] / self.all_values['Vgp']
        Iavg = (1 / math.pi) * (self.all_values['I'] * math.sqrt(2) / self.all_values['n'])
        Irms = self.all_values['I'] / (math.sqrt(2) * self.all_values['n'])
        Psw_on = self.all_values['I'] * 1.414 * self.all_values['Vdc'] * self.all_values['fsw'] * (tir + tvf) * 0.5 / (3.141)
        Psw_off = self.all_values['I'] * 1.414 * self.all_values['Vdc'] * self.all_values['fsw'] * (tif + tvr) * 0.5 / (3.141)
        Psw = Psw_on + Psw_off
        Tf_guess = self.all_values['Ti'] + 10  # You can adjust the initial guess as needed
        max_iterations = 100
        tolerance = 1e-3
        Ri = self.all_values['a'] * self.all_values['Ti'] ** 2 + self.all_values['b'] * self.all_values['Ti'] + self.all_values['c']
        i = 0
        for _ in range(max_iterations):
            i = i + 1
            # Calculate delta T (final temperature - initial temperature)
            delta_T = Tf_guess - self.all_values['Ti']
            # Calculate initial resistance

            # Calculatce final resistance
            Rf = self.all_values['a'] * Tf_guess ** 2 + self.all_values['b'] * Tf_guess + self.all_values['c']
            # print(Rf*1000,math.floor(Tf_guess))
            # Calculate conduction  power loss per mosfet
            P_cond = Irms ** 2 * Rf
            # print(P_loss)

            # P_loss= (Psw_on + Psw_off + P_cond)
            P_loss = (P_cond + Psw) * 6 * self.all_values['n']
            # Calculate final temperature using thermal resistance formula
            delta_T_final = (P_loss) / (6 * self.all_values['n']) * Rth
            Tf_new = self.all_values['Ti'] + delta_T_final

            # Check for convergence
            if abs(Tf_new - Tf_guess) < tolerance:
                break

            Tf_guess = Tf_new


        # Making response for saving the mosfet data into the table
        power_unit_id = self.get_unit_by_name('w')
        req_data = {'power_loss':P_loss,
                    'power_loss_unit': power_unit_id,
                   'swon_power_loss': Psw_on,
                   'swon_power_loss_unit': power_unit_id,
                   'swoff_power_loss':Psw_off,
                   'swoff_power_loss_unit': power_unit_id,
                   'cond_power_loss': P_cond,
                   'cond_power_loss_unit': power_unit_id,
                   'final_temp': Tf_new,
                   'final_temp_unit': self.get_unit_by_name('Deg C'),
                   'final_resistance': Rf,
                   'final_resistance_unit': self.get_unit_by_name('Ohm'),

                  }

        return req_data
    def get_final_mosfet_data(self):
        order_model, val = self.get_all_data()
        print(self.all_values)
        try:
            if order_model.category.name == 'buck':
                return order_model, self.calulate_for_buck()
            return order_model, self.calculate()
        except:
            return (None, None)



