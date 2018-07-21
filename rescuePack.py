from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import os
import csv
from enum import Enum

class ExtensionFile(Enum):
    GRAPHICS = 1,
    VIDEO = 2,
    DOCUMENT = 3,
    AUDIO = 4,
    OTHER = 5

class NewExtensionDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(NewExtensionDialog, self).__init__(*args, **kwargs)
        windowSize = (200,100)
        screenSize = QDesktopWidget().availableGeometry()
        # center window
        self.setGeometry(screenSize.width()/2 - windowSize[0]/2, screenSize.height()/2 - windowSize[1]//2, windowSize[0], windowSize[1])

        layout = QVBoxLayout()

        QBtn = (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.acceptClick)
        self.buttonBox.rejected.connect(self.reject)

        self.extensionEL = QLineEdit()
        self.extensionEL.setToolTip("Write extension without any dots or other characters")
        layout.addWidget(self.extensionEL)

        self.extensionLibrary = QComboBox()
        self.extensionLibrary.setToolTip("Choose an appopriate library to add a new extension")
        self.extensionLibrary.addItem("Audio file library", QVariant("audio.ext"))
        self.extensionLibrary.addItem("Document file library", QVariant("document.ext"))
        self.extensionLibrary.addItem("Graphics file library", QVariant("graphics.ext"))
        self.extensionLibrary.addItem("Video file library", QVariant("video.ext"))
        self.extensionLibrary.addItem("Other file library", QVariant("other.ext"))
        
        layout.addWidget(self.extensionLibrary)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def acceptClick(self):
        # validate extension edit line
        if self.extensionEL.text() is None or self.extensionEL.text() == "":
            # show error message here
            self.showErrorMessage("Invalid extension")
            # self.reject()
            return
        
        # choose library file to save to
        file_name = self.extensionLibrary.currentData()
        file_path = os.path.join('Extensions', file_name)

        with (open(file_path, "a")) as outp:
            csv_writer = csv.writer(outp)
            line = (self.extensionEL.text(), 1)
            csv_writer.writerow(line)

        self.accept()

    def showErrorMessage(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

class ExtensionDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(ExtensionDialog, self).__init__(*args, **kwargs)

        windowSize = (600,600)
        screenSize = QDesktopWidget().availableGeometry()
        # center window
        self.setGeometry(screenSize.width()/2 - windowSize[0]/2, 50, windowSize[0], windowSize[1])

        # holders
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.main_grid = QGridLayout()

        self.createLayout()

        layout.addLayout(self.main_grid)

        self.setLayout(layout)

    def createLayout(self):
        self.row = 1 ##
        self.graphics_dict = {}
        self.video_dict = {}
        self.audio_dict = {}
        self.document_dict = {}
        self.other_dict = {}

        QBtn = (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.acceptClick)
        self.buttonBox.rejected.connect(self.rejectClick)
        
        
        
        # widgets
        title = QLabel("File types to rescue")
        font = title.font()
        font.setPointSize(14)
        title.setFont(font)
        title.setAlignment(Qt.AlignHCenter)
        self.main_grid.addWidget(title, self.row, 1, 1, 10, Qt.AlignHCenter)
        self.row += 1 # ++

        # generate grapchics file type checkboxes
        self.generateCheckboxes(self.main_grid, ExtensionFile.GRAPHICS, self.graphics_dict)
        # generate video file type checkboxes
        self.generateCheckboxes(self.main_grid, ExtensionFile.VIDEO, self.video_dict)
        # generate document file type checkboxes
        self.generateCheckboxes(self.main_grid, ExtensionFile.DOCUMENT, self.document_dict)
        # generate audio file type checkboxes
        self.generateCheckboxes(self.main_grid, ExtensionFile.AUDIO, self.audio_dict)
        # generate other file type checkboxes
        self.generateCheckboxes(self.main_grid, ExtensionFile.OTHER, self.other_dict)        

        # add new extension button
        new_ext_btn = QPushButton("Add new extension")
        new_ext_btn.setMinimumSize(200, 25)
        new_ext_btn.clicked.connect(self.showNewExtensionDialog)
        self.main_grid.addWidget(new_ext_btn, self.row, 1, 1, 10, Qt.AlignHCenter)
        self.row += 1 # ++

        # add buttons
        self.main_grid.addWidget(self.buttonBox, self.row, 1, 1, 10, Qt.AlignRight)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

    @staticmethod
    def generateListOfExtentionsToRescue():
        filenames = ('graphics.ext', 'video.ext', 'document.ext', 'audio.ext', 'other.ext')
        EXTENSIONS = []
        for file_name in filenames:
            file_path = os.path.join('Extensions', file_name)
            with (open(file_path, 'r')) as inp:
                csv_reader = csv.reader(inp, delimiter=',')

                for line in csv_reader:
                    extension = str(line[0]).strip("'")
                    enabled = bool(int(line[1]))
                    if enabled:
                        EXTENSIONS.append(extension)

        return list(EXTENSIONS)

    def generateCheckboxes(self, main_grid, enumerator, output_dict):
        group_box = QGroupBox()
        current_group_grid = QGridLayout()
        
        if enumerator == ExtensionFile.GRAPHICS:
            file_name = 'graphics.ext'
            group_box.setTitle("Graphics files:")
        elif enumerator == ExtensionFile.VIDEO:
            file_name = 'video.ext'
            group_box.setTitle("Video files:")
        elif enumerator == ExtensionFile.DOCUMENT:
            file_name = 'document.ext'
            group_box.setTitle("Document files:")
        elif enumerator == ExtensionFile.AUDIO:
            file_name = 'audio.ext'
            group_box.setTitle("Audio files:")
        elif enumerator == ExtensionFile.OTHER:
            file_name = 'other.ext'
            group_box.setTitle("Other files:")

        file_path = os.path.join('Extensions', file_name)
        row = 1
        with (open(file_path, 'r')) as inp:
            csv_reader = csv.reader(inp, delimiter=',')
            column = 0
            for line in csv_reader:
                extension = str(line[0]).strip("'")
                
                enabled = Qt.Checked if bool(int(line[1])) else Qt.Unchecked
                checkbox = QCheckBox(extension)
                checkbox.setCheckState(enabled)
                
                output_dict[extension] = checkbox
                output_dict[extension].stateChanged.connect(lambda state, output_dict=output_dict, checkbox=checkbox: self.checkboxClick(state, output_dict, checkbox))
                current_group_grid.addWidget(checkbox, row, column+1, 1, 1)
                column = (column + 1)%10
                row = row+ 1 if column == 0 else row
        
        select_all_checkbox = QCheckBox(r"Select/Deselect all")
        select_all_checkbox.setCheckState(Qt.Checked)
        select_all_checkbox.stateChanged.connect(lambda state, output_dict=output_dict: self.selectAllInLibrary(state, output_dict))
        row += 1
        current_group_grid.addWidget(select_all_checkbox, row, 1, 1, 10, Qt.AlignRight)

        group_box.setLayout(current_group_grid)
        main_grid.addWidget(group_box, self.row, 1, 1, 10)
        self.row += 1 # ++

    def checkboxClick(self, state, output_dict, checkbox):
        # if state == Qt.Unchecked:
        #     output_dict[checkbox.text()] = False
        # else:
        #     output_dict[checkbox.text()] = True
        print(checkbox.text(), output_dict[checkbox.text()].checkState())

    def selectAllInLibrary(self, state, output_dict):
        for key in output_dict:
            checkbox = output_dict[key]
            checkbox.setCheckState(state)

    def acceptClick(self):
        # saving graphics extensions
        with (open(os.path.join("Extensions", "graphics.ext"), "w")) as outp:
            csv_writer = csv.writer(outp, delimiter=",")
            for key in self.graphics_dict:
                checkbox = self.graphics_dict[key]
                state = 1 if checkbox.checkState() == Qt.Checked else 0
                        
                line = ("'%s'" % key, state)
                csv_writer.writerow(line)

        # saving video extensions
        with (open(os.path.join("Extensions", "video.ext"), "w")) as outp:
            csv_writer = csv.writer(outp, delimiter=",")
            for key in self.video_dict:
                checkbox = self.video_dict[key]
                state = 1 if checkbox.checkState() == Qt.Checked else 0
                        
                line = ("'%s'" % key, state)
                csv_writer.writerow(line)

        # saving audio extensions
        with (open(os.path.join("Extensions", "audio.ext"), "w")) as outp:
            csv_writer = csv.writer(outp, delimiter=",")
            for key in self.audio_dict:
                checkbox = self.audio_dict[key]
                state = 1 if checkbox.checkState() == Qt.Checked else 0
                        
                line = ("'%s'" % key, state)
                csv_writer.writerow(line)

        # saving document extensions
        with (open(os.path.join("Extensions", "document.ext"), "w")) as outp:
            csv_writer = csv.writer(outp, delimiter=",")
            for key in self.document_dict:
                checkbox = self.document_dict[key]
                state = 1 if checkbox.checkState() == Qt.Checked else 0
                        
                line = ("%s" % key, state)
                csv_writer.writerow(line)

        # saving other extensions
        with (open(os.path.join("Extensions", "other.ext"), "w")) as outp:
            csv_writer = csv.writer(outp, delimiter=",")
            for key in self.other_dict:
                checkbox = self.other_dict[key]
                state = 1 if checkbox.checkState() == Qt.Checked else 0
                        
                line = ("%s" % key, state)
                csv_writer.writerow(line)
        self.accept()
       

    def rejectClick(self):
        print("rejected changes")
        self.reject()

    def showNewExtensionDialog(self):
        dlg = NewExtensionDialog()
        dlg.accepted.connect(self.refreshExtensionWindow)
        dlg.exec_()
    
    def refreshExtensionWindow(self):
        self.clearLayout(self.main_grid)
        self.createLayout()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = ExtensionDialog()
    dlg.exec_()
    app.exec_()