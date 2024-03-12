import pdfplumber
import pandas as pd
import numpy as np
import re


def g(df):
    df.columns = [x.upper()[:-1] if x.endswith('s') else x.upper() for x in df.columns]
    return df


def get_req_value_from_tables(pdf_path, output_csv_path, column_names_list, symbols_to_match, minmaxtyp_column):
    symbols_found = []
    parameter_found = []
    value_found = []
    min_found = []
    max_found = []
    typ_found = []
    unit_found = []

    with pdfplumber.open(pdf_path) as pdf:
        # Extracting tables from all pages
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    prev_column = []
    # Now, you can work with the extracted tables
    for idx, table in enumerate(all_tables):
        data = table

        # if idx != 2:
        #     continue

        # print(f"This is DATAFRAME no. :  {idx}")

        data_frame = pd.DataFrame(data[:], )

        # import pdb;pdb.set_trace()

        data_frame_new = pd.DataFrame({'PARAMETER': [],
                                       'SYMBOL': [],
                                       'MIN': [],
                                       'TYP': [],
                                       'MAX': [],
                                       'VALUE': [],
                                       'UNIT': []
                                       })

        best_match = 0
        best_minmaxtyp_match = 0
        # The above code is defining a function called `best_match_index`.
        best_match_index = -1
        best_minmaxtyp_match_index = -1

        for idx, row in enumerate(data_frame.values):
            match_count = sum([1 for cell in row if remove_special_characters(str(cell).lower()) in column_names_list])
            match_minmaxtyp_count = sum(
                [1 for cell in row if remove_special_characters(str(cell).lower()) in minmaxtyp_column])
            # Creating an empty DataFrame
            data_frame_new = pd.DataFrame()

            if match_count > best_match:
                best_match = match_count
                best_match_index = idx

            if match_minmaxtyp_count > best_minmaxtyp_match:
                best_minmaxtyp_match = match_minmaxtyp_count
                best_minmaxtyp_match_index = idx
        # print(
        #     f"best_match : {best_match}  ||  best_match_index: {best_match_index} || best_minmaxtyp_match_index: {best_minmaxtyp_match_index}")

        # import pdb;pdb.set_trace()

        if best_match >= 2 and best_minmaxtyp_match >= 1 and best_match_index != best_minmaxtyp_match_index:

            # print(f"Condition 1")

            prev_column = data_frame.iloc[best_match_index].str.upper().to_list()

            data_frame.columns = data_frame.iloc[best_match_index].str.upper()
            data_frame_new = data_frame.iloc[best_match_index + 1:]
            data_frame_new = data_frame_new.fillna('')

            # import pdb;pdb.set_trace()

            if 'SYMBOL' in data_frame_new.columns:
                symbol_col = 'SYMBOL'
                # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            elif 'PARAMETER' in data_frame_new.columns:
                symbol_col = 'SYMBOL'

            data_frame_new[symbol_col] = data_frame_new[symbol_col].replace('\n', '', regex=True)
            data_frame_new[symbol_col] = data_frame_new[symbol_col].apply(
                lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new = data_frame_new.reset_index(drop=True)
            data_frame_new.replace('\n', '', regex=True, inplace=True)

            # Iterate through rows and update column names
            for idx, row in enumerate(data_frame_new.values):
                for col_idx, cell in enumerate(row):
                    cell_value = remove_special_characters(str(cell).lower())
                    if cell_value in minmaxtyp_column:
                        # Update column name and set cell value to NaN
                        data_frame_new.columns.values[col_idx] = cell_value.upper()
                        data_frame_new.iloc[idx, col_idx] = np.nan

            # data_frame_new = data_frame_new.fillna(np.nan)
            data_frame_new = data_frame_new.dropna(thresh=4)
            data_frame_new = gcolumn_name_fix(data_frame_new.copy())

        elif best_match >= 2 and best_match_index > -1 and best_minmaxtyp_match_index == -1:

            # print(f"Condition 2")

            prev_column = data_frame.iloc[best_match_index].str.upper().to_list()

            data_frame.columns = data_frame.iloc[best_match_index].str.upper()
            data_frame_new = data_frame.iloc[best_match_index + 1:]
            data_frame_new = data_frame_new.fillna('')
            # print(data_frame_new.columns)
            if 'SYMBOL' in data_frame_new.columns:
                symbol_col = 'SYMBOL'
                # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            elif 'PARAMETER' in data_frame_new.columns:
                symbol_col = 'PARAMETER'
                # data_frame_new['Parameter'] = data_frame_new['Parameter'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new[symbol_col] = data_frame_new[symbol_col].replace('\n', '', regex=True)
            data_frame_new[symbol_col] = data_frame_new[symbol_col].apply(
                lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new.columns = [remove_special_characters(col) for col in data_frame_new.columns]
            data_frame_new = data_frame_new.reset_index(drop=True)
            data_frame_new = gcolumn_name_fix(data_frame_new.copy())
            data_frame_new.replace('\n', '', regex=True, inplace=True)


        elif best_match >= 2 and best_match_index > -1 and best_match_index == best_minmaxtyp_match_index:

            # print(f"Condition 3")
            prev_column = data_frame.iloc[best_match_index].str.upper().to_list()

            data_frame.columns = data_frame.iloc[best_match_index].str.upper()
            data_frame_new = data_frame.iloc[best_match_index + 1:]
            data_frame_new = data_frame_new.fillna('')

            if 'SYMBOL' in data_frame_new.columns:
                symbol_col = 'SYMBOL'
                # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            elif 'PARAMETER' in data_frame_new.columns:
                symbol_col = 'PARAMETER'
                # data_frame_new['Parameter'] = data_frame_new['Parameter'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))

            data_frame_new[symbol_col] = data_frame_new[symbol_col].replace('\n', '', regex=True)
            data_frame_new[symbol_col] = data_frame_new[symbol_col].apply(
                lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new.columns = [remove_special_characters(col) for col in data_frame_new.columns]
            data_frame_new = data_frame_new.reset_index(drop=True)
            data_frame_new = gcolumn_name_fix(data_frame_new.copy())

            data_frame_new.replace('\n', '', regex=True, inplace=True)

        elif best_match >= 2:
            # print("Condition 4.")
            data_frame_new = data_frame.iloc[best_match_index + 1:]
            prev_column = data_frame.iloc[best_match_index].str.upper().to_list()
            data_frame_new.replace('', np.nan, inplace=True)  # Convert empty strings to NaN
            data_frame_new = data_frame_new.dropna(thresh=4)
            data_frame_new = data_frame_new.reset_index(drop=True)

            # .str.upper()
            data_frame_new.columns = data_frame_new.columns.str.upper()

            if 'SYMBOL' in data_frame_new.columns:
                symbol_col = 'SYMBOL'
                # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            elif 'PARAMETER' in data_frame_new.columns:
                symbol_col = 'PARAMETER'
                # data_frame_new['Parameter'] = data_frame_new['Parameter'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))

            data_frame_new[symbol_col] = data_frame_new[symbol_col].replace('\n', '', regex=True)
            data_frame_new[symbol_col] = data_frame_new[symbol_col].apply(
                lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new.columns = data_frame_new.columns.fillna('unnamed')
            data_frame_new.columns = [remove_special_characters(col) for col in data_frame_new.columns]
            data_frame_new = gcolumn_name_fix(data_frame_new.copy())
            data_frame_new.replace('\n', '', regex=True, inplace=True)

        elif best_match == 0 and best_match_index > -1 and best_minmaxtyp_match == 0 and best_minmaxtyp_match_index == -1 and len(
                data_frame) > 2:
            # print("Condition 5.")

            # prev_column

            data_frame_new = data_frame.iloc[best_match_index + 1:]
            data_frame_new.columns = prev_column

            data_frame_new.replace('', np.nan, inplace=True)  # Convert empty strings to NaN
            data_frame_new = data_frame_new.dropna(thresh=4)
            data_frame_new = data_frame_new.reset_index(drop=True)

            # .str.upper()
            data_frame_new.columns = data_frame_new.columns.str.upper()

            if 'SYMBOL' in data_frame_new.columns:
                symbol_col = 'SYMBOL'
                # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            elif 'PARAMETER' in data_frame_new.columns:
                symbol_col = 'PARAMETER'
                # data_frame_new['Parameter'] = data_frame_new['Parameter'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))

            data_frame_new[symbol_col] = data_frame_new[symbol_col].replace('\n', '', regex=True)
            data_frame_new[symbol_col] = data_frame_new[symbol_col].apply(
                lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            # data_frame_new['Symbol'] = data_frame_new['Symbol'].apply(lambda x: re.sub(r'[^A-Za-z]+', '', str(x).upper()))
            data_frame_new.columns = data_frame_new.columns.fillna('unnamed')
            data_frame_new.columns = [remove_special_characters(col) for col in data_frame_new.columns]
            data_frame_new = gcolumn_name_fix(data_frame_new.copy())
            data_frame_new.replace('\n', '', regex=True, inplace=True)

        # import pdb;pdb.set_trace()

        if not data_frame_new.empty:

            for idx, symbol_in_df in enumerate(data_frame_new[symbol_col.upper()]):
                # Check if the symbol is present in the CSV DataFrame
                if symbol_in_df in symbols_to_match.keys():

                    if symbol_in_df in symbols_to_match.keys():
                        # Get the corresponding parameter
                        parameter = symbols_to_match[symbol_in_df]

                        # Your existing code to extract values from the CSV DataFrame

                        # Append the matched values to the lists
                        parameter_found.append(parameter)
                        symbols_found.append(symbol_in_df)

                        min_found.append('' if "MIN" not in data_frame_new.columns else data_frame_new['MIN'].iloc[idx])
                        typ_found.append('' if "TYP" not in data_frame_new.columns else data_frame_new['TYP'].iloc[idx])
                        max_found.append('' if "MAX" not in data_frame_new.columns else data_frame_new['MAX'].iloc[idx])
                        value_found.append(
                            '' if "VALUE" not in data_frame_new.columns else data_frame_new['VALUE'].iloc[idx])
                        unit_found.append(
                            '' if "UNIT" not in data_frame_new.columns else data_frame_new['UNIT'].iloc[idx])

        # import pdb;pdb.set_trace()
        # print(f"PARAMETER: {parameter_found}")
        # print(f"SYMBOL: {symbols_found}")
        # print(f"VALUE: {value_found}")
        # print(f"MIN: {min_found}")
        # print(f"MAX: {max_found}")
        # print(f"TYP: {typ_found}")
    # Create a DataFrame with the matched values

    new_df = pd.DataFrame({
        'parameter': parameter_found,
        'Symbol': symbols_found,
        'min': min_found,
        'typ': typ_found,
        'max': max_found,
        'value': value_found,
        'unit': unit_found
    })

    return new_df


def remove_special_characters(s):
    # Remove special characters from the string
    return re.sub(r'[^a-zA-Z]', '', str(s))


def gcolumn_name_fix(df):
    df.columns = [x.upper()[:-1] if x.endswith('s') else x.upper() for x in df.columns]
    return df


def main(input_pdf):
    output_csv_path = 'table_output/'

    symbols_to_match = {"RDSON": "Drain Source On-State Resistance",
                        "RTHJC": "Thermal Resistance Junction to Case",
                        "RTJC": "Thermal Resistance Junction to Case",
                        "RCIDJC": "Thermal Resistance Junction to Case",
                        "VGSTH": "Gate Threshold Voltage",
                        "CISS": "Input Capacitance",
                        "QGD": "Gate-Drain Charge",
                        "VSD": "Diode Forward voltage",
                        "TRR": "Reverse Recovery Time",
                        "QRR": "Reverse Recovery Charge",
                        "VPLATEAU": "Gate Plateau Voltage"}

    strings_to_match = ["RDSON", "RTHJC", "RTJC", "RCIDJC", "VGSTH", "CISS", "QGD", "VPLATEAU", "VSD", "TRR", "QRR"]

    column_names_list = ['parameter', 'characteristic', 'symbol', 'conditions', 'values', 'value', 'unit', ]
    minmaxtyp_column = ['min', 'typ', 'max', 'minimum', 'maximum', 'type']

    matched_rows = get_req_value_from_tables(input_pdf, output_csv_path, column_names_list, symbols_to_match,
                                             minmaxtyp_column)

    df = matched_rows

    return matched_rows



def value_parser(rec):
    value = rec.get('typ', None)
    if not value and rec.get('min', None):
        value = rec.get('min')
    if not value and rec.get('max', None):
        value = rec.get('max', None)
    if value and isinstance(value, dict):
        values = list(value.values())[0]
        if values and isinstance(values, str):
            values_list = values.split(' ')[0].split('.')
            other = ''.join(values_list[1:]).strip()
            return float('.'.join([values_list[0], other]))
        else:
            return 0.0
    return value
def get_values_from_record(record):
    record_data = record.copy()
    record_data.fillna('', inplace=True)
    rec = record_data.to_dict()
    value_parser(rec)
    new_dict = {
        'value': value_parser(rec) if value_parser(rec) != {} else 0 ,
        'unit': list(rec.get('unit', {}).values())[0] if list(rec.get('unit', {}).values()) !=[] else ''
    }
    # print(new_dict)
    return {k:v for k,v in new_dict.items()}


def desire_value_extractor(table):
    all_fields = ['Thermal Resistance Junction to Case',
                   'Gate Resistance',
                    'reverse transfer capacitance',
                     'Gate Threshold Voltage',
                     'Drain Source On-State Resistance',
                     'Input Capacitance',
                     'Gate-Drain Charge',
                     'Gate Plateau Voltage',
                     'Diode Forward voltage',
                     'Reverse Recovery Time',
                     'Reverse Recovery Charge']
    res = {}
    for fld in all_fields:
        # print(fld)
        res['_'.join(fld.lower().replace('-', ' ').replace(',','').split()[:3])] = get_values_from_record(table[table['parameter'].str.lower() == fld.lower()])
    # print(res)
    val = res.pop('drain_source_on')
    res['drain_source_on-state-resistance'] = val
    return res
def get_data_for_empty():
    df = pd.DataFrame(
        { 'parameter': pd.Series(['Thermal Resistance Junction to Case',
                   'Gate Resistance',
                    'reverse transfer capacitance',
                     'Gate Threshold Voltage',
                     'Drain Source On-State Resistance',
                     'Input Capacitance',
                     'Gate-Drain Charge',
                     'Gate Plateau Voltage',
                     'Diode Forward voltage',
                     'Reverse Recovery Time',
                     'Reverse Recovery Charge']),
          'typ': pd.Series(np.zeros(11)),
          'min': pd.Series(np.zeros(11)),
          'max': pd.Series(np.zeros(11)),
          'unit': pd.Series(['' for i in range(11)]),
    })
    return df
def table_extractor_main(input_file):
    # folder_path = 'all_pdfs'
    company = ['Infineon', 'onsemi', 'st_life_', 'ixys_littlefuse']

    company_idx = 0
    file_idx = 1
    df = main(input_file)
    df.fillna('', inplace=True)
    df.replace('-', '', inplace=True)
    # dataframe is empty then create dummy dataframe
    if df.empty:
       df = get_data_for_empty()
    return desire_value_extractor(df)
