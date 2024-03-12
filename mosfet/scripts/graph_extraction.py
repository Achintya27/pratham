# import pytesseract
from PIL import Image
import pdf2image
import cv2
import os
import numpy as np
import pandas as pd
# from PIL import Image
from glob import glob
from natsort import natsorted
import re
import shutil
import os
import traceback
import requests
import json
from mosfet.scripts.status_code import *
import time
import jellyfish as jf

#   37fa92b6349a4a608b5403d9fd651cc7

text_recognition_url = 'https://text-ocr01.cognitiveservices.azure.com/' + \
                       "vision/v3.2/read/analyze"  # URL for OCR

# 508c209e24d044628faaafc2d20e78d4 b81d845abefe49e48ab864942906e32a

# Free Credits key
# 0f02f35595e24592b934b0691948c135 b81d845abefe49e48ab864942906e32a
api_key = "56f00dd1830140dfbc12fc64662f894e"
headers = {'Ocp-Apim-Subscription-Key': api_key,
           'Content-Type': 'application/octet-stream'}

# def op_location_fun(img_file_path):
#     result = {}
#     try:
#         ## read pdf split and send API request, it returns a operation location
#         try:
#             with open(img_file_path, 'rb') as img_file:  # read pdf from  pdf_paths
#                 response = requests.post(text_recognition_url, headers = headers, data = img_file)

#             ## check if API returns success code
#             if response.status_code==202:
#                 ## get opearation location for respective pdf split
#                 op_loc = response.headers["Operation-Location"]
#                 # print(op_loc)
#                 content = [op_loc, img_file_path] # combine operation location and pdf name
#                 ## append operation location and pdf split name to op_loc_list
#                 # op_loc_list.append(content)
#             else:
#                 ## if API response does not return success code.
#                 ## combine operation location("NA") and pdf name and append to op_loc_list
#                 content = ["NA", img_file_path]
#                 # op_loc_list.append(content)

#             ## return sucess code with op_loc_list and original pdf_name
#             result.update({'res_code': STATUS_200, 'status_str': STR_200, 'result':[content]})
#             return result

#         except Exception as es:
#             result.update({'res_code': STATUS_500, 'status_str': es, 'result': None})
#             return result

#     except Exception as es:
#         print(traceback.print_exc())
#         result.update({'res_code': STATUS_500, 'status_str': es, 'result': None})
#         return result


import time


def op_location_fun(img_file_path):
    result = {}
    try:
        ## read pdf split and send API request, it returns an operation location
        try:
            with open(img_file_path, 'rb') as img_file:  # read pdf from pdf_paths
                response = requests.post(text_recognition_url, headers=headers, data=img_file)

            while response.status_code != 202 or 'Operation-Location' not in response.headers:
                time.sleep(1)  # Wait for 1 second before rechecking
                # response = requests.post(text_recognition_url, headers=headers, data=img_file)

            # Extract operation location once received
            op_loc = response.headers.get("Operation-Location")
            content = [op_loc, img_file_path]

            # Return success code with operation location and original pdf_name
            result.update({'res_code': STATUS_200, 'status_str': STR_200, 'result': [content]})
            return result

        except Exception as es:
            result.update({'res_code': STATUS_500, 'status_str': str(es), 'result': None})
            return result

    except Exception as es:
        print(traceback.print_exc())
        result.update({'res_code': STATUS_500, 'status_str': str(es), 'result': None})
        return result


def create_json_file(status):
    result = {}
    try:
        if status.get('res_code') == STATUS_200:
            ## get result from op_location_fun
            op_loc_list = status.get('result')[0]

            ## get the pdf name
            pdf_file_path = op_loc_list[1]
            filename = pdf_file_path.split('/')[-1]
            pdf_name = os.path.splitext(filename)[0]

            ## creete a json folder with pdf name, to store json response from API
            # json_path = os.path.join(json_folder + "/" + pdf_name + "/")
            # print(json_path)
            # if not os.path.exists(json_path):  # check if directory exists
            # os.makedirs(json_path)
            try:
                ## check if there are any operation locations
                if len(op_loc_list) > 0:
                    ## get operation location
                    operation_location = op_loc_list[0]
                    # time.sleep(10)
                    ## if there is a valid operation location for pdf split
                    if operation_location != 'NA':
                        # read_operation_location = op_loc_list[0][0]
                        ## craeting an empty dictionary to store json results
                        analysis = {}
                        poll = True

                        while (poll):
                            ## call the api with operation location
                            ## operation location is a URL that was returned by first API Call
                            response_final = requests.get(operation_location,
                                                          headers=headers)  # extract data from operaion location
                            ## get the response from API and store in dictionary
                            analysis = response_final.json()

                            ## if succeed then stop
                            if "analyzeResult" in analysis:
                                poll = False
                            ## or if failed then stop
                            if "status" in analysis and analysis['status'] == 'failed':
                                poll = False

                        if "analyzeResult" in analysis:
                            ## open a json file and dump the results in Single JSON file
                            # with open(os.path.join(json_path + pdf_name + ".json"), 'w', encoding='utf-8') as f:
                            #     json.dump(analysis, f, ensure_ascii=False, indent=4)

                            result.update({'res_code': STATUS_200, 'status_str': STR_200, 'result': [analysis]})
                            return result
                    else:
                        ## if there is no valid operation location for pdf split
                        # related_name_list.append(op_loc_list[0][1])
                        ## return error msg with split pdf list and pdf name
                        result.update({'res_code': STATUS_511, 'status_str': STR_511, 'result': [analysis]})
                        return result


                else:
                    ## if there are no operation locations return error string 506
                    result.update({'res_code': STATUS_506, 'status_str': STR_506, 'result': None})
                    return result

            except Exception as es:
                result.update({'res_code': STATUS_500, 'status_str': es, 'result': None})
                return result
        else:
            ## return result from op_location_fun
            return status
    except Exception as es:
        traceback.print_exc()
        print('In create json file : ', es)
        result.update({'res_code': STATUS_500, 'status_str': es, 'result': None})
        return result


