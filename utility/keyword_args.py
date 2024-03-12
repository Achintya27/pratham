write_only = {'write_only': True}
hidden_values = ['created_by', 'updated_by', 'is_active', 'created_at', 'updated_at']
keyword_args = {
    "device_categories": {key: write_only for key in [*hidden_values]},
    "buck_boost" : {key: write_only for key in ['mode','inductor_unit', 'capacitor_unit', *hidden_values]},
    "flyback_forword": {key: write_only for key in ['mode', 'magnetising_inductor_unit', 'output_capacitor_unit', *hidden_values]},
    "active_flyback_forword": {key: write_only for key in ["dead_time_unit", 'mode', 'magnetising_inductor_unit', 'output_capacitor_unit', *hidden_values]},
    "cuk_sephic": {key: write_only for key in ['mode', 'inductor_unit', 'output_capacitor_unit', *hidden_values]},
    "ac_dc": {key: write_only for key in ['mode', 'grid_inductance_unit', 'gird_frequency_unit', 'dead_time_unit', *hidden_values]},
    "half_full_push": {key: write_only for key in ['dead_time_unit', *hidden_values]},
    "voltage_power": {key: write_only for key in ['switching_unit', 'output_power_unit', 'output_voltage_current_unit', 'gate_voltage_unit', *hidden_values]},
    "thermal_info": {key: write_only for key in ["thermal_resistance_unit", "resistance_unit", *hidden_values]},
    "units": {key: write_only for key in ['created_at', 'updated_at', *hidden_values]},
    "order": {key: write_only for key in ['circuit_type', 'circuit_id','voltage_power','category', 'mosfet_raw', 'device_thermal_info', 'mosfet']},
    "mosfet_raw_data": {key: write_only for key in ['internal_gate_resistance_unit','reverse_trans_cap_unit','reverse_recovery_charge_unit','thermal_resistance_junction_unit','reverse_recovery_time_unit','diode_forward_voltage_unit','gate_drain_charge_unit','input_capacitance_unit','gate_resistance_unit','gate_plateau_voltage_unit','gate_threshold_voltage_unit',*hidden_values]},
    "mosfet_data": {key: write_only for key in ['final_temp_unit','cond_power_loss_unit','final_resistance_unit','swoff_power_loss_unit','swon_power_loss_unit','power_loss_unit',*hidden_values]}
}

