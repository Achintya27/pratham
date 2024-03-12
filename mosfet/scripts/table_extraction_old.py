import pdfplumber
import pandas as pd
from fuzzywuzzy import fuzz
import os

def get_values_from_record(record):
    record_data = record.copy()
    record_data.fillna('', inplace=True)
    rec = record_data.to_dict()
    new_dict = {
        'value': rec.get('Value', None),
        'unit': rec.get('Unit', None),
        'min': rec.get('Min', None),
        'max': rec.get('Max', None)
    }
    return {k: list(v.values())[0] if v and isinstance(v, dict) else None for k, v in new_dict.items() if
            v and isinstance(v, dict)}


def desire_value_extractor(table):
    all_fields = [
        "Gate Threshold Voltage", "Gate Plateau Voltage", "Input Capacitance", "Gate-Drain Charge",
        "Diode Forward Voltage", "Reverse Recovery Time", "Reverse Recovery Charge",
        "Thermal Resistance Junction to Case", "Gate Resistance", "RMS Output Current Current",
        "No. of parallel Mosfets",
        "Ambient Temperature", "Reverse Transfer Capacitance", "Gate Voltage", "Thermal Resistance Paste",
        "DC Link Voltage",
        "Switching frequency", "Gate Turn on resistance", "Gate Turn off resistance", "Internal Gate resistance"
    ]
    res = {}
    for fld in all_fields:
        res['_'.join(fld.lower().replace('-', ' ').replace(',', '').split()[:3])] = get_values_from_record(
            table[table['Conditions'].str.lower() == fld.lower()])
    #     print(res)
    return res


