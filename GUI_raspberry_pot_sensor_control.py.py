
import datetime
import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import functools
import numpy as np
import random as rd
import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import time
import threading
import explorerhat

N = 0.6
x_tot = 1000
xlim = 20
savedel = 10.0
tps = 20.

def setCustomSize(x, width, height):
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMinimumSize(QtCore.QSize(width, height))
    x.setMaximumSize(QtCore.QSize(width, height))

''''''

class CustomMainWindow(QtGui.QMainWindow):
    

    def __init__(self):

        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle("Visualiseur de tension")
        
        # bold font
        myFont=QtGui.QFont()
        myFont.setBold(True)

        # Create the frame of the window
        self.FRAME_A = QtGui.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210,210,235,255).name())
        self.LAYOUT_A = QtGui.QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)
        
        ### Place titre "Parametres visualisation"
        self.titreVisu=QtGui.QLabel()
        self.titreVisu.setFont(myFont)
        self.titreVisu.setText("Parametres visualisation de la tension")
        self.titreVisu.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.titreVisu, 0, 0, 1, 1)
        
        
        ### Set labels of every line
        self.delayLabel = QtGui.QLabel()
        self.delayLabel.setText("Delai entre acquisition (en sec)")
        self.LAYOUT_A.addWidget(self.delayLabel, 2, 0, 1, 1)
        
        self.nbxLabel = QtGui.QLabel()
        self.nbxLabel.setText("Durée à visualiser")
        self.LAYOUT_A.addWidget(self.nbxLabel, 3, 0, 1, 1)
        
        self.savedelLabel = QtGui.QLabel()
        self.savedelLabel.setText("Intervalle de sauvegarde (en sec)")
        self.LAYOUT_A.addWidget(self.savedelLabel, 4, 0, 1, 1)
        
        self.ylimLabel = QtGui.QLabel()
        self.ylimLabel.setText("Echelle de tension (en Volt) :")
        self.LAYOUT_A.addWidget(self.ylimLabel, 5, 0, 1, 2)
        self.yminLabel = QtGui.QLabel()
        self.yminLabel.setText("U minimum :")
        self.yminLabel.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.yminLabel, 6, 0, 1, 1)
        self.ymaxLabel = QtGui.QLabel()
        self.ymaxLabel.setText("U maximum :")
        self.ymaxLabel.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.ymaxLabel, 7, 0, 1, 1)
        
        #self.autoscaleLabel = QtGui.QLabel()
        #self.autoscaleLabel.setText("Autoscale")
        #self.LAYOUT_A.addWidget(self.autoscaleLabel, 8, 0, 1, 1)
        
        
        ### Place delay LineEdit
        self.delayBtn = QtGui.QLineEdit()
        #self.delayBtn.setValidator(QDoubleValidator(0.0,60.0,3))
        self.delayBtn.setMaxLength(4)
        self.delayBtn.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.delayBtn, 2, 1, 1, 1)
        
        ### Place nbx LineEdit
        self.nbxBtn = QtGui.QLineEdit()
        self.nbxBtn.setMaxLength(4)
        self.nbxBtn.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.nbxBtn, 3, 1, 1, 1)
        
        ### Place nbx LineEdit
        self.saveDel = QtGui.QLineEdit()
        self.saveDel.setMaxLength(4)
        self.saveDel.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.saveDel, 4, 1, 1, 1)
        
        ### Place set_ylim LineEdit
        self.set_ymin = QtGui.QLineEdit()
        self.set_ymin.setMaxLength(4)
        self.set_ymin.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.set_ymin, 6, 1, 1, 1)
        self.set_ymax = QtGui.QLineEdit()
        self.set_ymax.setMaxLength(4)
        self.set_ymax.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.set_ymax, 7, 1, 1, 1)
        
        ### Place the autoscale checkbox
        self.autoscale = QtGui.QCheckBox('Autoscale')
        self.autoscale.stateChanged.connect(self._set_autoscale)
        self.autoscale.toggle()
        self.LAYOUT_A.addWidget(self.autoscale, 8, 1, 1, 1)
        
        ### Place the set_parameters btn
        self.set_para = QtGui.QPushButton(text="Appliquer les parametres")
        self.set_para.setObjectName("connect")
        self.connect(self.set_para, QtCore.SIGNAL("clicked()"),self._set_para)
        self.LAYOUT_A.addWidget(self.set_para, 10, 0, 1, 2)
        
        ### Place the freeze btn
        self.freeze = QtGui.QPushButton(text="freeze")
        self.freeze.setObjectName("connect")
        self.connect(self.freeze, QtCore.SIGNAL("clicked()"),self._freeze)
        self.LAYOUT_A.addWidget(self.freeze, 11, 0, 1, 2)
        
        ### place blanc
        self.blank=QtGui.QLabel()
        self.blank.setText("")
        self.blank.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.blank, 13, 0, 1, 1)
        
        ### Place titre "Parametres rampe de tension"
        self.titreRampe=QtGui.QLabel()
        self.titreRampe.setFont(myFont)
        self.titreRampe.setText("Parametres rampe de tension pour le lock")
        self.titreRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.titreRampe, 14, 0, 1, 1)
        
        ### Place min rampe de tension
        self.minRampe = QtGui.QLineEdit()
        self.minRampe.setMaxLength(4)
        self.minRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.minRampe, 15, 1, 1, 1)
        self.LabminRampe = QtGui.QLabel()
        self.LabminRampe.setText("Min rampe U :")
        self.LabminRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.LabminRampe, 15, 0, 1, 1)
        
        ### Place max rampe de tension
        self.maxRampe = QtGui.QLineEdit()
        self.maxRampe.setMaxLength(4)
        self.maxRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.maxRampe, 16, 1, 1, 1)
        self.LabmaxRampe = QtGui.QLabel()
        self.LabmaxRampe.setText("Min rampe U :")
        self.LabmaxRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.LabmaxRampe, 16, 0, 1, 1)
        
        ### Place min rampe de tension
        self.minRampe = QtGui.QLineEdit()
        self.minRampe.setMaxLength(4)
        self.minRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.minRampe, 15, 1, 1, 1)
        self.LabminRampe = QtGui.QLabel()
        self.LabminRampe.setText("Min rampe U :")
        self.LabminRampe.setAlignment(QtCore.Qt.AlignRight)
        self.LAYOUT_A.addWidget(self.LabminRampe, 15, 0, 1, 1)
        
        
        
        
        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, 0, 2, 12, 1)

        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name = 'myDataLoop', target = dataSendLoop, daemon = True, args = (self.addData_callbackFunc,))
        myDataLoop.start()

        self.show()

    ''''''
    def _set_autoscale(self):
        
        #if self.autoscale.isChecked():
        self.myFig._autosc()
        #else:
        #    self.myFig.ax1.set_ylim(float(self.set_ymin.text()), float(self.set_ymax.text()))
        
    def _freeze(self):
        self.myFig._stop()
        
    
    def _set_para(self):
        """
        applique les parametres entres dans le gui
        """
        print("usr delay=", self.delayBtn.text())
        print("usr nb_x=", self.nbxBtn.text())
        global N
        global xlim
        global savedel
        global tps
        if self.saveDel.text() != '':
            savedel = round(float(self.saveDel.text()), 3)
        if self.delayBtn.text() != '':
            N = round(float(self.delayBtn.text()), 3)
            self.myFig.event_source.interval=N*10**3
        if '' != self.nbxBtn.text():
            tps = float(self.nbxBtn.text())
            xlim = int(float(self.nbxBtn.text())/N + 1)
        if (self.set_ymin.text(), self.set_ymax.text()) != ('',''):
            self.myFig.ax1.set_ylim(float(self.set_ymin.text()), float(self.set_ymax.text()))
        #self.myFig.event_source.interval=N*10**3
        self.myFig.draw()

    ''''''

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)



