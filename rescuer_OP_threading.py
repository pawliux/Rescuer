import threading
import tkinter as tk
from tkinter import filedialog
import os
from shutil import copyfile
import datetime

from file_extensions import ImageExtensions, AudioExtensions, DocumentExtensions, VideoExtensions


class Files:
    """ class for all file results and actions to be hold """

    def __init__(self):
        self.FILES = {}
        self.bgThread = None

    def start_analysis(self):
        self.bgThread = threading.Thread()
        self.bgThread.__init__(target=self.analyze, args=())
        self.bgThread.start()


    def analyze(self):

        AppGUI.information.set("Analyzing... Please wait!")
        path = Actions.source_folder
        for root, directories, files in os.walk(path):
            for file in files:
                f_path = os.path.join(root, file)
                # if file extension is among those we are looking for and if f_path is a file not a directory
                if self.is_checked(f_path) and os.path.isfile(f_path):
                    # adding r to the path to be able to split root directory from the path
                    split_array, path = self.split("r" + f_path)
                    self.analyze_array(split_array, path)

        print(self.FILES)
        AppGUI.information.set("Done. You can start rescue of files.")

    @staticmethod
    def is_checked(file):
        filename, extension = os.path.splitext(file)
        if extension != "":
            extension = extension[1:]
            if extension in Actions.EXTENSIONS:
                return True
        return False

    @staticmethod
    def split(path):
        return path.split("/"), path[1:]

    def analyze_array(self, split_array, path):
        cursor = self.FILES
        for i in range(len(split_array)):
            # if we looped to the last segment of the path (filename)
            if i == len(split_array) - 1:
                # then we set cursor to the file path on the system for later reference, r segment is removed
                cursor[split_array[i]] = path
            else:
                # if not yet created a dictionary on the cursor then create it
                if split_array[i] not in cursor:
                    cursor[split_array[i]] = {}
                # if dictionary type is created then cursor is set one step deeper in FILES
                cursor = cursor[split_array[i]]


    def start_copying(self):
        self.bgThread = threading.Thread()
        self.bgThread.__init__(target=self.copy_files, args=())
        self.bgThread.start()


    def copy_files(self):
        self.find_files(self.FILES, Actions.destination_folder)
        AppGUI.information.set("File rescue complete.")

    def find_files(self, SOURCE, current_save_path):
        # first looping through all not meaningful directories with only one child
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
                print("trying recursive on " + key)
                if not os.path.isdir(current_save_path):
                    os.mkdir(current_save_path)
                # setting current path to one folder deeper
                new_save_path = os.path.join(current_save_path, key)
                # examining deeper path recursively
                self.find_files(cursor[key], new_save_path)
            else:
                # copy a file here
                # if directory to save the file in not created, then creating directory
                if not os.path.isdir(current_save_path):
                    os.mkdir(current_save_path)
                # copy file (path to file is value of cursor[key]) to destination directory
                AppGUI.information.set("copying {} to {}".format(key, current_save_path))
                copyfile(cursor[key], os.path.join(current_save_path, key))



class Actions:
    source_folder = None
    destination_folder = None
    EXTENSIONS = []

    @staticmethod
    def pick_extensions():
        Actions.EXTENSIONS.extend(AudioExtensions)
        Actions.EXTENSIONS.extend(ImageExtensions)
        Actions.EXTENSIONS.extend(DocumentExtensions)
        Actions.EXTENSIONS.extend(VideoExtensions)

    @staticmethod
    def get_default_destination():
        now = datetime.datetime.now()
        destination_foldername = "Saved on {}-{}-{}".format(now.year, now.month, now.day)
        destination_foldername = os.path.join(os.path.expanduser("~"), "PCREPAIR", destination_foldername)
        Actions.destination_folder = destination_foldername
        return destination_foldername

    @staticmethod
    def open_source_dir(entry_field):
        d = filedialog.askdirectory()
        entry_field.delete(0, tk.END)
        entry_field.insert(0, d)
        Actions.source_folder = d

    @staticmethod
    def open_destination_dir(entry_field):
        d = filedialog.askdirectory()
        entry_field.delete(0, tk.END)
        entry_field.insert(0, d)
        Actions.destination_folder = d


class AppGUI(tk.Frame):
    """ class to define tkinter GUI"""
    information = None

    def __init__(self, parent,):
        # initiate objects
        f = Files()
        Actions.pick_extensions()
        AppGUI.information = tk.StringVar()
        AppGUI.information.set("")


        # initiate GUI
        tk.Frame.__init__(self, master=parent)

        # source directory gui
        tk.Label(parent, text="Source: ", width=15, anchor=tk.E).grid(row=0, column=1)
        source_entry = tk.Entry(parent, width=60)
        source_entry.grid(row=0, column=2, ipady=5)
        openDir_source_button = tk.Button(parent, text="Choose directory", width=15, command=lambda: Actions.open_source_dir(source_entry))
        openDir_source_button.grid(row=0, column=3, padx=10)

        # destination directory gui

        tk.Label(parent, text="Destination:", width=15, anchor=tk.E).grid(row=1, column=1)
        destination_entry = tk.Entry(parent, width=60)
        destination_entry.grid(row=1, column=2, ipady=5)

        # set default save destination
        destination_entry.insert(0, Actions.get_default_destination())
        openDir_destination_button = tk.Button(parent, text="Choose directory", width=15, command=lambda: Actions.open_destination_dir(destination_entry))
        openDir_destination_button.grid(row=1, column=3, padx=10)

        # action buttons
        analyze_button = tk.Button(parent, text="Start analyzer", width=20, command=f.start_analysis)
        analyze_button.grid(row=2, column=1, columnspan=3, padx=20)

        save_button = tk.Button(parent, text="Save chosen files",  width=20, command=f.start_copying)
        save_button.grid(row=3, column=1, columnspan=3, padx=20)

        info_label = tk.Label(parent, textvariable=AppGUI.information, width=80, borderwidth=1, relief=tk.SUNKEN, anchor=tk.W)
        info_label.grid(row=4, column=1, columnspan=3, pady=20, ipady=4)


if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.geometry("800x480")
    ROOT.title("File Rescuer by pawliux")
    APP = AppGUI(ROOT)
    ROOT.mainloop()