def calculate_overlap(rect1, rect2):
    # Calculate overlap area of two rectangles
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = cv2.boundingRect(rect2)

    # Calculate coordinates of intersection
    x_left = max(x1, x2)
    y_top = max(y1, y2)
    x_right = min(x1 + w1, x2 + w2)
    y_bottom = min(y1 + h1, y2 + h2)

    # Calculate area of intersection rectangle
    intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)

    # Calculate areas of both rectangles
    area_rect1 = w1 * h1
    area_rect2 = w2 * h2

    # Calculate overlap percentage
    overlap_percentage = intersection_area / min(area_rect1, area_rect2)

    return overlap_percentage


def extract_graphs_from_pdf(pdf_path, main_output_path, size_increase=120):
    output_folder = f'{main_output_path}1st_Pass_Graphs/'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    pages = pdf2image.convert_from_path(pdf_path)
    # print(len(pages))
    count = 0
    for page_num, page in enumerate(pages):

        page_np = np.array(page)  # Convert PIL.Image to numpy array
        total_area = page_np.shape[0] * page_np.shape[1]
        gray = cv2.cvtColor(page_np, cv2.COLOR_BGR2GRAY)
        # Apply thresholding
        _, binary_image = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)

        kernel = np.ones((1, 1), np.uint8)
        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
        # Find contours
        contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filter the detected contours to only include those that are likely to be graphs
        graph_contours = []
        bounding_boxes = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            area = w * h
            should_add = None
            # if cv2.contourArea(contour) > 80000 and cv2.contourArea(contour)<250000:  # Minimum contour area
            if 0.2 > (area / total_area) > 0.03:
                should_add = True
                # Check overlap with existing graph_contours
                for existing_contour in graph_contours:

                    if calculate_overlap((x, y, w, h), existing_contour) > 0.5:  # Set your overlap threshold here
                        should_add = False
                        break

                if should_add:
                    graph_contours.append(contour)

                # graph_contours.append(contour)

        # Save the potential graph regions as images with increased size
        for idx, contour in enumerate(graph_contours):
            count += 1
            x, y, w, h = cv2.boundingRect(contour)
            x -= size_increase
            y -= size_increase
            w += 2 * size_increase
            h += 2 * size_increase

            # Ensure that the new coordinates are within the image boundaries
            x = max(0, x)
            y = max(0, y)
            w = min(gray.shape[1] - x, w)
            h = min(gray.shape[0] - y, h)

            graph_region = page.crop((x, y, x + w, y + h))
            graph_region = graph_region.resize((w + 2 * size_increase, h + 2 * size_increase))

            graph_filename = f"page_{page_num + 1}_graph_{idx + 1}.jpg"
            graph_path = os.path.join(output_folder, graph_filename)
            graph_region.save(graph_path)  # Use the PIL save method here
            # print(graph_path)
    # print("PAGE COUNT: ",count)


def perform_ocr(pdf_file_path):  ## specifically for desktop application
    result = {}
    status1 = None
    try:
        ## create folder to store split pdfs for pdf file
        status1 = op_location_fun(pdf_file_path)
        # print('STATUS 1 : ', status1)
        if status1.get('res_code') == STATUS_200 or status1.get('result') != None:

            ## create folder to store Jsons for pdf file

            status2 = create_json_file(status1)['result'][0]

            # print('STATUS 2 : ', status2)
            if status2.get('res_code') != STATUS_200:
                result.update({'res_code': STATUS_200, 'status_str': STR_200, 'result': [status2]})
                return result
        ## return success code with output_path
        # else:
        #     perform_ocr(pdf_file_path)

    except Exception as es:
        result.update({'res_code': STATUS_500, 'status_str': es, 'result': [None]})
        return result


