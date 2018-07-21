import sys
import threading
import os
from shutil import copyfile
import datetime
import re
import subprocess

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from rescuePack import *

from file_extensions import ImageExtensions, AudioExtensions, DocumentExtensions, VideoExtensions


class ExtendedTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, *args, **kwargs):
        super(ExtendedTreeWidgetItem, self).__init__(*args, **kwargs)
        self.rescueFile = None
    
    def setRescueFile(self, rFile):
        self.rescueFile = rFile
        # print("setting rescue file",self.rescueFile)

    def getRescueFile(self):
        return self.rescueFile

    def generatePathToItem(self):
        path = self.text(0)

        parent = self.parent()
        while parent:
            path = os.path.join(parent.text(0), path)
            parent = parent.parent()

        return path
    

class RescueFile:
    def __init__(self, path, size):
        self.path = path
        self.filesize = size
        self.ischecked = True

    def isChecked(self):
        return self.ischecked

    def setChecked(self, checked):
        if isinstance(checked, bool):
            self.ischecked = checked
        elif isinstance(checked, Qt.CheckState):
            self.ischecked = True if checked == Qt.Checked else False
        # print(self.path, self.ischecked)
    
    def getFileSize(self):
        units = ""
        if self.filesize < 1000:
            units = " B"
            return str(self.filesize)+units
        elif self.filesize < 1000000:
            units = " KB"
            return str(round(self.filesize/1000, 2))+units
        elif self.filesize < 1000000000:
            units = " MB"
            return str(round(self.filesize/1000000, 2))+units
        else:
            units = " GB"
            return str(round(self.filesize/1000000000, 2))+units

    def getPath(self):
        return self.path


class Actions:
    source_folder = None
    destination_folder = None
    EXTENSIONS = []

    @staticmethod
    def pick_extensions():
        Actions.EXTENSIONS = []
        Actions.EXTENSIONS.extend(ExtensionDialog.generateListOfExtentionsToRescue())
        print(Actions.EXTENSIONS)

    @staticmethod
    def get_default_destination():
        now = datetime.datetime.now()
        destination_foldername = "Saved on {}-{}-{}".format(now.year, now.month, now.day)
        destination_foldername = os.path.join(os.path.expanduser("~"), "PCREPAIR", destination_foldername)
        Actions.destination_folder = destination_foldername
        return destination_foldername

    @staticmethod
    def open_source_dir(self):
        dir_name = QFileDialog.getExistingDirectory()
        Actions.update_source_dir(dir_name)
        GUI.source_entry.setText(dir_name)

    @staticmethod
    def open_destination_dir(self):
        dir_name = QFileDialog.getExistingDirectory()
        Actions.destination_folder = dir_name
        GUI.destination_entry.setText(dir_name)

    @staticmethod
    def update_source_dir(dir_name):
        if os.path.exists(dir_name):
            Actions.source_folder = dir_name
            GUI.updateInfo("Source folder updated to {}".format(dir_name))
        else:
            GUI.updateInfo("Invalid source directory, please check!")

    @staticmethod
    def update_destination_dir(dir_name):
        if os.path.isabs(dir_name):
            Actions.destination_folder = dir_name
            GUI.updateInfo("Destination folder updated to {}".format(dir_name))
        else:
            GUI.updateInfo("Invalid destination path. Please check!!")
        


    @staticmethod
    def isValidDirectory(dir_name):
        if dir_name == "" or dir_name is None:
            return False
        elif os.path.exists(dir_name):
            return True
        else:
            return False