def get_req_value_from_tables(pdf_path, column_names_list, strings_to_match):
    with pdfplumber.open(pdf_path) as pdf:
        # Extracting tables from all pages
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)
    final_tables = []
    matched_rows = []

    # Now, you can work with the extracted tables
    for idx, table in enumerate(all_tables):
        data = table
        data_frame = pd.DataFrame(data[:], )
        # data_frame.to_csv(f'/mnt/f/mysite/LOCAL_TESTING/Table_Ext/table_{idx+1}.csv',index=False)
        best_match = 0
        best_match_index = 0
        for idx, row in enumerate(data_frame.values):
            match_count = sum([1 for cell in row if cell in column_names_list])
            if match_count > best_match:
                best_match = match_count
                best_match_index = idx
                # break

        # Set the header row and drop rows above it
        if best_match > 3:
            data_frame.columns = data_frame.iloc[best_match_index]

            data_frame_new = data_frame.iloc[best_match_index + 1:]
            data_frame_new = data_frame_new.fillna('')
            data_frame_new['Symbol'] = data_frame_new['Symbol'].replace('\n', '', regex=True)

            # data_frame_new.to_csv(f'table_{idx + 1}.csv', index=False)
            # final_tables.append(data_frame_new)
            column_name_list = data_frame_new.columns

            if "Symbol" in column_name_list:
                column_name = "Symbol"
            if "SYMBOL" in column_name_list:
                column_name = "SYMBOL"

            # print(column_name_list)
            for string in strings_to_match:

                # filtered_rows = data_frame_new[data_frame_new[column_name].str.contains(string)]
                filtered_rows = data_frame_new[
                    data_frame_new[column_name].apply(lambda x: fuzz.token_sort_ratio(string, x) >= 80)]
                #                 print(filtered_rows)

                if not filtered_rows.empty:
                    matched_rows.append(filtered_rows)

            # data_frame_new.to_csv(f'/mnt/f/mysite/LOCAL_TESTING/Table_Ext/table_{idx+1}.csv',index=False)
    try:
        final_result = pd.concat([matched_rows])
        final_result = pd.concat(matched_rows).reset_index(drop=True).fillna('')
        #         final_result.to_csv(f'{output_csv_path}final_value_req_table.csv',index=False)
        return final_result
    except:
        # Define column names and row values
        column_names = ['Conditions', 'Symbol', 'Value', 'Unit', 'Min', 'Typ', 'Max']
        row_values = [
            "Gate Threshold Voltage", "Gate Plateau Voltage", "Input Capacitance", "Gate-Drain Charge",
            "Diode Forward Voltage", "Reverse Recovery Time", "Reverse Recovery Charge",
            "Thermal Resistance Junction to Case", "Gate Resistance", "RMS Output Current Current",
            "No. of parallel Mosfets",
            "Ambient Temperature", "Reverse Transfer Capacitance", "Gate Voltage", "Thermal Resistance Paste",
            "DC Link Voltage",
            "Switching frequency", "Gate Turn on resistance", "Gate Turn off resistance", "Internal Gate resistance"
        ]

        # Create an empty dataframe
        final_result = pd.DataFrame(columns=column_names)

        # Populate the dataframe with row values
        final_result['Conditions'] = row_values

        # Set the values for 'Gate Resistance' row to 0 for columns 'Value', 'Unit', 'Min', 'Typ', 'Max'
        final_result.loc[final_result['Conditions'] == 'Gate Resistance', ['Value', 'Unit', 'Min', 'Typ', 'Max']] = 0
        final_result.loc[final_result['Conditions'] == 'Gate Threshold Voltage', ['Symbol']] = 'VGSth'
        final_result.loc[final_result['Conditions'] == 'Gate Plateau Voltage', ['Symbol']] = 'Vplateau'
        final_result.loc[final_result['Conditions'] == 'Input Capacitance', ['Symbol']] = 'Ciss'
        final_result.loc[final_result['Conditions'] == 'Gate-Drain Charge', ['Symbol']] = 'Qgd'
        final_result.loc[final_result['Conditions'] == 'Diode Forward Voltage', ['Symbol']] = 'Vsd'
        final_result.loc[final_result['Conditions'] == 'Reverse Recovery Time', ['Symbol']] = 'Trr'
        final_result.loc[final_result['Conditions'] == 'Reverse Recovery Charge', ['Symbol']] = 'Qrr'
        final_result.loc[final_result['Conditions'] == 'Thermal Resistance Junction to Case', ['Symbol']] = 'RthJC'
        final_result.loc[final_result['Conditions'] == 'Gate Resistance', ['Symbol']] = 'Rg'
        final_result.loc[final_result['Conditions'] == 'RMS Output Current Current', ['Symbol']] = 'I'
        final_result.loc[final_result['Conditions'] == 'No. of parallel Mosfets', ['Symbol']] = 'n'
        final_result.loc[final_result['Conditions'] == 'Ambient Temperature', ['Symbol']] = 'Ti'
        final_result.loc[final_result['Conditions'] == 'Reverse Transfer Capacitance', ['Symbol']] = 'Crss'
        final_result.loc[final_result['Conditions'] == 'Gate Voltage', ['Symbol']] = 'Vg'
        final_result.loc[final_result['Conditions'] == 'Thermal Resistance Paste', ['Symbol']] = 'Rthpaste'
        final_result.loc[final_result['Conditions'] == 'DC Link Voltage', ['Symbol']] = 'Vdc'
        final_result.loc[final_result['Conditions'] == 'Switching frequency', ['Symbol']] = 'Fsw'
        final_result.loc[final_result['Conditions'] == 'Gate Turn on resistance', ['Symbol']] = 'Rgon'
        final_result.loc[final_result['Conditions'] == 'Gate Turn off resistance', ['Symbol']] = 'Rgoff'
        final_result.loc[final_result['Conditions'] == 'Internal Gate resistance', ['Symbol']] = 'Rgi'

        # Fill empty cells with ''
        final_result = final_result.fillna('')
        #         final_result.to_csv(f'final_value_req_table.csv',index=False)
        return final_result

    # return matched_rows

def table_extractor_main(input_pdf):
    column_names_list = ['Parameter', 'Characteristic', 'Symbol', 'Conditions', 'Values', 'Value', 'Unit', 'Min', 'Typ',
                         'Max']
    strings_to_match = ["RDSON", "RTHJC", "VGSTH", "CISS", "QGD", "VPLATAEU", "VSD", "TRR", "QRR"]
    matched_rows = get_req_value_from_tables(input_pdf,  column_names_list, strings_to_match)
    #     print(matched_rows)
    print(f'Table Data is extracted {os.path.split(input_pdf)[-1]} Successfully')
    return desire_value_extractor(matched_rows)

