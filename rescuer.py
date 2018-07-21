import os
from tkinter import *
from tkinter import filedialog
import datetime
from shutil import copyfile
from file_extensions import ImageExtensions, AudioExtensions, DocumentExtensions, VideoExtensions

# FUNCTIONS
# pick a source directory


def open_source_dir():
    d = filedialog.askdirectory()
    source_entry.delete(0,END)
    source_entry.insert(0, d)

# pick a destination directory


def open_destination_dir():
    d = filedialog.askdirectory()
    source_entry.delete(0,END)
    source_entry.insert(0, d)

# start analyzing function


def analyze():
    info_var.set("Analyzing...")
    path = source_entry.get()
    for root, directories, files in os.walk(path):
        for file in files:
            f_path = os.path.join(root, file)
            # if file extension is among those we are looking for and if f_path is a file not a directory
            if is_checked(f_path) and os.path.isfile(f_path):
                # adding r to the path to be able to split root directory from the path
                split("r"+f_path)
    info_var.set("Done")

# Helper function for analyze() function. Adds file to a dictionary of FILES


def split(path):
    split_array = path.split("/")
    cursor = FILES
    for i in range(len(split_array)):
        # if we looped to the last segment of the path (filename)
        if i == len(split_array)-1:
            # then we set cursor to the file path on the system for later reference, r segment is removed
            cursor[split_array[i]] = path[1:]
        else:
            # if not yet created a dictionary on the cursor then create it
            if split_array[i] not in cursor:
                cursor[split_array[i]] = {}
            # if dictionary type is created then cursor is set one step deeper in FILES
            cursor = cursor[split_array[i]]

# Checks if file is among the chosen ones to recover


def is_checked(file):
    filename, extension = os.path.splitext(file)
    if extension != "":
        extension = extension[1:]
        if extension in EXTENSIONS:
            return True
    return False

# Makes one array from all chosen extensions


def pick_extensions():
    EXTENSIONS.extend(AudioExtensions)
    EXTENSIONS.extend(ImageExtensions)
    EXTENSIONS.extend(DocumentExtensions)
    EXTENSIONS.extend(VideoExtensions)

# Starts do the copy job


def copy_files():
    find_files(FILES, default_destination)


def find_files(SOURCE, current_path):
    #first looping through all not meaningful directories with only one child
    cursor = SOURCE
    cursorLength = cursor.__len__()
    while cursorLength == 1:
        # list(cursor.keys())[0] returns the only key in the dictionary of length 1
        # if the key is a file name then break loop
        if type(cursor[list(cursor.keys())[0]]) is dict:
            cursor = cursor[list(cursor.keys())[0]]
            cursorLength = cursor.__len__()
        else:
            break

    print("last cursor:")
    print(cursor)

    # keep track of save path
    # if there was more than one child
    for key in cursor:
        # if the child of cursor is dictionary
        if type(cursor[key]) is dict:
            # create a directory at the current destination path if it's not created
            info_var.set("trying recursive on "+key)
            if not os.path.isdir(current_path):
                os.mkdir(current_path)
            # setting current path to one folder deeper
            new_path = os.path.join(current_path, key)
            # examining deeper path recursively
            find_files(cursor[key], new_path)
        else:
            # copy a file here
            # if directory to save the file in not created, then creating directory
            if not os.path.isdir(current_path):
                os.mkdir(current_path)
            # copy file (path to file is value of cursor[key]) to destination directory
            copyfile(cursor[key], os.path.join(current_path, key))
            info_var.set("copying {} to {}".format(key, current_path))


# Generates destination folder name with current date


def generate_destination_folder():
    now = datetime.datetime.now()
    global destination_foldername
    destination_foldername = "Saved on {}{}{}".format(now.year, now.month, now.day)
    destination_foldername = os.path.join("PCREPAIR", destination_foldername)
    print(destination_foldername)


FILES = {}
EXTENSIONS = []
pick_extensions()

generate_destination_folder()
default_destination = os.path.join(os.path.expanduser("~"), destination_foldername)


window = Tk()
window.geometry("800x480")
window.title("File Rescuer by pawliux")

openDir_source_frame = Frame(window)
openDir_source_frame.pack(side=TOP, pady=10)
label = Label(openDir_source_frame, text="Source:", width=15, anchor=E)
label.pack(side=LEFT, padx=2)
source_entry = Entry(openDir_source_frame, width=60)
source_entry.pack(side=LEFT, ipady=5)
openDir_source_button = Button(openDir_source_frame, text="Choose directory", command=open_source_dir)
openDir_source_button.pack(side=LEFT, padx=10)

openDir_destination_frame = Frame(window)
openDir_destination_frame.pack(pady=10)
label = Label(openDir_destination_frame, text="Destination:", width=15, anchor=E)
label.pack(side=LEFT, padx=2)
destination_entry = Entry(openDir_destination_frame, width=60)
destination_entry.pack(side=LEFT, ipady=5)
# set default save destination
destination_entry.insert(0, default_destination)
openDir_destination_button = Button(openDir_destination_frame, text="Choose directory", command=open_destination_dir)
openDir_destination_button.pack(side=LEFT, padx=10)

analyze_button = Button(window, text="Start analyzer", command=analyze)
analyze_button.pack(fill=X, padx=20)
save_button = Button(window, text="Save chosen files", command=copy_files)
save_button.pack(fill=X, padx=20)

info_var = StringVar()
Label(window, textvariable=info_var).pack(fill=X, padx=20)




if __name__ == "__main__":
    window.mainloop()