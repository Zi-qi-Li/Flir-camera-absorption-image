import sys
import typing
from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtWidgets import QWidget
import matplotlib.pyplot as plt
import Param
import numpy as np

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self,Update_Func,Close_Func):
        super().__init__()

        self.myUpdate=Update_Func
        self.myClose=Close_Func

        # Setup timer
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.update_func)
        self.timer.start(5)

        # Setup window
        self.setWindowTitle("image")
        self.setGeometry(300,100,1500,1000)  #(300,100,400,300)
    
    def update_func(self):
        self.myUpdate()

    def closeEvent(self,event):
        self.timer.stop()
        self.myClose()
        event.accept()
        
class MyClass(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("image")
        self.setGeometry(300,100,1500,1000)  #(300,100,400,300)
        self.lbl=QtWidgets.QLabel("figure",self)
        self.pm=QtGui.QPixmap("./image/result_1.png")
        self.lbl.setPixmap(self.pm)
        self.lbl.resize(1200,900)
        self.lbl.setScaledContents(True)

        
        btn1=QtWidgets.QPushButton("remove",self)
        btn1.clicked.connect(self.myRemovePic)
        btn1.move(0,900)
        
        btn2=QtWidgets.QPushButton("add",self)
        btn2.clicked.connect(self.myAddPic)
        btn2.move(0,950)
        #self.show()
    def myRemovePic(self):
        self.lbl.setPixmap(QtGui.QPixmap(""))
    def myAddPic(self):
        self.lbl.setPixmap(self.pm)
        


#qapp = QtWidgets.QApplication(sys.argv)
#app = MyClass()
    
#app.show()
#app.activateWindow()
#app.raise_()
#qapp.exec()

a=np.load('.\\image\\Param.npy',allow_pickle=True)