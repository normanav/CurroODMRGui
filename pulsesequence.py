import sys
import numpy as np
from PyQt5.QtWidgets import QMenu, QTableWidgetItem, QFileDialog, QLabel,  QLineEdit, QComboBox, QSizePolicy, QTableWidget, QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QFont, QCursor
import csv
import datetime
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QDir
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
        self.width = 1215
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        buttons = PulseInputButtons()
        self.setCentralWidget(buttons)

        self.show()

class PulseInputButtons(QWidget):
    def __init__(self):
        super(PulseInputButtons, self).__init__()
        self.initpulsebuttons()

    def initpulsebuttons(self):
        grid = QGridLayout()
        MW = self.MWbuttons()
        Laser = self.Laserbuttons()
        DAQ = self.DAQbuttons()
        Save = self.SaveLoadButtons()
        Sequence = self.sequence()
        Times = self.timevars()

        grid.addWidget(MW,0,0)
        grid.addWidget(Laser, 1,0)
        grid.addWidget(DAQ, 2,0)
        grid.addWidget(Save, 3, 0)

        # grid.addWidget(Sequence, 0,1, 8,8)
        buttonbox = QGroupBox()
        buttonbox.setLayout(grid)
        buttonbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        Sequence.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        buttonbox.setTitle('Instrument Parameters')
        layout = QGridLayout()
        layout.addWidget(buttonbox, 0,0)
        layout.addWidget(Sequence, 0, 1, 1, 3)
        layout.addWidget(Times, 0, 4)
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
        DAQbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        DAQlayout.addWidget(Samplelabel,0,0)
        DAQlayout.addWidget(self.Samplebutton,0,1)
        DAQlayout.addWidget(Timeoutlabel,1,0)
        DAQlayout.addWidget(self.Timeoutbutton,1,1)

        return DAQbox

    def sequence(self):
        self.col_names = ['AOM', 'MW', 'DAQ', 'Start Trigger']
        self.row_name = ['Start Time', 'Pulse Duration', 'Instruction Code', 'Instruction Data']
        self.row_names = self.row_name*3
        self.cols = len(self.col_names)
        self.rows = len(self.row_names)
        self.seqarray = np.zeros((self.rows, self.cols))
        self.seqarray[:] = np.nan
        self.instructioncode = [0]*(int(self.rows/4))


        sequencelayout = QGridLayout()
        sequencebox = QGroupBox()
        sequencebox.setLayout(sequencelayout)

        sequencebox.setTitle('Pulse Sequence Designer')
        self.table_widget = QTableWidget(self.rows, self.cols)
        sequencelayout.addWidget(self.table_widget,0,0, 1, 2)

        self.table_widget.setHorizontalHeaderLabels(self.col_names)
        self.table_widget.setVerticalHeaderLabels(self.row_names)

        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.on_customContextMenuRequested)
        for i in range(np.size(self.seqarray, 0)):
            for j in range(np.size(self.seqarray,1)):
                if np.isnan(self.seqarray[i][j]):
                    self.table_widget.setItem(i,j,  QTableWidgetItem('None'))
                else:
                    self.table_widget.setItem(i,j, QTableWidgetItem(str(self.seqarray[i][j])))
        self.table_widget.cellChanged.connect(self.onitemchanged)


        self.saveseqbtn = QPushButton('Save Sequence')
        self.loadseqbtn = QPushButton('Load Sequence')
        sequencelayout.addWidget(self.saveseqbtn, 1, 0)
        sequencelayout.addWidget(self.loadseqbtn, 1, 1)
        self.saveseqbtn.clicked.connect(self.onclick_saveseq)

        return sequencebox

    def timevars(self):
        box = QGroupBox()
        lay = QGridLayout()
        box.setLayout(lay)
        box.setTitle('Time Variables')

        T1box, self.T1, self.T1units = self.timebox('T1')
        self.T1.setText('40')
        index = self.T1units.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.T1units.setCurrentIndex(index)

        Cyclebox, self.Cycle, self.Cycleunits = self.timebox('Cycle')
        self.Cycle.setText(str(10/3 * 5))
        index = self.Cycleunits.findText('ns', Qt.MatchFixedString)
        if index >= 0:
            self.Cycleunits.setCurrentIndex(index)

        Trigbox, self.T_Trigger, self.Trigunits = self.timebox('T_Trigger')
        self.T_Trigger.setText('1')
        index = self.Trigunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.Trigunits.setCurrentIndex(index)

        LasDbox, self.Laser_D, self.LasDunits = self.timebox('Laser_D')
        self.Laser_D.setText('300')
        index = self.LasDunits.findText('ns', Qt.MatchFixedString)
        if index >= 0:
            self.LasDunits.setCurrentIndex(index)

        LasRbox, self.Laser_R, self.LasRunits = self.timebox('Laser_R')
        self.Laser_R.setText('200')
        index = self.LasRunits.findText('ns', Qt.MatchFixedString)
        if index >= 0:
            self.LasRunits.setCurrentIndex(index)

        MWDbox, self.MW_D, self.MWDunits = self.timebox('MW_D')
        self.MW_D.setText('1')
        index = self.MWDunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.MWDunits.setCurrentIndex(index)

        readbox, self.readout_D, self.readunits = self.timebox('Readout_D')
        self.readout_D.setText('1')
        index = self.readunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.readunits.setCurrentIndex(index)

        t90box, self.t_90, self.t90units = self.timebox('T_90')
        self.t_90.setText('50')
        index = self.t90units.findText('ns', Qt.MatchFixedString)
        if index >= 0:
            self.t90units.setCurrentIndex(index)

        halftaubox, self.halftau, self.halftauunits = self.timebox('T_HalfTau')
        self.halftau.setText('80')
        index = self.halftauunits.findText('ns', Qt.MatchFixedString)
        if index >= 0:
            self.halftauunits.setCurrentIndex(index)

        tdelaybox, self.t_delay, self.tdelayunits = self.timebox('T_delay')
        self.t_delay.setText('1')
        index = self.tdelayunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.tdelayunits.setCurrentIndex(index)

        waitbox, self.t_wait, self.waitunits = self.timebox('T_wait')
        self.t_wait.setText('1')
        index = self.waitunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.waitunits.setCurrentIndex(index)

        startbox, self.start_d, self.startunits = self.timebox('Start_D')
        self.start_d.setText('1')
        index = self.startunits.findText('us', Qt.MatchFixedString)
        if index >= 0:
            self.startunits.setCurrentIndex(index)


        lay.addWidget(T1box, 0, 0)
        lay.addWidget(Cyclebox, 0, 1)
        lay.addWidget(Trigbox, 1, 0)
        lay.addWidget(LasDbox, 1, 1)
        lay.addWidget(LasRbox, 2, 0)
        lay.addWidget(MWDbox, 2, 1)
        lay.addWidget(t90box, 3, 0)
        lay.addWidget(halftaubox, 3, 1)
        lay.addWidget(tdelaybox, 4, 0)
        lay.addWidget(waitbox, 4, 1)
        lay.addWidget(readbox, 5, 0)
        lay.addWidget(startbox, 5, 1)

        box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        return box

    def timebox(self, timename):

        combo = QComboBox()
        combo.addItem('ps')
        combo.addItem('ns')
        combo.addItem('us')
        combo.addItem('ms')
        combo.addItem('s')

        box = QGroupBox()
        lay = QHBoxLayout()
        box.setTitle(timename)
        timeedit = QLineEdit()
        timeedit.setFixedWidth(50)
        unitscombo = combo
        box.setLayout(lay)
        lay.addWidget(timeedit)
        lay.addWidget(unitscombo)

        return box, timeedit, unitscombo

    def SaveLoadButtons(self):
        SaveLoadbox = QGroupBox()
        SaveLoadlayout = QHBoxLayout()
        SaveLoadbox.setLayout(SaveLoadlayout)

        Savebutton = QPushButton('Save Params \n to File')
        ## by clicking save button, it will also load all the parameters to the device, waiting for execute
        Savebutton.clicked.connect(self.on_click_savetext)
        Savebutton.clicked.connect(self.on_click_loadparameters)
        Loadbutton = QPushButton('Load Params \n From File')
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
        # loaded = savedPara(MW_pw, MW_trig, MW_samplingmode, Laser_pw, \
        #                                 DAQ_Nsample, DAQ_timeout)
        # loaded.loadParameters()
        # loaded.export()

        # for i in range(self.rows):
        #     value = QTableWidgetItem("__________".format(i, 0))
        #     self.table_widget.setItem(i, 0, value)
        # return


    def onclick_saveseq(self):
        datafilename = self.saveFileDialog()
        file = open(datafilename, 'w', newline='') #begin the writing
        tsv_writer = csv.writer(file, delimiter='\t') #defining the filetype as tab-separated
        tsv_writer.writerow([now.strftime("%Y-%m-%d %H:%M")]) #includes date and time
        tsv_writer.writerow([]) #blank row
        tsv_writer.writerow(['Rows', '',*self.col_names])
        # tsv_writer.writerow(['\t', self.col_names[0]+'\t', self.col_names[1]+'\t', self.col_names[2]+'\t', self.col_names[3]+'\t'])
        for i in range(self.rows):
            tsv_writer.writerow([self.row_names[i], self.seqarray[i][0], self.seqarray[i][1], self.seqarray[i][2], self.seqarray[i][3]])
        print('Saved!')


        file.close()


    def setmode(self, text):
        if text == 'a':
            self.colormap = self.heat
        if text == 'b':
            self.colormap = self.gray
        if text == 'c':
            self.colormap = self.rainbow


    def onitemchanged(self):
        col = self.table_widget.currentColumn()
        row = self.table_widget.currentRow()
        text = self.table_widget.item(row, col).text()

        value = None

        try:
            value = float(text)
        except:
            pass


        if value is None:
            try:
                value = getattr(self, text).text()
            except:
                pass
        #
        if value is not None:
            self.seqarray[row, col] = value

        print(self.seqarray)

    @pyqtSlot(QPoint)
    def on_customContextMenuRequested(self, pos):
        it = self.table_widget.itemAt(pos)
        if it is None:
            return
        #
        menu = QMenu()
        newrow = [-999, -999, -999, -999]
        if it.row() % 4 == 0:
            if it.column() == 0:
                add_pulse_action = menu.addAction('Add Pulse')
                delete_pulse_action = menu.addAction('Delete Pulse')
                action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))
                if action == add_pulse_action:
                    self.row_names = self.row_names + self.row_name
                    self.table_widget.insertRow(it.row()+4)
                    self.table_widget.insertRow(it.row()+4)
                    self.table_widget.insertRow(it.row()+4)
                    self.table_widget.insertRow(it.row()+4)
                    self.rows = self.rows + 4
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    self.seqarray = np.insert(self.seqarray, it.row()+4, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+4, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+4, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+4, newrow, axis=0)
                    return

                if action == delete_pulse_action:
                    self.table_widget.removeRow(it.row()+1)
                    self.seqarray = np.delete(self.seqarray, it.row(), axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row(), axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row(), axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row(), axis=0)

                    self.table_widget.removeRow(it.row()+1)
                    self.table_widget.removeRow(it.row()+1)
                    self.table_widget.removeRow(it.row())
                    self.row_names = self.row_names[:-4]
                    self.rows = self.rows - 4
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    return

        if it.row() % 4 == 1:
            if it.column() == 0:
                add_pulse_action = menu.addAction('Add Pulse')
                delete_pulse_action = menu.addAction('Delete Pulse')
                divider = menu.addAction('----------')
                T1_action = menu.addAction('T1')
                action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))

                if action == add_pulse_action:
                    self.row_names = self.row_names + self.row_name
                    self.table_widget.insertRow(it.row()+3)
                    self.table_widget.insertRow(it.row()+3)
                    self.table_widget.insertRow(it.row()+3)
                    self.table_widget.insertRow(it.row()+3)
                    self.rows = self.rows + 4
                    self.seqarray = np.insert(self.seqarray, it.row()+3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row()+3, newrow, axis=0)
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    return

                if action == delete_pulse_action:
                    self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)

                    self.table_widget.removeRow(it.row()-1)
                    self.table_widget.removeRow(it.row()+1)
                    self.table_widget.removeRow(it.row()+1)
                    self.table_widget.removeRow(it.row())
                    self.row_names = self.row_names[:-4]
                    self.rows = self.rows - 4
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    return

                if action ==T1_action:
                    value = QTableWidgetItem('T1'.format(it.row(), it.column()))
                    self.table_widget.setItem(it.row(), it.column(), value)
                    return

            else:
                add_pulse_action = menu.addAction('Add Pulse')
                delete_pulse_action = menu.addAction('Delete Pulse')
                divider = menu.addAction('----------')
                Ttrig_action = menu.addAction('T1')
                action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))

                if action == add_pulse_action:
                    self.row_names = self.row_names + self.row_name
                    self.table_widget.insertRow(it.row() + 3)
                    self.table_widget.insertRow(it.row() + 3)
                    self.table_widget.insertRow(it.row() + 3)
                    self.table_widget.insertRow(it.row() + 3)
                    self.rows = self.rows + 4
                    self.seqarray = np.insert(self.seqarray, it.row() + 3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row() + 3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row() + 3, newrow, axis=0)
                    self.seqarray = np.insert(self.seqarray, it.row() + 3, newrow, axis=0)
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    return

                if action == delete_pulse_action:
                    self.seqarray = np.delete(self.seqarray, it.row() - 1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row() - 1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row() - 1, axis=0)
                    self.seqarray = np.delete(self.seqarray, it.row() - 1, axis=0)

                    self.table_widget.removeRow(it.row() - 1)
                    self.table_widget.removeRow(it.row() + 1)
                    self.table_widget.removeRow(it.row() + 1)
                    self.table_widget.removeRow(it.row())
                    self.row_names = self.row_names[:-4]
                    self.rows = self.rows - 4
                    self.table_widget.setVerticalHeaderLabels(self.row_names)
                    return

                if action == Ttrig_action:
                    value = QTableWidgetItem('T_Trigger'.format(it.row(), it.column()))
                    self.table_widget.setItem(it.row(), it.column(), value)
                    return

        if it.row() % 4 == 2:
            action0 = menu.addAction('Continue')
            action1 = menu.addAction('Stop')
            action2 = menu.addAction('Loop')
            action3 = menu.addAction('End Loop')
            action4 = menu.addAction('')
            add_pulse_action = menu.addAction('Add Pulse')
            delete_pulse_action = menu.addAction('Delete Pulse')

            action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))

            if action == add_pulse_action:
                self.row_names = self.row_names + self.row_name
                self.table_widget.insertRow(it.row() + 2)
                self.table_widget.insertRow(it.row() + 2)
                self.table_widget.insertRow(it.row() + 2)
                self.table_widget.insertRow(it.row() + 2)
                self.rows = self.rows + 4
                self.table_widget.setVerticalHeaderLabels(self.row_names)
                self.seqarray = np.insert(self.seqarray, it.row() + 2, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 2, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 2, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 2, newrow, axis=0)
                return

            if action == delete_pulse_action:
                self.seqarray = np.delete(self.seqarray, it.row()-2, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-2, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-2, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-2, axis=0)

                self.table_widget.removeRow(it.row() - 2)
                self.table_widget.removeRow(it.row() - 1)
                self.table_widget.removeRow(it.row() + 1)
                self.table_widget.removeRow(it.row())
                self.row_names = self.row_names[:-4]
                self.rows = self.rows - 4
                self.table_widget.setVerticalHeaderLabels(self.row_names)
                return

            if action == action0:
                value = QTableWidgetItem('Continue'.format(it.row(), it.column()))
                self.table_widget.setItem(it.row(), it.column(), value)
                return

            if action == action1:
                value = QTableWidgetItem('Stop'.format(it.row(), it.column()))
                self.table_widget.setItem(it.row(), it.column(), value)

                return

        if it.row() % 4 == 3:
            add_pulse_action = menu.addAction('Add Pulse')
            delete_pulse_action = menu.addAction('Delete Pulse')
            action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))

            if action == add_pulse_action:
                self.row_names = self.row_names + self.row_name
                self.table_widget.insertRow(it.row() + 1)
                self.table_widget.insertRow(it.row() + 1)
                self.table_widget.insertRow(it.row() + 1)
                self.table_widget.insertRow(it.row() + 1)
                self.rows = self.rows + 4
                self.table_widget.setVerticalHeaderLabels(self.row_names)
                self.seqarray = np.insert(self.seqarray, it.row() + 1, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 1, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 1, newrow, axis=0)
                self.seqarray = np.insert(self.seqarray, it.row() + 1, newrow, axis=0)
                return

            if action == delete_pulse_action:
                self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)
                self.seqarray = np.delete(self.seqarray, it.row()-1, axis=0)

                self.table_widget.removeRow(it.row() - 3)
                self.table_widget.removeRow(it.row() - 2)
                self.table_widget.removeRow(it.row() - 1)
                self.table_widget.removeRow(it.row())
                self.row_names = self.row_names[:-4]
                self.rows = self.rows - 4
                self.table_widget.setVerticalHeaderLabels(self.row_names)
                return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MainGui()
    sys.exit(app.exec_())

#TODO: implement instruction type list tracking and inputting into
#TODO figure out how to convert sums of times into values
#TODO: finish menu options for instruction types

#TODO: test in real system