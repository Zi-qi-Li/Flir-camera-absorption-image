import numpy as np
import Camera
import DrawImage
import Param
import Release_Camera
import sys
import os
from PyQt5 import QtCore, QtWidgets
import datetime
import copy

MAX_X_PIXEL=3072
MAX_Y_PIXEL=2048

DESKTOP_DEFAULT_HEIGHT=1440
DESKTOP_DEFAULT_WIDTH=2560

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self,window_magnification):
        super().__init__()
        
        # Change the size of UI according to the resolution of screen
        self.window_magnification=window_magnification

        # Bool object to check the status
        self.camera_connected=False
        self.acq_start=False
        self.image_displayed=False

        # Object to draw image
        self.plt_image=DrawImage.QMatplotlib(self.window_magnification)
        
        # Object to acquire image
        self.timer=QtCore.QTimer()

        # Object to save params
        self.param=Param.Param()
        # Try to load params in last run. If it is the first time to run, it will create a folder to store params.
        self.param.load_param(self.param.path+'Param.plk')
        
        # Init GUI
        self.init_UI()

        # Try to connect camera, if there is no camera, do nothing.
        self.connect_camera()

    def connect_camera(self):
        if self.camera_connected:
            self.log.append('Camera already connected')
            #self.info.setText('Camera already connected')
            return
        try:
            self.log.append('Connecting camera...')
            self.camera=Camera.Camera()
            # trigger mode is turned on in setup_camera()
            if not self.camera.setup_camera():
                raise Exception('Unable to set camera')
            self.set_gain()
            self.set_exposure()
            
            self.camera_connected=True
            self.log.append('Camera connected')
            #self.info.setText('Camera connected')
            self.btn_connect.setDisabled(True)
            self.btn_disconnect.setDisabled(False)
            self.btn_gain.setDisabled(False)
            self.btn_exposure.setDisabled(False)
            self.btn_start.setDisabled(False)
            #self.btn_end.setDisabled(False)

        except Exception as ex:
            print('GUI: Fail to connect camera: %s' % ex)
            self.log.append('Fail to connect camera: %s' % ex)
            #self.info.setText('Fail to connect camera')


    def disconnect_camera(self):
        if not self.camera_connected:
            self.log.append('Camera already disconnected')
            #self.info.setText('Camera already disconnected')
            return
        try:
            self.log.append('Disconnecting camera...')
            self.end_acquisition()
            self.camera.release_camera()
            
            #self.info.setText('Camera disconnected')
            self.btn_connect.setDisabled(False)
            self.btn_disconnect.setDisabled(True)
            self.btn_gain.setDisabled(True)
            self.btn_exposure.setDisabled(True)
            self.btn_start.setDisabled(True)
            self.btn_end.setDisabled(True)
            
            self.camera_connected=False
            self.log.append('Camera disconnected')
        except Exception as ex:
            print('GUI: Fail to disconnect camera: %s' % ex)
            self.log.append('Fail to disconnect camera: %s' % ex)


    def start_acquisition(self):
        if not self.camera_connected:
            self.log.append('Connect camera first before start acquisition')
            #self.info.setText('Connect camera before start acquisition')
            print('GUI: Connect camera first before start acquisition')
            return
        if self.acq_start:
            self.log.append('Camera already starts')
            #self.info.setText('Camera already starts')
            print('GUI: Camera already starts')
            return
        if not self.camera.start_acquisition():
            self.log.append('Fail to start camera')
            print('GUI: Fail to start camera')
            return
        self.timer.timeout.connect(self.aquire_image)
        self.acq_start=True
        self.btn_end.setDisabled(False)
        self.btn_start.setDisabled(True)
        self.log.append('Start acquisition')
        #self.info.setText('Start acquisition')
        self.timer.start(5)


    def end_acquisition(self):
        if not self.camera_connected:
            #self.log.append('Connect camera before end acquisition')
            #self.info.setText('Connect camera before end acquisition')
            #print('Connect camera before end acquisition')
            return
        if not self.acq_start:
            #self.log.append('Camera already ends')
            #self.info.setText('Camera already ends')
            #print('Camera already ends')
            return
        try:
            self.timer.stop()
        except:
            pass
        self.camera.end_acquisition()
        self.acq_start=False
        self.btn_end.setDisabled(True)
        self.btn_start.setDisabled(False)
        self.log.append('End acquisition')
        #self.info.setText('End acquisition')


    def init_UI(self):
        # Setup window
        self.setWindowTitle("image")
        self.setGeometry(int(100*self.window_magnification),int(100*self.window_magnification),
                         int(2200*self.window_magnification),int(1150*self.window_magnification))  #(300,100,400,300)

        
        # This browser shows infomation of execution
        self.log=QtWidgets.QTextBrowser(self)
        self.log.resize(int(600*self.window_magnification),int(300*self.window_magnification))
        self.log.move(int(1520*self.window_magnification),int(820*self.window_magnification))
        

        # Label to display Image
        self.lbl=QtWidgets.QLabel("",self)
        self.lbl.resize(int(1500*self.window_magnification),int(1000*self.window_magnification))
        self.lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.lbl.setScaledContents(True)
        #self.lbl.setText('Acquiring image...')
        #self.lbl.setFont(QtGui.QFont("Times", 12))
        self.lbl.move(int(0*self.window_magnification),int(100*self.window_magnification))
        self.hboxlayout = QtWidgets.QHBoxLayout(self.lbl)
        self.hboxlayout.addWidget(self.plt_image)

        # set Gain
        self.lb_gain=QtWidgets.QLabel("Gain (db):",self)
        self.lb_gain.resize(int(150*self.window_magnification),int(50*self.window_magnification))
        self.lb_gain.setScaledContents(True)
        self.lb_gain.move(int(1550*self.window_magnification),int(220*self.window_magnification))

        self.btn_gain=QtWidgets.QPushButton("set Gain",self)
        self.btn_gain.clicked.connect(self.set_gain)
        self.btn_gain.resize(int(200*self.window_magnification),int(50*self.window_magnification))
        self.btn_gain.move(int(1900*self.window_magnification),int(220*self.window_magnification))
        
        self.edit_Gain=QtWidgets.QLineEdit(self)
        self.edit_Gain.resize(int(100*self.window_magnification),int(30*self.window_magnification))
        self.edit_Gain.move(int(1750*self.window_magnification),int(230*self.window_magnification))
        self.edit_Gain.setText('%s' % self.param.GAIN)

        #self.lb_gain_info=QtWidgets.QLabel('',self)#("Set Gain to %s db" % self.param.GAIN,self)
        #self.lb_gain_info.resize(450,50)
        #self.lb_gain_info.setScaledContents(True)
        #self.lb_gain_info.move(1550,260)

        # set Exposure Time
        self.lb_exposure=QtWidgets.QLabel("Exposure (us):",self)
        self.lb_exposure.resize(int(200*self.window_magnification),int(50*self.window_magnification))
        self.lb_exposure.setScaledContents(True)
        self.lb_exposure.move(int(1550*self.window_magnification),int(290*self.window_magnification))

        self.btn_exposure=QtWidgets.QPushButton("set Exposure",self)
        self.btn_exposure.clicked.connect(self.set_exposure)
        self.btn_exposure.resize(int(200*self.window_magnification),int(50*self.window_magnification))
        self.btn_exposure.move(int(1900*self.window_magnification),int(290*self.window_magnification))
        
        self.edit_exposure=QtWidgets.QLineEdit(self)
        self.edit_exposure.resize(int(100*self.window_magnification),int(30*self.window_magnification))
        self.edit_exposure.move(int(1750*self.window_magnification),int(300*self.window_magnification))
        self.edit_exposure.setText('%s' % self.param.EXPOSURE)

        #self.lb_exposure_info=QtWidgets.QLabel('',self)#("Set Exposure Time to %s us" % self.param.EXPOSURE,self)
        #self.lb_exposure_info.resize(450,50)
        #self.lb_exposure_info.setScaledContents(True)
        #self.lb_exposure_info.move(1550,360)
        
        # X Y for display
        self.lb_display_Xmin=QtWidgets.QLabel("Xmin:",self)
        self.lb_display_Xmin.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_display_Xmin.setScaledContents(True)
        self.lb_display_Xmin.move(int(1550*self.window_magnification),int(400*self.window_magnification))
        
        self.edit_display_Xmin=QtWidgets.QLineEdit(self)
        self.edit_display_Xmin.setText('%s' % self.param.DIS_XMIN)
        self.edit_display_Xmin.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_display_Xmin.move(int(1650*self.window_magnification),int(400*self.window_magnification))
        
        self.lb_display_Xmax=QtWidgets.QLabel("Xmax:",self)
        self.lb_display_Xmax.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_display_Xmax.setScaledContents(True)
        self.lb_display_Xmax.move(int(1800*self.window_magnification),int(400*self.window_magnification))

        self.edit_display_Xmax=QtWidgets.QLineEdit(self)
        self.edit_display_Xmax.setText('%s' % self.param.DIS_XMAX)
        self.edit_display_Xmax.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_display_Xmax.move(int(1900*self.window_magnification),int(400*self.window_magnification))

        self.lb_display_Ymin=QtWidgets.QLabel("Ymin:",self)
        self.lb_display_Ymin.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_display_Ymin.setScaledContents(True)
        self.lb_display_Ymin.move(int(1550*self.window_magnification),int(450*self.window_magnification))

        self.edit_display_Ymin=QtWidgets.QLineEdit(self)
        self.edit_display_Ymin.setText('%s' % self.param.DIS_YMIN)
        self.edit_display_Ymin.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_display_Ymin.move(int(1650*self.window_magnification),int(450*self.window_magnification))
        
        self.lb_display_Ymax=QtWidgets.QLabel("Ymax:",self)
        self.lb_display_Ymax.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_display_Ymax.setScaledContents(True)
        self.lb_display_Ymax.move(int(1800*self.window_magnification),int(450*self.window_magnification))

        self.edit_display_Ymax=QtWidgets.QLineEdit(self)
        self.edit_display_Ymax.setText('%s' % self.param.DIS_YMAX)
        self.edit_display_Ymax.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_display_Ymax.move(int(1900*self.window_magnification),int(450*self.window_magnification))

        self.btn_display=QtWidgets.QPushButton("Display",self)
        self.btn_display.clicked.connect(self.display)
        self.btn_display.resize(int(450*self.window_magnification),int(50*self.window_magnification))
        self.btn_display.move(int(1550*self.window_magnification),int(500*self.window_magnification))

        # X Y for calculate OD
        self.lb_Xmin=QtWidgets.QLabel("Xmin:",self)
        self.lb_Xmin.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_Xmin.setScaledContents(True)
        self.lb_Xmin.move(int(1550*self.window_magnification),int(600*self.window_magnification))
        
        self.edit_Xmin=QtWidgets.QLineEdit(self)
        self.edit_Xmin.setText('%s' % self.param.XMIN)
        self.edit_Xmin.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_Xmin.move(int(1650*self.window_magnification),int(600*self.window_magnification))
        
        self.lb_Xmax=QtWidgets.QLabel("Xmax:",self)
        self.lb_Xmax.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_Xmax.setScaledContents(True)
        self.lb_Xmax.move(int(1800*self.window_magnification),int(600*self.window_magnification))

        self.edit_Xmax=QtWidgets.QLineEdit(self)
        self.edit_Xmax.setText('%s' % self.param.XMAX)
        self.edit_Xmax.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_Xmax.move(int(1900*self.window_magnification),int(600*self.window_magnification))

        self.lb_Ymin=QtWidgets.QLabel("Ymin:",self)
        self.lb_Ymin.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_Ymin.setScaledContents(True)
        self.lb_Ymin.move(int(1550*self.window_magnification),int(650*self.window_magnification))

        self.edit_Ymin=QtWidgets.QLineEdit(self)
        self.edit_Ymin.setText('%s' % self.param.YMIN)
        self.edit_Ymin.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_Ymin.move(int(1650*self.window_magnification),int(650*self.window_magnification))
        
        self.lb_Ymax=QtWidgets.QLabel("Ymax:",self)
        self.lb_Ymax.resize(int(170*self.window_magnification),int(30*self.window_magnification))
        self.lb_Ymax.setScaledContents(True)
        self.lb_Ymax.move(int(1800*self.window_magnification),int(650*self.window_magnification))

        self.edit_Ymax=QtWidgets.QLineEdit(self)
        self.edit_Ymax.setText('%s' % self.param.YMAX)
        self.edit_Ymax.resize(int(70*self.window_magnification),int(30*self.window_magnification))
        self.edit_Ymax.move(int(1900*self.window_magnification),int(650*self.window_magnification))

        self.btn_cal=QtWidgets.QPushButton("Calculate OD",self)
        self.btn_cal.clicked.connect(self.calculate_od)
        self.btn_cal.resize(int(450*self.window_magnification),int(50*self.window_magnification))
        self.btn_cal.move(int(1550*self.window_magnification),int(700*self.window_magnification))

        self.cal_result=QtWidgets.QLabel("",self)
        self.cal_result.resize(int(450*self.window_magnification),int(30*self.window_magnification))
        self.cal_result.setScaledContents(True)
        self.cal_result.move(int(1550*self.window_magnification),int(750*self.window_magnification))

        # start
        self.btn_start=QtWidgets.QPushButton("Start",self)
        self.btn_start.clicked.connect(self.start_acquisition)
        self.btn_start.resize(int(175*self.window_magnification),int(50*self.window_magnification))
        self.btn_start.move(int(1550*self.window_magnification),int(120*self.window_magnification))

        # end
        self.btn_end=QtWidgets.QPushButton("End",self)
        self.btn_end.clicked.connect(self.end_acquisition)
        self.btn_end.resize(int(175*self.window_magnification),int(50*self.window_magnification))
        self.btn_end.move(int(1750*self.window_magnification),int(120*self.window_magnification))

        # connect camera
        self.btn_connect=QtWidgets.QPushButton("Connect",self)
        self.btn_connect.clicked.connect(self.connect_camera)
        self.btn_connect.resize(int(175*self.window_magnification),int(50*self.window_magnification))
        self.btn_connect.move(int(1550*self.window_magnification),int(50*self.window_magnification))

        # disconnect camera
        self.btn_disconnect=QtWidgets.QPushButton("Disconnect",self)
        self.btn_disconnect.clicked.connect(self.disconnect_camera)
        self.btn_disconnect.resize(int(175*self.window_magnification),int(50*self.window_magnification))
        self.btn_disconnect.move(int(1750*self.window_magnification),int(50*self.window_magnification))

        # Refresh camera
        self.btn_refresh=QtWidgets.QPushButton("Refresh",self)
        self.btn_refresh.clicked.connect(self.refresh_camera)
        self.btn_refresh.resize(int(150*self.window_magnification),int(50*self.window_magnification))
        self.btn_refresh.move(int(1950*self.window_magnification),int(50*self.window_magnification))

        # select image and display
        self.btn_select=QtWidgets.QPushButton("Select",self)
        self.btn_select.clicked.connect(self.select_image)
        self.btn_select.resize(int(110*self.window_magnification),int(40*self.window_magnification))
        self.btn_select.move(int(1200*self.window_magnification),int(45*self.window_magnification))

        self.edit_filename=QtWidgets.QLineEdit(self)
        self.edit_filename.setText(self.param.CURRENT_IMAGE_PATH+'/')
        self.edit_filename.resize(int(1000*self.window_magnification),int(30*self.window_magnification))
        self.edit_filename.move(int(180*self.window_magnification),int(50*self.window_magnification))

        self.btn_load=QtWidgets.QPushButton("Load",self)
        self.btn_load.clicked.connect(self.load_image)
        self.btn_load.resize(int(110*self.window_magnification),int(40*self.window_magnification))
        self.btn_load.move(int(50*self.window_magnification),int(45*self.window_magnification))

        self.btn_save=QtWidgets.QPushButton("Save",self)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_save.resize(int(110*self.window_magnification),int(40*self.window_magnification))
        self.btn_save.move(int(1320*self.window_magnification),int(45*self.window_magnification))
        

        # disable all the btn except btn_connect
        self.btn_gain.setDisabled(True)
        self.btn_exposure.setDisabled(True)
        self.btn_start.setDisabled(True)
        self.btn_end.setDisabled(True)
        self.btn_disconnect.setDisabled(True)
        self.btn_cal.setDisabled(True)
        self.btn_display.setDisabled(True)


    def set_gain(self):
        try:
            str=self.edit_Gain.text()
            gain=float(str)
            if gain >= 0 and gain < 47.99:
                #self.camera.end_acquisition()
                if self.camera.set_gain(gain):
                    self.log.append('Set Gain to %s db' % gain)
                    #self.lb_gain_info.setText('Set Gain to %s db' % gain)
                    self.param.GAIN=gain
                    #self.camera.start_acquisition()
                else:
                    raise Exception('Set gain error')
                
        except Exception as ex:
            if str=='auto' or str=='Auto':
                self.camera.auto_gain()
                self.log.append('Set Gain to Auto')
                #self.lb_gain_info.setText('Set Gain to Auto')
                return True
            else:
                self.log.append('Fail to set Gain: %s'%ex)
                return False
        return True
            


    def set_exposure(self):
        try:
            str=self.edit_exposure.text()
            exposure=int(str)
            if exposure >= 0:
                #self.camera.end_acquisition()
                if self.camera.set_exposure_time(exposure):
                    self.log.append('Set Exposure Time to %s us' % exposure)
                    #self.lb_exposure_info.setText('Set Exposure Time to %s us' % exposure)
                    self.param.EXPOSURE=exposure
                    #self.camera.start_acquisition()
                else:
                    raise Exception('Set exposure time error')
                
        except Exception as ex:
            #if str=='auto' or str=='Auto':
                #self.camera.auto_gain()
                #self.lb_gain_info.setText('Set Gain to Auto')
            self.log.append('Fail to set Exposure time: %s'%ex)
            return False
        return True


    def check_x(self,x):
        if x>MAX_X_PIXEL or x<0:
            raise Exception('Wrong X')


    def check_y(self,y):
        if y>MAX_Y_PIXEL or y<0:
            raise Exception('Wrong X')


    def select_image(self):
        try:
            #path,name=os.path.split(self.edit_filename.text())
            filename,filetype=QtWidgets.QFileDialog.getOpenFileNames(self,'Select Image',
                                                        self.param.CURRENT_IMAGE_PATH, "*.npy")
            self.edit_filename.setText(filename[0])
            self.param.CURRENT_IMAGE_PATH,name=os.path.split(filename[0])
        except:
            return False
        try:
            self.load_image()
        except:
            self.log.append('Fail to select image: %s'%ex)
            #self.info.setText('Fail to select image')
            print('GUI: Fail to select image: %s'%ex)
            return False
        return True


    def load_image(self):
        try:
            tmp=np.load(self.edit_filename.text())
        except:
            self.select_image()
            return
        try:
            if not (type(tmp[0,0]) == np.float16 or type(tmp[0,0]) == np.float32 or type(tmp[0,0]) == np.uint16):
                raise Exception('Wrong data type')
            if (not (len(tmp)==MAX_Y_PIXEL)) or (not (len(tmp[0])==MAX_X_PIXEL)):
                raise Exception('Wrong data type')
            self.od=tmp
            self.log.append('Load image successfully')
            print('GUI: Load image successfully')
            self.display()
        except Exception as ex:
            self.log.append('Fail to load image: %s' % ex)
            #self.info.setText('Fail to load image')
            print('GUI: Fail to load image: %s' % ex)
            return False
        return True


    def display(self):
        try:
            dis_xmin=int(self.edit_display_Xmin.text())
            dis_xmax=int(self.edit_display_Xmax.text())
            dis_ymin=int(self.edit_display_Ymin.text())
            dis_ymax=int(self.edit_display_Ymax.text())
            self.check_x(dis_xmin)
            self.check_x(dis_xmax)
            self.check_y(dis_ymin)
            self.check_y(dis_ymax)
            if dis_xmin>=dis_xmax or dis_ymin>=dis_ymax:
                raise Exception('Wrong X or Y')
            
            self.param.DIS_XMIN=dis_xmin
            self.param.DIS_XMAX=dis_xmax
            self.param.DIS_YMIN=dis_ymin
            self.param.DIS_YMAX=dis_ymax

            
            self.plt_image.plt_image(self.od,self.param.DIS_XMIN,self.param.DIS_XMAX,self.param.DIS_YMIN,self.param.DIS_YMAX)
            self.calculate_od()

            '''
            self.image.plt_od(self.od,self.param.DIS_XMIN,self.param.DIS_XMAX,self.param.DIS_YMIN,self.param.DIS_YMAX,
                              self.param.XMIN,self.param.XMAX,self.param.YMIN,self.param.YMAX)
            self.image.save_figure(self.param.path+'tmp')
            self.pm=QtGui.QPixmap(self.param.path+'tmp.png')
            self.lbl.setPixmap(self.pm)
            os.remove(self.param.path+'tmp.png')'''

            if not self.image_displayed:
                self.image_displayed=True
                self.btn_display.setDisabled(False)
                self.btn_cal.setDisabled(False)
            

            
            self.log.append('Display image successfully')
            print('GUI: Display image successfully')
            #raise Exception('')
            
        except Exception as ex:
            self.log.append('Fail to display image: %s' % ex)
            #self.info.setText('Fail to display image')
            print('GUI: Fail to display image: %s' % ex)
            #print('Error: %s'%ex)
            return False
        return True


    def save_image(self):
        try:
            filename,filetype=QtWidgets.QFileDialog.getSaveFileName(self,'Save Image',
                                                        self.param.IMAGE_SAVING_PATH, "*.npy")
            if len(filename)>0:
                self.param.IMAGE_SAVING_PATH,name=os.path.split(filename)
            else:
                raise Exception('No filename for saving')
            #print(self.param.IMAGE_SAVING_PATH)
        except Exception as ex:
            #print('%s' % ex)
            return
        try:
            np.save(filename,self.od)
            self.edit_filename.setText(filename)
            self.log.append('Image saved successfully')
            print('GUI: Image saved successfully')
        except Exception as ex:
            self.log.append('Fail to save image: %s' % ex)
            print('GUI: Fail to save image: %s' % ex)


    def save_image_auto(self):
        try:
            np.save(self.edit_filename.text(),self.od)
            #self.edit_filename.setText(filename)
            self.log.append('Image saved successfully')
            print('GUI: Image saved successfully')
        except Exception as ex:
            self.log.append('Fail to save image: %s' % ex)
            print('GUI: Fail to save image: %s' % ex)


    def calculate_od(self):
        try:
            xmin=int(self.edit_Xmin.text())
            xmax=int(self.edit_Xmax.text())
            ymin=int(self.edit_Ymin.text())
            ymax=int(self.edit_Ymax.text())
            self.check_x(xmin)
            self.check_x(xmax)
            self.check_y(ymin)
            self.check_y(ymax)
            if xmin>=xmax or ymin>=ymax:
                raise Exception('Wrong X or Y')
            
            self.param.XMIN=xmin
            self.param.XMAX=xmax
            self.param.YMIN=ymin
            self.param.YMAX=ymax
            
            tmp=copy.deepcopy(self.od[ymin:ymax,xmin:xmax])
            tmp[np.isnan(tmp)]=0
            tmp[np.isinf(tmp)]=0
            total_od=np.sum(tmp,dtype=np.float32)
            self.plt_image.plt_od_region(self.param.XMIN,self.param.XMAX,self.param.YMIN,self.param.YMAX)
            print('GUI: Optical density: %s' % total_od)
            self.log.append('Optical density: %s' % total_od)
            self.cal_result.setText('Optical density: %s' % total_od)
            self.plt_image.draw()
        except Exception as ex:
            print('GUI: Fail to calculate OD: %s' % ex)
            self.log.append('Fail to calculate OD: %s' % ex)
            self.cal_result.setText('Fail to calculate OD')


    def refresh_camera(self):
        try:
            self.disconnect_camera()
        except:
            pass
        Release_Camera.Release_camera()
        self.connect_camera()


    def closeEvent(self,event):
        #try:
        #    self.timer.stop()
        #except:
        #    pass
        self.disconnect_camera()
        try:
            self.plt_image.release()
        except:
            pass
        self.param.save_param(self.param.path+'Param.plk')
        #self.camera.release_camera()
        event.accept()


    def aquire_image(self):

        try:
            if not self.camera.acquire_single_image():
                return False
            self.log.append('Aquire image %d successfully' % self.camera.image_cnt)
        except Exception as ex:
            #print('Error: %s' % ex)
            print('GUI: Fail to aquire image: %s' % ex)
            self.log.append('Fail to aquire image: %s' % ex)
            self.end_acquisition()
            return False
        if self.camera.image_cnt > 0 and self.camera.image_cnt % 3 == 0 :
            
            # Calculate OD
            try:
                self.log.append('Get 3 images, processing data...')
                self.background=self.camera.get_image(self.camera.image_cnt)
                self.no_atom=self.camera.get_image(self.camera.image_cnt-1)
                self.atom=self.camera.get_image(self.camera.image_cnt-2)
                self.od=-np.log((self.atom-self.background)/(self.no_atom-self.background),dtype=np.float32)
                '''
                self.image.plt_result(self.background,self.no_atom,self.atom,self.od,
                                      self.param.XMIN,self.param.XMAX,self.param.YMIN,self.param.YMAX)
                self.image.save_figure(self.camera.path+'result_%d'%(self.camera.image_cnt//3))
                
                self.pm=QtGui.QPixmap(self.camera.path+'result_%d'%(self.camera.image_cnt//3))
                self.lbl.setPixmap(self.pm)
                #self.image_displayed=True
                '''
                auto_filename=datetime.datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')
                self.edit_filename.setText(self.camera.path+auto_filename)
                self.save_image_auto()
                self.display()
                self.log.append('Complete, save data as %s' % auto_filename + '.npy')
                

                #self.status.setText('result_%d'%(self.camera.image_cnt//3)+'.png')
                #self.show()
                pass

            except Exception as ex:
                print('GUI: Fail to process data: %s' % ex)
                self.log.append('Fail to process data: %s' % ex)
                #print('Error: %s' % ex)
                return False
            

            '''
            # Save original data
            filename_bg=self.camera.auto_filename(self.camera.image_cnt)+"_background"
            filename_na=self.camera.auto_filename(self.camera.image_cnt-1)+"_no_atom"
            filename_at=self.camera.auto_filename(self.camera.image_cnt-2)+"_atom"
            self.camera.save_data(filename_bg,self.camera.image_cnt)
            self.camera.save_data(filename_na,self.camera.image_cnt-1)
            self.camera.save_data(filename_at,self.camera.image_cnt-2)
            #np.save(camera.path+camera.auto_filename()+"_od",od)
            
            # Draw image
            DrawImage.array16_to_image(self.background,self.camera.path,filename_bg)
            DrawImage.array16_to_image(self.no_atom,self.camera.path,filename_na)
            DrawImage.array16_to_image(self.atom,self.camera.path,filename_at)
            #DrawImage.array32f_to_image(self.od,camera.path,self.camera.auto_filename()+"_od")'''
            

        return True


if __name__ == "__main__":
    try:
        qapp = QtWidgets.QApplication(sys.argv)

        # Change the size of UI according to the resolution of screen
        my_desktop=qapp.desktop()
        desktop_height=my_desktop.height()
        desktop_width=my_desktop.width()
        window_magnification=min(desktop_height/DESKTOP_DEFAULT_HEIGHT,desktop_width/DESKTOP_DEFAULT_WIDTH)

        app = MyWindow(window_magnification)
    
        app.show()
        app.activateWindow()
        app.raise_()
        qapp.exec()
    except Exception as ex:
        '''try:
            app.camera.release_camera()
        except:
            pass'''
        print('GUI: Error: %s' % ex)
        