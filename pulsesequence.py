import sys
import numpy as np
from PyQt5.QtWidgets import QMenu,QTableWidgetSelectionRange, QTableWidgetItem, QToolButton, QFileDialog, QLabel,  QLineEdit, QComboBox, QSizePolicy, QTableWidget, QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QFont, QCursor
import csv
import datetime
from PyQt5.QtCore import pyqtSlot, Qt, QPoint
# from functionpool import savedPara
now = datetime.datetime.now()


class MainGui(QMainWindow):
    """This is the main window."""
    def __init__(self):
        super(MainGui, self).__init__()
        self.font = QFont('Sans Serif', 12)
        app.setFont(self.font)
        self.title = 'ODMR Control'
        self.left = 200
        self.top = 50
        self.width = 1000
        self.height = 300
        self.initUI()
        self.columns = 3

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        buttons = PulseInputButtons()
        self.setCentralWidget(buttons)

        self.show()

class PulseInputButtons(QWidget):
    def __init__(self):
        super(PulseInputButtons, self).__init__()
        self.columns = 3
        self.initpulsebuttons()

    def initpulsebuttons(self):
        grid = QGridLayout()
        MW = self.MWbuttons()
        Laser = self.Laserbuttons()
        DAQ = self.DAQbuttons()
        Save = self.SaveLoadButtons()
        Sequence = self.sequence()

        grid.addWidget(MW,0,0)
        grid.addWidget(Laser, 1,0)
        grid.addWidget(DAQ, 2,0)
        grid.addWidget(Save, 3, 0)
        # grid.addWidget(Sequence, 0,1, 8,8)
        buttonbox = QGroupBox()
        buttonbox.setLayout(grid)
        buttonbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        Sequence.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QHBoxLayout()
        layout.addWidget(buttonbox)
        layout.addWidget(Sequence)
        self.setLayout(layout)

    def MWbuttons(self):
        MWgroupbox = QGroupBox()
        MWlayout = QGridLayout()
        MWgroupbox.setTitle('MW')
        MWgroupbox.setLayout(MWlayout)

        self.MWPWlabel = QLabel('PW (dbm)')
        self.MWPWbutton = QLineEdit('4.0')

        self.Triggerlabel = QLabel('Trigger Mode')
        self.Triggermode = QComboBox()
        self.Triggermode.addItem('trig')
        self.Triggermode.addItem('cont')
        self.Triggermode.addItem('gate')
        self.Triggermode.activated[str].connect(lambda x: self.setmode(x))

        self.Samplinglabel = QLabel('Sampling Mode')
        self.Samplingmode = QComboBox()
        self.Samplingmode.addItem('RF')
        self.Samplingmode.addItem('NRZ')
        self.Samplingmode.addItem('NRTZ')
        self.Samplingmode.addItem('RTZ')
        self.Samplingmode.activated[str].connect(lambda x: self.setmode(x))

        # self.Routelabel = QLabel('Sampling Route')
        # self.Samplingroute = QLineEdit()

        MWlayout.addWidget(self.MWPWlabel,0,0)
        MWlayout.addWidget(self.MWPWbutton,0,1)

        MWlayout.addWidget(self.Triggerlabel,1,0)
        MWlayout.addWidget(self.Triggermode,1,1)

        MWlayout.addWidget(self.Samplinglabel,2,0)
        MWlayout.addWidget(self.Samplingmode,2,1)

        # MWlayout.addWidget(Routelabel,3,0)
        # MWlayout.addWidget(Samplingroute,3,1)

        return MWgroupbox

    def Laserbuttons(self):
        Laserbox = QGroupBox()
        Laserlayout = QGridLayout()
        Laserbox.setTitle('Laser')
        Laserbox.setLayout(Laserlayout)

        Laserlabel = QLabel('Laser Power (mW)')
        self.Laserbutton = QLineEdit('300')

        Laserlayout.addWidget(Laserlabel, 0,0)
        Laserlayout.addWidget(self.Laserbutton,0,1)
        return Laserbox

    def DAQbuttons(self):
        DAQbox = QGroupBox()
        DAQlayout = QGridLayout()
        DAQbox.setTitle('DAQ')
        DAQbox.setLayout(DAQlayout)

        Samplelabel = QLabel('N Sample')
        self.Samplebutton = QLineEdit('20000')

        Timeoutlabel = QLabel('Timeout (s)')
        self.Timeoutbutton = QLineEdit('60')

        DAQlayout.addWidget(Samplelabel,0,0)
        DAQlayout.addWidget(self.Samplebutton,0,1)
        DAQlayout.addWidget(Timeoutlabel,1,0)
        DAQlayout.addWidget(self.Timeoutbutton,1,1)

        return DAQbox

    def sequence(self):
        row_names = ['Delay', 'F1_Ph', 'F1_TxGate', 'F1_PhRst', 'F1_UnBlank', 'Acq', 'Acq_phase' 'RX_Blank', 'Ext_Trig', 'CTRL',
                     'Scope_Trig', 'RX_PhRst', 'RX_Phase', 'FHOP', 'AHOP']
        self.rows = len(row_names)
        sequencelayout = QGridLayout()
        sequencebox = QGroupBox()
        sequencebox.setLayout(sequencelayout)
        self.table_widget = QTableWidget(self.rows,self.columns)
        self.addcol_button = QPushButton('Add Column')
        self.addcol_button.clicked.connect(self.onclick_addcolumn)

        sequencelayout.addWidget(self.table_widget,0,0)
        sequencelayout.addWidget(self.addcol_button)
        # table_widget.setHorizontalHeaderLabels()
        self.table_widget.setVerticalHeaderLabels(row_names)



        i=0
        j=0
        while i < self.rows:

            while j < self.columns:
                it = QTableWidgetItem("{}-{}".format(i, j))
                self.table_widget.setItem(i, j, it)
                j=j+1
                # print(j, 'added column')
            j=0
            i =i+1
            # print(i, 'added row')

        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.on_customContextMenuRequested)


        return sequencebox



    def SaveLoadButtons(self):
        SaveLoadbox = QGroupBox()
        SaveLoadlayout = QHBoxLayout()
        SaveLoadbox.setLayout(SaveLoadlayout)

        Savebutton = QPushButton('Save')
        ## by clicking save button, it will also load all the parameters to the device, waiting for execute
        Savebutton.clicked.connect(self.on_click_savetext)
        Savebutton.clicked.connect(self.on_click_loadparameters)
        Loadbutton = QPushButton('Load')
        Loadbutton.clicked.connect(self.on_click_loadtext)

        SaveLoadlayout.addWidget(Savebutton)
        SaveLoadlayout.addWidget(Loadbutton)
        return SaveLoadbox

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        return fileName

    def loadtext(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        fileName = str(fileName)
        print(fileName)
        if not fileName: return
        self.text1, self.text = np.loadtxt(fileName, usecols=(0,1), skiprows=2, unpack=True)
        return self.text1, self.text


    @pyqtSlot()
    def on_click_savetext(self):
        #here we get instrument info for the file saving header

        #this is where we start to format the save files
        datafilename = self.saveFileDialog() #using the file name selected in the file dialog
        file = open(datafilename, 'w', newline='') #begin the writing
        tsv_writer = csv.writer(file, delimiter='\t') #defining the filetype as tab-separated
        tsv_writer.writerow([now.strftime("%Y-%m-%d %H:%M")]) #includes date and time
        tsv_writer.writerow([]) #blank row
        # #writes camera type and grating info
        # # if caps.ulCameraType == 14:
        # #     tsv_writer.writerow(['Camera Type:', 'InGaAs'])
        # # else:
        # #     tsv_writer.writerow(['Camera Type:', 'unknown'])
        # # tsv_writer.writerow(['Camera Serial Number:', iSerialNumber])
        tsv_writer.writerow([])
        tsv_writer.writerow(['MWPW:', float(self.MWPWbutton.text())])
        tsv_writer.writerow(['Trigger mode:', self.Triggermode.currentText()])
        tsv_writer.writerow(['Sampling Mode:', self.Samplingmode.currentText()])
        # tsv_writer.writerow([])
        tsv_writer.writerow(['Laser:', float(self.Laserbutton.text())])
        tsv_writer.writerow([])
        tsv_writer.writerow(['DAQ N sample:', float(self.Samplebutton.text())])
        tsv_writer.writerow(['DAQ Timeout:', float(self.Timeoutbutton.text())])
        tsv_writer.writerow([])
        # TODO: Figure out how to read out table values
        tsv_writer.writerow(['Pulse Sequence', ]) #writes the data
        # datalist = list(self.data)
        # for i in range(len(datalist)):
        #     tsv_writer.writerow([i, self.wavelength[i], datalist[i]])
        file.close()

    def on_click_loadtext(self):
        self.text1, self.text = self.loadtext()

        print('Loaded')

    def on_click_loadparameters(self):
        MW_pw = float(QLineEdit.text(self.MWPWbutton)) ## in dbm
        MW_trig = str(self.Triggermode.currentText())
        MW_samplingmode = str(self.Samplingmode.currentText())
        Laser_pw = float(QLineEdit.text(self.Laserbutton)) ## in mW
        DAQ_Nsample = int(QLineEdit.text(self.Samplebutton))
        DAQ_timeout = float(QLineEdit.text(self.Timeoutbutton)) ## in sec
        loaded = savedPara(MW_pw, MW_trig, MW_samplingmode, Laser_pw, \
                                        DAQ_Nsample, DAQ_timeout)
        loaded.loadParameters()
        loaded.export()

    def onclick_addcolumn(self):
        self.table_widget.insertColumn(0)
        

    def setmode(self, text):
        if text == 'a':
            self.colormap = self.heat
        if text == 'b':
            self.colormap = self.gray
        if text == 'c':
            self.colormap = self.rainbow

    @pyqtSlot(QPoint)
    def on_customContextMenuRequested(self, pos):
        print(pos)
        it = self.table_widget.itemAt(pos)
        if it is None:
            return
        print(it, it.row())
        # # print(it, pos)
        # if it is None: return
        # c = it.column()
        # # item_range = QTableWidgetSelectionRange(0, c, self.table_widget.rowCount()-1 , c)
        # # self.table_widget.setRangeSelected(item_range, True)
        #
        menu = QMenu()
        delete_column_action = menu.addAction("Delete Column")
        add_column_action = menu.addAction('Add Column')
        if it.row() == 0:
            menu.addAction("Row 0")
        action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))
        if action == delete_column_action:
            self.table_widget.removeColumn(it.column())
        if action == add_column_action:
            self.table_widget.insertColumn(it.column())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainGui()
    sys.exit(app.exec_())


#TODO: add functionality to all buttons
#TODO: make sure we have the layout correct (ask Zeppelin what buttons are missing or are formatted wrong, etc.)
#TODO: set up read/write functionality for all boxes
#TODO: set up save/load for all boxes
#TODO: figure out how to make pulse sequence widget responsive to add/remove column/row

#Button on click function added
#TODO: test in real system