class Files:
    """ class for all file results and actions to be hold """

    def __init__(self):
        self.bgThread = None

    def start_analysis(self):
        # cleaning up before we start
        self.FILES = {}
        GUI.treeWidget.clear()
        # if source directory is valid
        if Actions.isValidDirectory(Actions.source_folder):
            self.bgThread = threading.Thread()
            self.bgThread.__init__(target=self.analyze, args=())
            self.bgThread.start()
        else:
            GUI.updateInfo("Invalid source directory, please check!")


    def analyze(self):
        
        GUI.updateInfo("Analyzing... Please wait!")
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
        # generating a tree in tree widget
        if self.FILES.__len__() > 0:
            topTreeItem = ExtendedTreeWidgetItem()
            topTreeItem.setText(0, r'/')
            topTreeItem.setCheckState(0, Qt.Checked)
            self.buildATree(cursor=self.FILES['r'], treeCursor=topTreeItem)
            GUI.treeWidget.addTopLevelItem(topTreeItem)
            GUI.treeWidget.expandAll()

        # finished analyzing waiting for starting to rescue
        GUI.updateInfo("Done. You can start rescue of files.")

    def buildATree(self, cursor, treeCursor):
        for key in cursor:
            item = ExtendedTreeWidgetItem(treeCursor)
            item.setText(0, key)
            item.setCheckState(0, Qt.Checked)
            treeCursor.addChild(item)
            if isinstance(cursor[key], dict):
                self.buildATree(cursor[key], item)
            else:
                item.setRescueFile(cursor[key])
                item.setText(1, cursor[key].getFileSize())
                # print("item cursor",item, "item text", item.text(0), "rescue file", item.getRescueFile())

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
        print(split_array)
        cursor = self.FILES

        for i in range(len(split_array)):
            # print("split_array[i]", split_array[i])
            # if we looped to the last segment of the path (filename)
            if i == len(split_array) - 1:
                # then we set cursor to the file path on the system for later reference, r segment is removed
                cursor[split_array[i]] = RescueFile(path, os.path.getsize(path))                

            else:
                # if not yet created a dictionary on the cursor then create it
                if split_array[i] not in cursor:
                    cursor[split_array[i]] = {}

                # if dictionary type is created then cursor is set one step deeper in FILES
                cursor = cursor[split_array[i]]

    def start_copying(self):
        # if valid source and destination
        if (Actions.source_folder is not None and os.path.isdir(Actions.source_folder)) and \
           (Actions.destination_folder is not None and os.path.isabs(Actions.destination_folder)):
            self.bgThread = threading.Thread()
            self.bgThread.__init__(target=self.copy_files, args=())
            self.bgThread.start()
        else:
            GUI.updateInfo("Check source and destination directories.")


    def copy_files(self):
        os.makedirs(Actions.destination_folder)
        self.find_files(self.FILES, Actions.destination_folder)
        GUI.updateInfo("File rescue complete.")

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


        # keep track of save path
        # if there was more than one child
        for key in cursor:
            # if the child of cursor is dictionary
            if isinstance(cursor[key], dict):
                # create a directory at the current destination path if it's not created
                # print("trying recursive on " + key)
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
                GUI.updateInfo("copying {} to {}".format(key, current_save_path))
                # cursor[key] is RescueFile object
                if cursor[key].isChecked():
                    copyfile(cursor[key].getPath(), os.path.join(current_save_path, key))


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        windowSize = (800,600)
        screenSize = QDesktopWidget().availableGeometry()

        Actions.pick_extensions()
        self.f = Files()

        # center window
        self.setGeometry(screenSize.width()/2 - windowSize[0]/2, screenSize.height()/2 - windowSize[1]//2, windowSize[0], windowSize[1])
        self.setWindowTitle("Rescuer by pawliux v6")
        self.setWindowIcon(QIcon(os.path.join('icons', 'magnifier.png')))
        
        self.constructGui(windowSize)
        
        self.updateInfo("")
        
        self.show()
        

    def constructGui(self, windowSize):
        wgt = QWidget()
        vlayout = QVBoxLayout()
        vlayout.setAlignment(Qt.AlignTop)
        grid_layout = QGridLayout()

        # Source directory label
        self.source_label = QLabel("Source directory: ")
        self.source_label.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.source_label.setMinimumWidth(130)
        grid_layout.addWidget(self.source_label, 1, 1)
        # Source directory entry
        self.source_entry = QLineEdit()
        self.source_entry.setMaximumWidth(460)
        self.source_entry.returnPressed.connect(lambda: Actions.update_source_dir(self.source_entry.text()))
        grid_layout.addWidget(self.source_entry, 1, 2)
        # Source directory open button
        self.source_dir_button = QPushButton("Choose directory")
        self.source_entry.setMinimumWidth(150)
        grid_layout.addWidget(self.source_dir_button, 1, 3)
        self.source_dir_button.clicked.connect(Actions.open_source_dir)

        # Destination directory label
        self.destination_label = QLabel("Destination directory: ")
        self.destination_label.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.destination_label.setMinimumWidth(130)
        grid_layout.addWidget(self.destination_label, 2, 1)
        # Destination directory entry
        self.destination_entry = QLineEdit()
        self.destination_entry.setMaximumWidth(460)
        self.destination_entry.returnPressed.connect(lambda: Actions.update_destination_dir(self.destination_entry.text()))
        grid_layout.addWidget(self.destination_entry, 2, 2)
        self.destination_entry.setText(Actions.get_default_destination())
        # Destination directory open button
        self.destination_dir_button = QPushButton("Choose directory")
        self.destination_dir_button.setMinimumWidth(150)
        grid_layout.addWidget(self.destination_dir_button, 2, 3)
        self.destination_dir_button.clicked.connect(Actions.open_destination_dir)

        # Start analyzer button
        self.start_analysis_button = QPushButton("Begin analysis")
        self.start_analysis_button.setMinimumWidth(150)
        self.start_analysis_button.setMaximumWidth(150)
        grid_layout.addWidget(self.start_analysis_button, 3, 1, 1, 3, Qt.AlignHCenter)
        self.start_analysis_button.clicked.connect(self.f.start_analysis)
        # Rescue files button
        self.rescue_files_button = QPushButton("Rescue files")
        self.rescue_files_button.setMinimumWidth(150)
        self.rescue_files_button.setMaximumWidth(150)
        grid_layout.addWidget(self.rescue_files_button, 4, 1, 1, 3, Qt.AlignHCenter)
        self.rescue_files_button.clicked.connect(self.f.start_copying)

        # Info line
        self.info_line = QLabel("Information goes here")
        self.info_line.setStyleSheet("border: 1px solid grey;")
        self.info_line.setMinimumWidth(790)
        self.info_line.setMaximumWidth(790)
        self.info_line.setMinimumHeight(25)
        grid_layout.addWidget(self.info_line, 5, 1, 1, 3, Qt.AlignHCenter)

        self.setupTree(grid_layout)

        vlayout.addLayout(grid_layout)
        wgt.setLayout(vlayout)
        self.setCentralWidget(wgt)

        self.setupActionBar()

    def setupActionBar(self):
        self.menuBar().setNativeMenuBar(False)
        file_menu = self.menuBar().addMenu('&File')

        pickExtensions = QAction(QIcon(), "Pick file types", self)
        pickExtensions.setStatusTip("Pick file types to rescue")
        pickExtensions.triggered.connect(self.openExtensionDialog)
        file_menu.addAction(pickExtensions)

        exitAction = QAction(QIcon(), "Exit", self)
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(app.exit)
        file_menu.addAction(exitAction)

    def openExtensionDialog(self):
        dlg = ExtensionDialog()
        dlg.accepted.connect(Actions.pick_extensions)
        dlg.exec_()

    def setupTree(self, grid_layout):
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Results", "Size"])
        self.treeWidget.header().resizeSection(0, 600)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.itemChanged.connect(self.singleClickTreeWidget)
        self.treeWidget.itemDoubleClicked.connect(self.doubleClickTreeWidget)
        grid_layout.addWidget(self.treeWidget, 6, 1, -1, 3)

    def updateInfo(self, text):
        self.info_line.setText(text)

    def singleClickTreeWidget(self, widgetItem, column):
        # print("clicked on widget cursor", widgetItem, "text", widgetItem.text(0))
        parent = widgetItem.parent()
        if parent and parent.checkState(0) == Qt.Unchecked:
            widgetItem.setCheckState(0, Qt.Unchecked)
            return

        checkState = widgetItem.checkState(0)
        # checkState = Qt.Checked if widgetItem.checkState(0) == Qt.Unchecked else Qt.Unchecked

        widgetItem.setCheckState(0, checkState)
        rescue_file = widgetItem.getRescueFile()
        if rescue_file:
            rescue_file.setChecked(checkState)
        
        self.iterateThroughChildren(widgetItem, checkState)

    def iterateThroughChildren(self, item, checkState):
        for i in range(item.childCount()):
            child = item.child(i)
            # print("child",child, "text", child.text(0))
            child.setCheckState(0, checkState)
            rescue_file = child.getRescueFile()
            # print("rescue file",rescue_file, "child", child.text(0))
            if rescue_file:
                rescue_file.setChecked(checkState)
            else:
                self.iterateThroughChildren(child, checkState)


    def doubleClickTreeWidget(self, widgetItem, column):
        path = widgetItem.generatePathToItem()
        if widgetItem.getRescueFile():
            # opening file if known interpreter
            subprocess.call("xdg-open '{}'".format(path), shell=True)
        else:
            # open directory if valid
            subprocess.call("xdg-open '{}'".format(path), shell=True)
            
        

    
def main():
    global GUI
    global app
    sys.setrecursionlimit(10000)
    app = QApplication(sys.argv)
    app.setApplicationName("Rescuer v6")
    app.setOrganizationName("pawliux")
    app.setOrganizationDomain("pawliux.plx")
    GUI = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

