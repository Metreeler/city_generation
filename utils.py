import os
import shutil

def reset_files(folder):
    if not os.path.isdir(folder):
        folders = folder.split("/")
        folder_path = ""
        
        for f in folders[:-1]:
            folder_path += f + "/"
            if not os.path.isdir(folder_path):
                os.mkdir(folder_path)
            
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                reset_files(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))