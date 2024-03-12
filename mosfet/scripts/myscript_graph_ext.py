from mosfet.scripts.graph_extraction import *
def allextract_images_with_file(pdf_path, output_folder):
    graph_keys = "mosfet/scripts/graph_strings.csv"
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

    # filename = pdf_path.split('/')[-1].split('.pdf')[0]
    filename = os.path.split(pdf_path)[-1]
    # print(filename)
    # if filename not in ['Infineon_IMZ120R030M1H_DataSheet_v02_02_EN-1622480']:
    #     continue
    main_output_path = os.path.join(output_folder, filename, '')
    if not os.path.exists(main_output_path):
        os.makedirs(main_output_path)

    extract_graphs_from_pdf(pdf_path, main_output_path, size_increase)
    print(f"Images extracted and resized from {filename} pdf successfully!")
    detect_graph_list = natsorted(glob(f"{main_output_path}1st_Pass_Graphs/*.*"))
    detect_graph_list = detect_graph_list[:]
    req_main_grph_output = f"{main_output_path}FInal_Graph_Required/"
    if not os.path.exists(req_main_grph_output):
        os.makedirs(req_main_grph_output)
    req_graph_list = get_req_graphs(detect_graph_list, doc_type_list2, req_main_grph_output)
    print(f"Graph Extracted from {filename} pdf successfully!")

