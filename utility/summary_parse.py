import re
import pandas as pd

def change_to_number(string):
    """
    Change string values in numbers like 5.6K/W to 5.6
    :param string:
    :return: float
    """
    string = ''.join(string.split())
    if string:
        try:
            temp = re.compile(r"(\d+(?:\.\d+)?)([a-zA-Z/]+)")
            grp = temp.match(string).groups()
            return float(grp[0]), grp[1]
        except:
            return (0, '')
    return (0, '')


class OrderParser:
    def __init__(self, order):
        self.order = order

    def voltage_power_parser(self, voltage_power):
        return [
            {'Name': "Input Voltage",
             'Value': voltage_power.get('input_voltage', None),
             'Unit': voltage_power.get('input_voltage_unit', {}).get('unit', 'V')
             },
            {'Name': "Output Voltage" if (unit := voltage_power.get('output_voltage_current_unit_data', {}).get('unit',
                                                                                                                'V')) == 'V' else "Output Current",
             'Value': voltage_power.get('output_voltage_current', None),
             'Unit': unit
             },
            {'Name': "Output Power",
             'Value': voltage_power.get('output_power', None),
             'Unit': voltage_power.get('output_power_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Switching Frequency",
             'Value': voltage_power.get('switching_freq', None),
             'Unit': voltage_power.get('switching_unit_data', {}).get('unit', 'Khz')
             },
            {'Name': "Gate Voltage",
             'Value': voltage_power.get('gate_voltage', None),
             'Unit': voltage_power.get('gate_voltage_unit_data', {}).get('unit', 'V')
             }
        ]

    def device_parser(self, device_thermal):
        return [

            {'Name': "No. of Parallel Devices",
             'Value': device_thermal.get('number_of_parallel_devices', None),
             'Unit': None
             },
            {'Name': "Turn on gate resistance",
             'Value': device_thermal.get('rgon', None),
             'Unit': device_thermal.get('resistance_unit_data', {}).get('unit', 'Ohm')
             },
            {'Name': "Turn off gate resistance",
             'Value': device_thermal.get('rgoff', None),
             'Unit': device_thermal.get('resistance_unit_data', {}).get('unit', 'Ohm')
             },
            {'Name': "Thermal resistance of TIM",
             'Value': device_thermal.get('thermal_resistance', None),
             'Unit': device_thermal.get('thermal_resistance_unit_data', {}).get('unit', 'Ohm')
             },
            {'Name': "Heat sink Thermal resistance",
             'Value': (_heat_change := change_to_number(
                 device_thermal.get('heat_sink_temp', {}).get('thermal_resitence', '')))[0],
             'Unit': ''.join(_heat_change[1])
             },
            {'Name': "Heat sink Thermal capacitance",
             'Value': (_heat_change := change_to_number(
                 device_thermal.get('heat_sink_temp', {}).get('thermal_capaciter', '')))[0],
             'Unit': ''.join(_heat_change[1])
             },
            {'Name': "Heat sink Ambient Temperature",
             'Value': (_heat_change := change_to_number(
                 device_thermal.get('heat_sink_temp', {}).get('ambient_temperature', '')))[0],
             'Unit': ''.join(_heat_change[1])
             }]

    def mosfet_parser(self, mosfet_data):
        return [
            {'Name': "Power loss",
             'Value': mosfet_data.get('power_loss', None),
             'Unit': mosfet_data.get('power_loss_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Switch on power loss",
             'Value': mosfet_data.get('swon_power_loss', None),
             'Unit': mosfet_data.get('swon_power_loss_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Switch off power loss",
             'Value': mosfet_data.get('swoff_power_loss', None),
             'Unit': mosfet_data.get('swoff_power_loss_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Condition power loss",
             'Value': mosfet_data.get('cond_power_loss', None),
             'Unit': mosfet_data.get('cond_power_loss_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Final Temperature",
             'Value': mosfet_data.get('final_temp', None),
             'Unit': mosfet_data.get('final_temp_unit_data', {}).get('unit', 'W')
             },
            {'Name': "Final Resistance",
             'Value': mosfet_data.get('final_resistance', None),
             'Unit': mosfet_data.get('final_resistance_unit_data', {}).get('unit', 'W')
             }
        ]

    def acdc_parser(self, circuit_param):
        return [
            {'Name': "Grid Inductance",
             'Value': circuit_param.get('grid_inductance', None),
             'Unit': circuit_param.get('grid_inductance_unit_data', {}).get('unit', 'mH')
             },
            {'Name': "Grid Frequency",
             'Value': circuit_param.get('grid_frequency', None),
             'Unit': circuit_param.get('grid_frequency_unit_data', {}).get('unit', 'Hz')
             },
            {'Name': "Dead Time",
             'Value': circuit_param.get('dead_time', None),
             'Unit': circuit_param.get('dead_time_unit_data', {}).get('unit', 'nS')
             },
            {'Name': "Mode",
             'Value': circuit_param.get('mode_data', None).get('unit', 'SPWM'),
             'Unit': None
             },
            {'Name': "Power Factor cos phi",
             'Value': circuit_param.get('power_factor_cospi', None),
             'Unit': None
             },
            {'Name': "Modulation Index m",
             'Value': circuit_param.get('modulation_index', None),
             'Unit': None,
             }
        ]

    def push_pull_half_parser(self, circuit_param):
        return [
            {'Name': "Leakage Inductor",
             'Value': circuit_param.get('leakage_inductor', None),
             'Unit': circuit_param.get('leakage_inductor_unit_data', {}).get('unit', 'mH')
             },
            {'Name': "Turns ratio n:1",
             'Value': circuit_param.get('turns_ratio', None),
             'Unit': None
             },
            {'Name': "Duty",
             'Value': circuit_param.get('duty', None),
             'Unit': None
             }

        ]

    def cuk_sepic_parser(self, circuit_param):
        return [
            {'Name': "Input Inductor",
             'Value': circuit_param.get('input_inductor', None),
             'Unit': circuit_param.get('inductor_unit_data', {}).get('unit', 'mH')
             },
            {'Name': "Output Inductor",
             'Value': circuit_param.get('output_inductor', None),
             'Unit': circuit_param.get('inductor_unit_data', {}).get('unit', 'mH')
             },
            {'Name': "Input Capacitor",
             'Value': circuit_param.get('input_capacitor', None),
             'Unit': circuit_param.get('output_capacitor_unit_dat', {}).get('unit', 'mF')
             },
            {'Name': "Output Capacitor",
             'Value': circuit_param.get('output_capacitor', None),
             'Unit': circuit_param.get('capacitor_unit_data', {}).get('unit', 'mF')
             },
            *self.mode_and_duty(circuit_param)
        ]

    def active_fly_forward(self, circuit_param):
        return [
            *self.flyback_forward_parser(circuit_param),
            {'Name': "Dead Time",
             'Value': circuit_param.get('dead_time', None),
             'Unit': circuit_param.get('dead_time_unit_data', {}).get('unit', 'nS')
             }
        ]

    def flyback_forward_parser(self, circuit_param):
        return [
            {'Name': "Magnetising Inductor",
             'Value': circuit_param.get('magnetising_inductor', None),
             'Unit': circuit_param.get('magnetising_inductor_unit_data', {}).get('unit', 'mH')
             },
            {'Name': "Output Capacitor",
             'Value': circuit_param.get('output_capacitor', None),
             'Unit': circuit_param.get('output_capacitor_unit_data', {}).get('unit', 'mF')
             },
            {'Name': "Turns ratio n:1",
             'Value': circuit_param.get('turns_ratio', None),
             'Unit': None
             },
            *mode_and_duty(circuit_param)

        ]

    def boost_parser(self, circuit_param):
        return [
            {'Name': "Input Inductor",
             'Value': circuit_param.get('input_inductor', None),
             'Unit': circuit_param.get('inductor_unit_data', {}).get('unit', 'mF')
             },
            *self.buck_parser(circuit_param)
        ]

    def buck_parser(self, circuit_param):
        return [
            {'Name': "Output Inductor",
             'Value': circuit_param.get('output_inductor', None),
             'Unit': circuit_param.get('inductor_unit_data', {}).get('unit', 'mH')
             },

            {'Name': "Output Capacitor",
             'Value': circuit_param.get('output_capacitor', None),
             'Unit': circuit_param.get('capacitor_unit_data', {}).get('unit', 'mF')
             },
            *self.mode_and_duty(circuit_param)

        ]

    def mode_and_duty(self, circuit_param):
        return [
            {'Name': "Mode",
             'Value': circuit_param.get('mode_data', {}).get('unit', 'CCM'),
             'Unit': None
             },

            {'Name': "Duty",
             'Value': circuit_param.get('duty', None),
             'Unit': None
             }
        ]

    def get_circuit_parser(self, circuit_name):
        all_parser = {
            'buck': self.buck_parser,
            'boost': self.boost_parser,
            "flyback": self.flyback_forward_parser,
            "forward": self.flyback_forward_parser,
            "active flyback": self.active_fly_forward,
            "active forward": self.active_fly_forward,
            'active front end rectifier( 1 phase, 2 level)': self.acdc_parser,
            'active front end rectifier( 3 phase, 2 level)': self.acdc_parser,
            'inverter ( 3 phase, 3 level)': self.acdc_parser,
            'inverter ( 3 phase, 2 level)': self.acdc_parser,
            "cuk": self.cuk_sepic_parser,
            "sepic": self.cuk_sepic_parser,
            "half bridge": self.push_pull_half_parser,
            "full bridge": self.push_pull_half_parser,
            "push pull": self.push_pull_half_parser
        }
        if isinstance(circuit_name, str):
            circuit_name = circuit_name.lower()
        circuit_name = str(circuit_name).lower()
        return all_parser[circuit_name]

    def parser(self, csv = False):
        device_data = self.device_parser(self.order.get('devices_thermal_info_data', {}))
        voltage_power = self.voltage_power_parser(self.order.get('voltage_power_data', {}))
        if self.order.get('mosfet_data'):
            mosfet_data = self.mosfet_parser(self.order.get('mosfet_data',{}))
        else:
            mosfet_data = {}
        circuit_data = self.get_circuit_parser(self.order.get('device_categories', {}).get('name', ""))(self.order.get('circuit_param', {}))
        df = pd.DataFrame([
                *voltage_power,
                *circuit_data,
                *device_data,
                *mosfet_data
            ])
        df = df.rename(columns={'Name': "Parameters Name"})
        df['Unit'].fillna('', inplace = True)
        df.dropna(axis=0, inplace=True)
        if csv:
            return df
        else:
            df['Val'] = df['Value'].astype(str) + ' ' + df['Unit']
            final = {df['Parameters Name'].iloc[i]: df['Val'].iloc[i] for i in range(len(df['Val']))}
            return final

