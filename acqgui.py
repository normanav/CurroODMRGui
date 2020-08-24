import sys
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QSizePolicy, QPushButton, QWidget, \
    QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout, QInputDialog, QLineEdit, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import time as time
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QSize


class acqGui(QMainWindow):

    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        super(acqGui, self).__init__()
        self.title = 'threading test'

        self.initacqUI()
        sys.exit(app.exec_())

    def initacqUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        control = plotControl()
        self.setCentralWidget(control)
        self.show()


class plotControl(QWidget):
    def __init__(self):
        super(plotControl, self).__init__()

        self.nstart = 1
        self.nstop = 100
        self.dn = 1
        self.resumelabel = 0

        self.initUI()

    def initUI(self):
        uilayout = QGridLayout()
        self.startbtn = QPushButton('Start Plotting', self)
        self.pausebtn = QPushButton('Pause Plotting', self)
        self.stopbtn = QPushButton('Stop Plotting', self)
        mplplt = WidgetPlot() #initialising the widget plot class
        self.plot = mplplt #naming the widgetplot class
        self.plot.setMinimumSize(QSize(600, 600))

        self.startbtn.clicked.connect(self.on_click_start)
        self.pausebtn.clicked.connect(self.on_click_pause)
        self.stopbtn.clicked.connect(self.on_click_stop)

        uilayout.addWidget(self.startbtn, 0, 0)
        uilayout.addWidget(self.pausebtn, 1, 0)
        uilayout.addWidget(self.stopbtn, 2, 0)
        uilayout.addWidget(mplplt, 0, 1, 5, 5)

        self.setLayout(uilayout)

    @pyqtSlot()
    def on_click_start(self):
        if self.resumelabel == 0:
            data = []
            self.thread = AcquisitionThread(data, self.nstart, self.nstop, self.dn)
            self.thread.start()
            self.thread.signal.connect(self.on_thread_done)
        else:
            data = self.thread.dataQ()
            self.thread = AcquisitionThread(data, self.nstart, self.nstop, self.dn)
            self.thread.start()
            self.thread.signal.connect(self.on_thread_done)
            self.resumelabel = 0



    def on_click_pause(self):
        self.nstart = self.thread.halt()
        self.resumelabel = 1
    
    def on_click_stop(self):
        self.thread.halt()

    def on_thread_done(self, data):
        data = np.array(data) #sets data to a global variable so we can call it in other functions
        datax = np.arange(self.nstart, self.nstart + self.dn* len(data), 1)
        self.plot.plot(datax, data) #uses the QWidget class for plotting



## threading class
class AcquisitionThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, data, nstart, nstop, dn):
        QThread.__init__(self)
        self.data = data
        self.nstart = nstart
        self.ncurrent = nstart
        self.nstop = nstop
        self.dn = dn
        self.condition = 1

    def run(self):
        n_list = np.arange(self.nstart, self.nstop, self.dn)
        for n in n_list:
            self.ncurrent = n
            while self.condition == 1:
                self.data.append(np.random.rand())
                time.sleep(1)
                self.signal.emit(self.data)
            if self.condition != 1:
                break
                

    
    def halt(self):
        self.condition = 0
        return self.ncurrent

    def dataQ(self):
        return self.data

## plotting class
class PlotCanvas(FigureCanvas): #this creates a matplotlib canvas and defines some plotting aspects

    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, x, data):
        self.axes.plot(x, data, 'b.')
        self.axes.set_title('Title')
        self.draw()

    def plotfit(self, x, fit): #this is here to make sure the plot doesn't clear when trying to plot a fitting function
        # on top of the data
        self.axes.plot(x, fit, 'bo')
        self.draw()


class WidgetPlot(QWidget): #this converts the matplotlib canvas into a qt5 widget so we can implement it in the qt
    # framework laid out above
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)


    def plot(self, x, data):
        self.canvas.axes.clear() #it is important to clear out the plot first or everything just gets plotted on top of
        # each other and it becomes useless
        self.canvas.plot(x, data)

    def plotfit(self, x, fit):
        self.canvas.plotfit(x, fit)

acqGui()