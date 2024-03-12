import os
import shutil
def file_move_with_url(url, new_path=['media','pdfs','selected']):
    files_token = url.split('/')[3:]
    file_name = files_token[3]
    dir_file_name =os.path.join(*files_token)
    new_dir = os.path.join(*new_path)

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    new_dest = os.path.join(new_dir, file_name + '.jpg')
    shutil.move(dir_file_name, new_dest)
    shutil.rmtree(os.path.join(*files_token[:4]))
    return [*new_path, file_name + '.jpg']