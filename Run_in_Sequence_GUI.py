import numpy as np
import Camera
import DrawImage
import Param
import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui

MAX_X_PIXEL=3072
MAX_Y_PIXEL=2048

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.camera_connected=False
        self.acq_start=False
        self.image_displayed=False

        self.image=DrawImage.Plt_Result()
        
        self.timer=QtCore.QTimer()

        '''# Setup timer
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.aquire_image)
        self.timer.start(5)'''

        # self.camera=Camera.Camera()
        
        # params
        self.param=Param.Param()

        self.param.load_param(self.param.path+'Param.plk')
        '''
        # trigger mode is turned on in setup_camera()
        if not self.camera.setup_camera():
            self.close()

        self.camera.set_gain(self.param.GAIN) # set gain to 10.6 db
        #self.camera.auto_gain() # set gain to auto
        self.camera.set_exposure_time(self.param.EXPOSURE) # set exposure time to 100 us
        
        self.camera.start_acquisition()'''
        
        self.init_UI()

        self.connect_camera()

    def connect_camera(self):
        if self.camera_connected:
            self.info.setText('Camera already connected')
            return
        try:
            self.camera=Camera.Camera()
            # trigger mode is turned on in setup_camera()
            if not self.camera.setup_camera():
                raise Exception('Unable to set camera')
            self.set_gain()
            self.set_exposure()
            
            self.camera_connected=True
            self.info.setText('Camera connected')
            self.btn_connect.setDisabled(True)
            self.btn_disconnect.setDisabled(False)
            self.btn_gain.setDisabled(False)
            self.btn_exposure.setDisabled(False)
            self.btn_start.setDisabled(False)
            #self.btn_end.setDisabled(False)

        except:
            print('Fail to connect camera')
            self.info.setText('Fail to connect camera')

    def disconnect_camera(self):
        if not self.camera_connected:
            self.info.setText('Camera already disconnected')
            return
        self.end_acquisition()
        self.camera.release_camera()
        
        self.camera_connected=False
        self.info.setText('Camera disconnected')
        self.btn_connect.setDisabled(False)
        self.btn_disconnect.setDisabled(True)
        self.btn_gain.setDisabled(True)
        self.btn_exposure.setDisabled(True)
        self.btn_start.setDisabled(True)
        self.btn_end.setDisabled(True)
        

    def start_acquisition(self):
        if not self.camera_connected:
            self.info.setText('Connect camera before start acquisition')
            print('Connect camera before start acquisition')
            return
        if self.acq_start:
            self.info.setText('Camera already starts')
            print('Camera already starts')
            return
        self.camera.start_acquisition()
        self.timer.timeout.connect(self.aquire_image)
        self.acq_start=True
        self.btn_end.setDisabled(False)
        self.btn_start.setDisabled(True)
        self.info.setText('Start acquisition')
        self.timer.start(5)
        

    def end_acquisition(self):
        if not self.camera_connected:
            self.info.setText('Connect camera before end acquisition')
            print('Connect camera before end acquisition')
            return
        if not self.acq_start:
            self.info.setText('Camera already ends')
            print('Camera already ends')
            return
        self.timer.stop()
        self.camera.end_acquisition()
        self.acq_start=False
        self.btn_end.setDisabled(True)
        self.btn_start.setDisabled(False)
        self.info.setText('End acquisition')


    def init_UI(self):
        # Setup window
        self.setWindowTitle("image")
        self.setGeometry(200,200,2200,1200)  #(300,100,400,300)

        # Set image
        self.status=QtWidgets.QLabel("",self)
        self.status.resize(1500,100)
        self.status.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status.setScaledContents(True)
        #self.status.setText("Acquiring image...")
        #self.status.setFont(QtGui.QFont("Times", 12))
        self.status.move(0,0)
        
        self.log=QtWidgets.QTextBrowser(self)
        self.log.resize(600,200)
        self.log.move(1520,900)
        
        self.info=QtWidgets.QLabel("",self)
        self.info.resize(1500,100)
        self.info.setScaledContents(True)
        self.info.move(50,1100)

        self.lbl=QtWidgets.QLabel("",self)
        self.lbl.resize(1500,1000)
        self.lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.lbl.setScaledContents(True)
        #self.lbl.setText('Acquiring image...')
        #self.lbl.setFont(QtGui.QFont("Times", 12))
        self.lbl.move(0,100)

        # set Gain
        self.lb_gain=QtWidgets.QLabel("Gain (db):",self)
        self.lb_gain.resize(150,50)
        self.lb_gain.setScaledContents(True)
        self.lb_gain.move(1550,250)

        self.btn_gain=QtWidgets.QPushButton("set Gain",self)
        self.btn_gain.clicked.connect(self.set_gain)
        self.btn_gain.resize(200,50)
        self.btn_gain.move(1900,250)
        
        self.edit_Gain=QtWidgets.QLineEdit(self)
        self.edit_Gain.resize(100,30)
        self.edit_Gain.move(1750,260)
        self.edit_Gain.setText('%s' % self.param.GAIN)

        self.lb_gain_info=QtWidgets.QLabel('',self)#("Set Gain to %s db" % self.param.GAIN,self)
        self.lb_gain_info.resize(450,50)
        self.lb_gain_info.setScaledContents(True)
        self.lb_gain_info.move(1550,320)

        # set Exposure Time
        self.lb_exposure=QtWidgets.QLabel("Exposure (us):",self)
        self.lb_exposure.resize(200,50)
        self.lb_exposure.setScaledContents(True)
        self.lb_exposure.move(1550,350)

        self.btn_exposure=QtWidgets.QPushButton("set Exposure",self)
        self.btn_exposure.clicked.connect(self.set_exposure)
        self.btn_exposure.resize(200,50)
        self.btn_exposure.move(1900,350)
        
        self.edit_exposure=QtWidgets.QLineEdit(self)
        self.edit_exposure.resize(100,30)
        self.edit_exposure.move(1750,360)
        self.edit_exposure.setText('%s' % self.param.EXPOSURE)

        self.lb_exposure_info=QtWidgets.QLabel('',self)#("Set Exposure Time to %s us" % self.param.EXPOSURE,self)
        self.lb_exposure_info.resize(450,50)
        self.lb_exposure_info.setScaledContents(True)
        self.lb_exposure_info.move(1550,420)
        
        # X Y for display
        self.lb_display_Xmin=QtWidgets.QLabel("Xmin:",self)
        self.lb_display_Xmin.resize(170,30)
        self.lb_display_Xmin.setScaledContents(True)
        self.lb_display_Xmin.move(1550,500)
        
        self.edit_display_Xmin=QtWidgets.QLineEdit(self)
        self.edit_display_Xmin.setText('%s' % self.param.XMIN)
        self.edit_display_Xmin.resize(70,30)
        self.edit_display_Xmin.move(1650,500)
        
        self.lb_display_Xmax=QtWidgets.QLabel("Xmax:",self)
        self.lb_display_Xmax.resize(170,30)
        self.lb_display_Xmax.setScaledContents(True)
        self.lb_display_Xmax.move(1800,500)

        self.edit_display_Xmax=QtWidgets.QLineEdit(self)
        self.edit_display_Xmax.setText('%s' % self.param.XMAX)
        self.edit_display_Xmax.resize(70,30)
        self.edit_display_Xmax.move(1900,500)

        self.lb_display_Ymin=QtWidgets.QLabel("Ymin:",self)
        self.lb_display_Ymin.resize(170,30)
        self.lb_display_Ymin.setScaledContents(True)
        self.lb_display_Ymin.move(1550,550)

        self.edit_display_Ymin=QtWidgets.QLineEdit(self)
        self.edit_display_Ymin.setText('%s' % self.param.YMIN)
        self.edit_display_Ymin.resize(70,30)
        self.edit_display_Ymin.move(1650,550)
        
        self.lb_display_Ymax=QtWidgets.QLabel("Ymax:",self)
        self.lb_display_Ymax.resize(170,30)
        self.lb_display_Ymax.setScaledContents(True)
        self.lb_display_Ymax.move(1800,550)

        self.edit_display_Ymax=QtWidgets.QLineEdit(self)
        self.edit_display_Ymax.setText('%s' % self.param.YMAX)
        self.edit_display_Ymax.resize(70,30)
        self.edit_display_Ymax.move(1900,550)

        self.btn_display=QtWidgets.QPushButton("Display",self)
        self.btn_display.clicked.connect(self.display)
        self.btn_display.resize(450,50)
        self.btn_display.move(1550,600)

        # X Y for Calculate
        self.lb_Xmin=QtWidgets.QLabel("Xmin:",self)
        self.lb_Xmin.resize(170,30)
        self.lb_Xmin.setScaledContents(True)
        self.lb_Xmin.move(1550,700)
        
        self.edit_Xmin=QtWidgets.QLineEdit(self)
        self.edit_Xmin.setText('%s' % self.param.XMIN)
        self.edit_Xmin.resize(70,30)
        self.edit_Xmin.move(1650,700)
        
        self.lb_Xmax=QtWidgets.QLabel("Xmax:",self)
        self.lb_Xmax.resize(170,30)
        self.lb_Xmax.setScaledContents(True)
        self.lb_Xmax.move(1800,700)

        self.edit_Xmax=QtWidgets.QLineEdit(self)
        self.edit_Xmax.setText('%s' % self.param.XMAX)
        self.edit_Xmax.resize(70,30)
        self.edit_Xmax.move(1900,700)

        self.lb_Ymin=QtWidgets.QLabel("Ymin:",self)
        self.lb_Ymin.resize(170,30)
        self.lb_Ymin.setScaledContents(True)
        self.lb_Ymin.move(1550,750)

        self.edit_Ymin=QtWidgets.QLineEdit(self)
        self.edit_Ymin.setText('%s' % self.param.YMIN)
        self.edit_Ymin.resize(70,30)
        self.edit_Ymin.move(1650,750)
        
        self.lb_Ymax=QtWidgets.QLabel("Ymax:",self)
        self.lb_Ymax.resize(170,30)
        self.lb_Ymax.setScaledContents(True)
        self.lb_Ymax.move(1800,750)

        self.edit_Ymax=QtWidgets.QLineEdit(self)
        self.edit_Ymax.setText('%s' % self.param.YMAX)
        self.edit_Ymax.resize(70,30)
        self.edit_Ymax.move(1900,750)

        self.btn_cal=QtWidgets.QPushButton("calculate OD",self)
        self.btn_cal.clicked.connect(self.calculate_od)
        self.btn_cal.resize(450,50)
        self.btn_cal.move(1550,800)

        self.cal_result=QtWidgets.QLabel("",self)
        self.cal_result.resize(450,30)
        self.cal_result.setScaledContents(True)
        self.cal_result.move(1550,800)

        # start
        self.btn_start=QtWidgets.QPushButton("Start",self)
        self.btn_start.clicked.connect(self.start_acquisition)
        self.btn_start.resize(200,50)
        self.btn_start.move(1550,120)

        # end
        self.btn_end=QtWidgets.QPushButton("End",self)
        self.btn_end.clicked.connect(self.end_acquisition)
        self.btn_end.resize(200,50)
        self.btn_end.move(1800,120)

        # connect camera
        self.btn_connect=QtWidgets.QPushButton("Connect",self)
        self.btn_connect.clicked.connect(self.connect_camera)
        self.btn_connect.resize(200,50)
        self.btn_connect.move(1550,50)

        # disconnect camera
        self.btn_disconnect=QtWidgets.QPushButton("Disconnect",self)
        self.btn_disconnect.clicked.connect(self.disconnect_camera)
        self.btn_disconnect.resize(200,50)
        self.btn_disconnect.move(1800,50)

        # select image and display
        self.btn_select=QtWidgets.QPushButton("Select",self)
        self.btn_select.clicked.connect(self.select_image)
        self.btn_select.resize(100,30)
        self.btn_select.move(1500,1100)

        self.edit_filename=QtWidgets.QLineEdit(self)
        self.edit_filename.setText(self.param.CURRENT_IMAGE_PATH)
        self.edit_filename.resize(400,30)
        self.edit_filename.move(1600,1100)

        self.btn_load=QtWidgets.QPushButton("Load",self)
        self.btn_load.clicked.connect(self.load_image)
        self.btn_load.resize(100,30)
        self.btn_load.move(2000,1100)

        

        # disable all the btn except btn_connect
        self.btn_gain.setDisabled(True)
        # self.btn_cal.setDisabled(True)
        self.btn_exposure.setDisabled(True)
        self.btn_start.setDisabled(True)
        self.btn_end.setDisabled(True)
        self.btn_disconnect.setDisabled(True)


    def set_gain(self):
        try:
            str=self.edit_Gain.text()
            gain=float(str)
            if gain >= 0 and gain < 47.99:
                #self.camera.end_acquisition()
                self.camera.set_gain(gain)
                self.lb_gain_info.setText('Set Gain to %s db' % gain)
                self.param.GAIN=gain
                #self.camera.start_acquisition()
                
        except:
            if str=='auto' or str=='Auto':
                self.camera.auto_gain()
                self.lb_gain_info.setText('Set Gain to Auto')

    def set_exposure(self):
        try:
            str=self.edit_exposure.text()
            exposure=int(str)
            if exposure >= 0 and exposure <= 5000:
                #self.camera.end_acquisition()
                self.camera.set_exposure_time(exposure)
                self.lb_exposure_info.setText('Set Exposure Time to %s us' % exposure)
                self.param.EXPOSURE=exposure
                #self.camera.start_acquisition()
                
        except:
            #if str=='auto' or str=='Auto':
                #self.camera.auto_gain()
                #self.lb_gain_info.setText('Set Gain to Auto')
            pass


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
            self.load_image()
        except:
            self.info.setText('Fail to select image')
            print('Fail to select image')
    
    def load_image(self):
        try:
            tmp=np.load(self.edit_filename.text())
            if not (type(tmp[0,0]) == np.float16 or type(tmp[0,0]) == np.float32 or type(tmp[0,0]) == np.uint16):
                raise Exception('Wrong data type')
            if (not (len(tmp)==MAX_Y_PIXEL)) or (not (len(tmp[0])==MAX_X_PIXEL)):
                raise Exception('Wrong data type')
            self.od=tmp
            self.display()
        except:
            self.info.setText('Fail to load image')
            print('Fail to load image')

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

            self.image.plt_od(self.od,dis_xmin,dis_xmax,dis_ymin,dis_ymax)
            self.image.save_figure(self.param.path+'tmp')
            self.pm=QtGui.QPixmap(self.param.path+'tmp.png')
            self.lbl.setPixmap(self.pm)
            self.image_displayed=True
            os.remove(self.param.path+'tmp.png')

            self.param.DIS_XMIN=dis_xmin
            self.param.DIS_XMAX=dis_xmax
            self.param.DIS_YMIN=dis_ymin
            self.param.DIS_YMAX=dis_ymax
        except Exception as ex:
            self.info.setText('Fail to display image')
            print('Fail to display image')
            print('Error: %s'%ex)

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
            
            total_od=np.sum(self.od[xmin:xmax,ymin:ymax])
            self.cal_result.setText('Optical density: %f' % total_od)
        except:
            print('Error: OD Calulation Error')
            self.cal_result.setText('OD Calculation Error...')
        

    def closeEvent(self,event):
        #try:
        #    self.timer.stop()
        #except:
        #    pass
        self.disconnect_camera()
        self.image.release()
        self.param.save_param(self.param.path+'Param.plk')
        #self.camera.release_camera()
        event.accept()


    def aquire_image(self):

        try:
            if not self.camera.acquire_single_image():
                return False
            pass
        except Exception as ex:
            print('Error: %s' % ex)
            return False
        if self.camera.image_cnt > 0 and self.camera.image_cnt % 3 == 0 :
            
            # Calculate OD
            try:
                self.background=self.camera.get_image(self.camera.image_cnt)
                self.no_atom=self.camera.get_image(self.camera.image_cnt-1)
                self.atom=self.camera.get_image(self.camera.image_cnt-2)
                self.od=-np.log((self.atom-self.background)/(self.no_atom-self.background),dtype=np.float16)
            
                self.image.plt_result(self.background,self.no_atom,self.atom,self.od,
                                      self.param.XMIN,self.param.XMAX,self.param.YMIN,self.param.YMAX)
                self.image.save_figure(self.camera.path+'result_%d'%(self.camera.image_cnt//3))
                
                self.pm=QtGui.QPixmap(self.camera.path+'result_%d'%(self.camera.image_cnt//3))
                self.lbl.setPixmap(self.pm)
                self.image_displayed=True

                self.status.setText('result_%d'%(self.camera.image_cnt//3)+'.png')
                #self.show()

            except Exception as ex:
                print('Error: %s' % ex)
                return False
            

            '''
            # Save original data
            filename_bg=camera.auto_filename(camera.image_cnt)+"_background"
            filename_na=camera.auto_filename(camera.image_cnt-1)+"_no_atom"
            filename_at=camera.auto_filename(camera.image_cnt-2)+"_atom"
            camera.save_data(filename_bg,camera.image_cnt)
            camera.save_data(filename_na,camera.image_cnt-1)
            camera.save_data(filename_at,camera.image_cnt-2)
            np.save(camera.path+camera.auto_filename()+"_od",od)
            
            # Draw image
            DrawImage.array16_to_image(background,camera.path,filename_bg)
            DrawImage.array16_to_image(no_atom,camera.path,filename_na)
            DrawImage.array16_to_image(atom,camera.path,filename_at)
            DrawImage.array32f_to_image(od,camera.path,camera.auto_filename()+"_od")
            '''

        return True


if __name__ == "__main__":
    try:
        qapp = QtWidgets.QApplication(sys.argv)
        app = MyWindow()
    
        app.show()
        app.activateWindow()
        app.raise_()
        qapp.exec()
    except Exception as ex:
        '''try:
            app.camera.release_camera()
        except:
            pass'''
        print('Error: %s' % ex)
        