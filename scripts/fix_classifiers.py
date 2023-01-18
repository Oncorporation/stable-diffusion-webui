import os
import hashlib
from PIL import Image

# directory where the files are located
# exec(open(r"F:\sd\stable-diffusion-webui\scripts\fix_classifiers.py").read())
# fix_classifier_folder("F:/sd/stable-diffusion-webui/models/dreambooth/Classifiers/mecha")

def fix_classifier_folder(directory, ui=False):
    renamed_files_count = 0
    renamed_files = []
    if directory is None:
        directory = os.getcwd()
    print("Path of the directory : " + directory)    

    # iterate through all the files in the directory
    for filename in os.listdir(directory):
        # only use image files
        if filename.endswith(".png"):
            # get the file extension
            filebase = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]
            # get image file
            image = Image.open(os.path.join(directory, filename))
            # read the contents of the file description
            with open(os.path.join(directory, filebase + ".txt"), 'rb') as file:
                text = file.read()
            image.info["parameters"] = text
            # calculate the sha1 hash of the file contents
            sha1 = hashlib.sha1(image.tobytes()).hexdigest()
            # construct the new filename with the sha1 hash and the original extension
            new_filename = sha1 + extension
            new_filename_desc = sha1 + ".txt"
            filename_desc = filebase + ".txt"
            
            # rename the file
            try:
                if new_filename != filename:                
                    print("renaming "+ filename + " to " + new_filename + "")
                    os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
                    renamed_files.append(filename + ", " + new_filename)

                    print("renaming "+ filename_desc + " to " + new_filename_desc)
                    os.rename(os.path.join(directory, filename_desc), os.path.join(directory, new_filename_desc))
                    renamed_files.append(filename_desc + ", " + new_filename_desc)

                    renamed_files_count += 1
            except Exception as p:
                print(f"Exception renaming files: {str(p)}")
                #traceback.print_exc()
                #if ui:
                #    return 0, []
                #else:
                #    return 0, inst_paths, class_paths


    return renamed_files, renamed_files_count