'''N-gram search'''


def n_gram_search(search_val, string_val, doc_type=''):
    try:
        search_val, string_val = str(search_val).strip().lower().replace('  ', ' '), str(
            string_val).strip().lower().replace('  ', ' ')

        s1_len, s1_char_len, s2_len, s2_char_len = len(search_val.split()), len(search_val), len(
            string_val.split()), len(string_val)
        # print(s1_len, s1_char_len, s2_len, s2_char_len)
        # if(search_val == 'a/c reg no'):
        #     print('s1 len:', s1_len, search_val, '\ts1 char len:', s1_char_len, '\ts2 len:', s2_len, string_val)
        found_val, words_list = 0, string_val.split()
        doc_type_thresh = 0.82 if (len(search_val) >= 5) else 1

        # if string_val in "Aircraft Test Report":
        #     print(True)
        #     print(search_val, '||',string_val)

        if (doc_type == 'ARC'):
            doc_type_thresh = 0.7

        match_pct = 1 - jf.levenshtein_distance(search_val, string_val) / max(s1_char_len, s2_char_len)
        if (match_pct >= doc_type_thresh):
            found_val = 1
            return found_val

        if (s1_len == 1 and search_val in words_list):
            '''check if word is 100% match'''
            # print(f'{s1_len}-gram "{search_val}" matched 100% with word from string')
            found_val = 1

        # elif(s1_len > 1 and search_val in string_val):
        #     '''check if n-gram is 100% match'''
        #     print(f'{s1_len}-gram "{search_val}" matched 100% with string')
        #     found_val = 1
        elif (s1_len > 1 and search_val in string_val):
            # print(f'Page {pg_idx} => {s1_len}-gram "{search_val}" matched 100% {string_val} - sub-string matching')
            found_val = 1

        elif (s1_len == s2_len):
            '''if same len'''
            match_pct = 1 - jf.levenshtein_distance(search_val, string_val) / max(s1_char_len, s2_char_len)

            if (match_pct >= doc_type_thresh):
                # print('doc_type_thresh:', doc_type_thresh)
                found_val = 1
                # print(f'{s1_len}-gram "{search_val}" matched {match_pct}% with string: {string_val}')

        elif (s2_len > s1_len):
            '''check with n-grams'''

            if (s1_len == 1):
                grams = list(zip(words_list))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 2):
                grams = list(zip(words_list, words_list[1:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 3):
                grams = list(zip(words_list, words_list[1:], words_list[2:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val, 'match_pct:', match_pct)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 4):
                grams = list(zip(words_list, words_list[1:], words_list[2:], words_list[3:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 5):
                grams = list(zip(words_list, words_list[1:], words_list[2:], words_list[3:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 6):
                grams = list(zip(words_list, words_list[1:], words_list[2:], words_list[3:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break

            elif (s1_len == 7):
                grams = list(zip(words_list, words_list[1:], words_list[2:], words_list[3:]))
                # print(grams)

                for gram in grams:
                    gram_val = ' '.join(gram)
                    gram_char_len = len(gram_val)
                    # print('Gram char len:', gram_char_len, '\tGram_val:', gram_val)

                    match_pct = 1 - jf.levenshtein_distance(search_val, gram_val) / max(s1_char_len, gram_char_len)

                    if (match_pct >= doc_type_thresh):
                        found_val = 1
                        # print(f'{s1_len}-gram "{search_val}" matched {round(match_pct, 2)}% with string: {string_val}')
                        break
        #     else:
        #         print('No ngram match found!')
        # else:
        #     print('No ngram match found!')

        return found_val
    except:
        traceback.print_exc()


# def approx_search_doc_str(split_key,line_str_no_spl_val):
#     found = 0
#     split_key = re.sub(r'[^\w\s]+','',split_key)

#     if split_key in line_str_no_spl_val:
#         print(split_key,line_str_no_spl_val)
#         found = 1

# return found


def get_req_graphs(detect_graph_list, doc_type_list2, output_path):
    req_graph = set()
    batch_size = 5
    for i in range(0, len(detect_graph_list[:]), batch_size):
        batch = detect_graph_list[i:i + batch_size]  # Slice the list to get a batch of files
        # print("Processing batch:", batch)
        # Perform operations on the batch of files here
        # For example, print the files in this batch
        for graph_img in batch[:]:
            graph_img_name = graph_img.split(".jpg")[0].split('/')[-1]
            # if graph_img_name not in ['page_3_graph_4']:
            #     continue
            try:
                # print(f"Graph Image Name: {graph_img_name}")
                analysis = perform_ocr(graph_img)['result'][0]
                if analysis:
                    # print(analysis['status'])

                    try:

                        if "analyzeResult" in analysis and analysis['status'] == "succeeded" and len(
                                analysis['analyzeResult']['readResults'][0]['lines']) <= 49:

                            pages = analysis['analyzeResult']['readResults'][0]

                            total_lines = len(pages['lines'])
                            match_found = 0

                            for key in doc_type_list2:
                                key = key[0]
                                # print(key)
                                total_match = 0
                                match_word = []

                                if "+" in key:
                                    total_key = len(key.split('+'))
                                    for split_key in key.split('+'):
                                        if not match_found:

                                            for line_no, line in enumerate(pages['lines'][:]):

                                                for word_no, word in enumerate(line['words'][:]):

                                                    word_str_no_spl_val = re.sub(r'[^\w/()\- ]', '',
                                                                                 str(word['text'])).lower()
                                                    word_str_no_spl_val = re.sub(r'\(|\)', '', word_str_no_spl_val)

                                                    if word['boundingBox'][0] <= 900 and word['boundingBox'][1] > 20:
                                                        # print("PDF_TEXT: ",line['text'],line['boundingBox'])

                                                        if split_key != '' and word_str_no_spl_val != '':
                                                            split_key = split_key.lower()
                                                            found = n_gram_search(split_key, word_str_no_spl_val,
                                                                                  doc_type='')

                                                            if found and split_key not in match_word:
                                                                match_word.append(split_key)

                                                                total_match += 1
                                                                # print(split_key, word_str_no_spl_val, total_match,
                                                                #       total_key, key)
                                                                break

                                                if total_match == total_key:
                                                    match_found = 1
                                                    # print(word_str_no_spl_val, ' ', key, 'BoundingBox: ',
                                                    #       line['boundingBox'])

                                                    # print(f"RDSon Graph Found: {graph_img}")
                                                    req_graph.add(graph_img)
                                                    # print("Graphs Successfully moved")

                                                    shutil.copy(graph_img, output_path)
                                                    break

                                        else:
                                            break
                                if match_found:
                                    break
                    except:
                        traceback.print_exc()
            except:
                traceback.print_exc()

    # print(f"Final Image After Using String: {len(req_graph)}")
    return list(sorted(req_graph))


# def move_req_graphs(req_graph_list,output_path):

#     for graph_img in req_graph_list:
#         shutil.copy(graph_img, output_path)


if __name__ == "__main__":
    print("CODE STARTS")
    pdf_path = '/mnt/f/mysite/datasheets/Infineon/Infineon_IAUC60N04S6L030H_DataSheet_v01_00_EN-1921391.pdf'
    output_folder = "/mnt/f/mysite/LOCAL_TESTING/OUTPUT_10_Dec_2023_02/"  # Folder where images will be saved
    graph_keys = "/mnt/f/mysite/Notebooks/graph_strings.csv"
    size_increase = 130  # Set the desired size increase
    classify_cisc_strs_data2 = pd.read_csv(graph_keys, usecols=[0])
    formatted_doc_type_df2 = pd.DataFrame(classify_cisc_strs_data2)
    formatted_doc_type_df2['keywords'] = formatted_doc_type_df2['keywords'].apply(lambda x: '+'.join(
        sorted(str(x).lower().replace(' +', '+').replace('+ ', '+').replace(' + ', '+').replace('  ', ' ').split('+'),
               key=lambda x: str(x)[0])))
    formatted_doc_type_df2 = formatted_doc_type_df2.drop_duplicates()
    formatted_doc_type_df2['sent_len'] = formatted_doc_type_df2['keywords'].apply(lambda x: len(x))
    formatted_doc_type_df2 = formatted_doc_type_df2.sort_values(by=['sent_len'], ascending=[False])
    doc_type_list2 = formatted_doc_type_df2.iloc[:, :1].values.tolist()

    filename = pdf_path.split('/')[-1].split('.pdf')[0]
    print(filename)
    # if filename not in ['Infineon_IMZ120R030M1H_DataSheet_v02_02_EN-1622480']:
    #     continue
    main_output_path = output_folder + filename + '/'
    if not os.path.exists(main_output_path):
        os.makedirs(main_output_path)

    extract_graphs_from_pdf(pdf_path, main_output_path, size_increase)
    print("Graphs extracted and resized successfully!")
    detect_graph_list = natsorted(glob(f"{main_output_path}1st_Pass_Graphs/*.*"))
    detect_graph_list = detect_graph_list[:]
    req_main_grph_output = f"{main_output_path}FInal_Graph_Required/"
    if not os.path.exists(req_main_grph_output):
        os.makedirs(req_main_grph_output)
    req_graph_list = get_req_graphs(detect_graph_list, doc_type_list2, req_main_grph_output)