''' End Class '''


class CustomFigCanvas(FigureCanvas, TimedAnimation):

    def __init__(self):

        self.addedData = []

        # The data
        self.n = np.zeros(x_tot) - N
        self.y = (self.n * 0.0) # set values on y axis

        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.grid(True)

        # Create axis and lines on the fig
        
        self.ax1.set_xlabel('time')
        self.ax1.set_ylabel('tension en volt')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.plot(self.n, self.y, '-')
        
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, xlim - 1)
        self.ax1.set_ylim(0.45, 0.52)
        
        
        saveData = threading.Thread(target = self.saveDataLoop, daemon =True)
        saveData.start()

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = N*10**3, blit = True)
        
        
    def _autosc(self):
        
        pass
        """
        Umax = 0
        Umin = 0
        
        while True:
            if np.abs(Umax-np.max(self.y)) > Umax*0.2:
                      Umax = np.max(self.y)
            if np.abs(Umin-np.min(self.y)) < Umin*0.2:
                      Umin = np.min(self.y)
                      
            self.ax1.set_ylim((1-0.3)*Umin, (1+0.3)*Umax)
            time.sleep(N)
        """
    def saveDataLoop(self):
        while True:
            now = str(datetime.datetime.now())
            f = open("textfile_year_month.txt", "a+")
            f.write(str(self.n[-1]) + " " + now[11:22] + " " + str(self.y[-1]) + "\n")
            f.close()
            time.sleep(savedel)
        
        
    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)


    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedData) > 0):
            #now = str(datetime.datetime.now())
            self.y = np.roll(self.y, -1)
            self.n = np.roll(self.n, -1)
            self.n[-1]= round(self.n[-2] + N, 3)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])
            
        self.ax1.set_xlim(self.n[-1] - tps ,self.n[-1] + margin)

        self.line1.set_data(self.n[self.n>=self.n[-1] - tps], self.y[self.n>=self.n[-1] - tps])
        self.line1_tail.set_data(np.append(self.n[-10:- 1], self.n[-1]), np.append(self.y[-10:-1], self.y[-1]))
        self.line1_head.set_data(self.n[-1], self.y[-1])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]
        self.draw()


''' End Class '''


class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)

''' End Class '''



def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    while(True):
        #print(V)
        V = explorerhat.analog.two.read()
        #print("delay", N)
        mySrc.data_signal.emit(V) # <- Here you emit a signal!
        time.sleep(N)
                                    

if __name__== '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()


    sys.exit(app.exec_())

''''''