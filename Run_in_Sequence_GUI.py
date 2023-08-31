import numpy as np
import Camera
import DrawImage
import Param
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.image=DrawImage.Plt_Result()

        # Setup timer
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.aquire_image)
        self.timer.start(5)

        self.camera=Camera.Camera()
        
        # params
        self.param=Param.Param()
        self.param.load_param(self.param.path+'Param.plk')
        
        # trigger mode is turned on in setup_camera()
        if not self.camera.setup_camera():
            self.close()

        self.camera.set_gain(self.param.GAIN) # set gain to 10.6 db
        #self.camera.auto_gain() # set gain to auto
        self.camera.set_exposure_time(self.param.EXPOSURE) # set exposure time to 100 us
        
        self.camera.start_acquisition()
        
        self.init_UI()


    def init_UI(self):
        # Setup window
        self.setWindowTitle("image")
        self.setGeometry(200,200,2200,1100)  #(300,100,400,300)

        # Set image
        self.status=QtWidgets.QLabel("",self)
        self.status.resize(1500,100)
        self.status.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status.setScaledContents(True)
        self.status.setText("Acquiring image...")
        self.status.setFont(QtGui.QFont("Times", 12))
        self.status.move(0,0)

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
        self.lb_gain.move(1550,50)

        self.btn1=QtWidgets.QPushButton("set Gain",self)
        self.btn1.clicked.connect(self.set_gain)
        self.btn1.resize(200,50)
        self.btn1.move(1900,50)
        
        self.edit_Gain=QtWidgets.QLineEdit(self)
        self.edit_Gain.resize(100,30)
        self.edit_Gain.move(1750,60)
        self.edit_Gain.setText('%s' % self.param.GAIN)

        self.lb_gain_info=QtWidgets.QLabel("Set Gain to %s db" % self.param.GAIN,self)
        self.lb_gain_info.resize(450,50)
        self.lb_gain_info.setScaledContents(True)
        self.lb_gain_info.move(1550,120)

        # set Exposure Time
        self.lb_exposure=QtWidgets.QLabel("Exposure (us):",self)
        self.lb_exposure.resize(200,50)
        self.lb_exposure.setScaledContents(True)
        self.lb_exposure.move(1550,250)

        self.btn_exposure=QtWidgets.QPushButton("set Exposure",self)
        self.btn_exposure.clicked.connect(self.set_exposure)
        self.btn_exposure.resize(200,50)
        self.btn_exposure.move(1900,250)
        
        self.edit_exposure=QtWidgets.QLineEdit(self)
        self.edit_exposure.resize(100,30)
        self.edit_exposure.move(1750,260)
        self.edit_exposure.setText('%s' % self.param.EXPOSURE)

        self.lb_exposure_info=QtWidgets.QLabel("Set Exposure Time to %s us" % self.param.EXPOSURE,self)
        self.lb_exposure_info.resize(450,50)
        self.lb_exposure_info.setScaledContents(True)
        self.lb_exposure_info.move(1550,320)
        
        
        # Set X Y
        self.lb_Xmin=QtWidgets.QLabel("Xmin:",self)
        self.lb_Xmin.resize(170,30)
        self.lb_Xmin.setScaledContents(True)
        self.lb_Xmin.move(1550,500)
        
        self.edit_Xmin=QtWidgets.QLineEdit(self)
        self.edit_Xmin.setText('%s' % self.param.XMIN)
        self.edit_Xmin.resize(70,30)
        self.edit_Xmin.move(1650,500)
        
        self.lb_Xmax=QtWidgets.QLabel("Xmax:",self)
        self.lb_Xmax.resize(170,30)
        self.lb_Xmax.setScaledContents(True)
        self.lb_Xmax.move(1800,500)

        self.edit_Xmax=QtWidgets.QLineEdit(self)
        self.edit_Xmax.setText('%s' % self.param.XMAX)
        self.edit_Xmax.resize(70,30)
        self.edit_Xmax.move(1900,500)

        self.lb_Ymin=QtWidgets.QLabel("Ymin:",self)
        self.lb_Ymin.resize(170,30)
        self.lb_Ymin.setScaledContents(True)
        self.lb_Ymin.move(1550,600)

        self.edit_Ymin=QtWidgets.QLineEdit(self)
        self.edit_Ymin.setText('%s' % self.param.YMIN)
        self.edit_Ymin.resize(70,30)
        self.edit_Ymin.move(1650,600)
        
        self.lb_Ymax=QtWidgets.QLabel("Ymax:",self)
        self.lb_Ymax.resize(170,30)
        self.lb_Ymax.setScaledContents(True)
        self.lb_Ymax.move(1800,600)

        self.edit_Ymax=QtWidgets.QLineEdit(self)
        self.edit_Ymax.setText('%s' % self.param.YMAX)
        self.edit_Ymax.resize(70,30)
        self.edit_Ymax.move(1900,600)

        self.btn2=QtWidgets.QPushButton("calculate OD",self)
        self.btn2.clicked.connect(self.calculate_od)
        self.btn2.resize(450,50)
        self.btn2.move(1550,700)

        self.cal_result=QtWidgets.QLabel("",self)
        self.cal_result.resize(450,30)
        self.cal_result.setScaledContents(True)
        self.cal_result.move(1550,800)


    def set_gain(self):
        try:
            str=self.edit_Gain.text()
            gain=float(str)
            if gain >= 0 and gain < 47.99:
                self.camera.end_acquisition()
                self.camera.set_gain(gain)
                self.lb_gain_info.setText('Set Gain to %s db' % gain)
                self.param.GAIN=gain
                self.camera.start_acquisition()
                
        except:
            if str=='auto' or str=='Auto':
                self.camera.auto_gain()
                self.lb_gain_info.setText('Set Gain to Auto')

    def set_exposure(self):
        try:
            str=self.edit_exposure.text()
            exposure=int(str)
            if exposure >= 0 and exposure <= 5000:
                self.camera.end_acquisition()
                self.camera.set_exposure_time(exposure)
                self.lb_exposure_info.setText('Set Exposure Time to %s us' % exposure)
                self.param.EXPOSURE=exposure
                self.camera.start_acquisition()
                
        except:
            if str=='auto' or str=='Auto':
                self.camera.auto_gain()
                self.lb_gain_info.setText('Set Gain to Auto')


    def check_x(self,x):
        if x>self.camera.image_width or x<0:
            raise Exception('Wrong X')


    def check_y(self,y):
        if y>self.camera.image_height or y<0:
            raise Exception('Wrong X')


    def calculate_od(self):
        try:
            xmin=int(self.edit_Xmin.text())
            xmax=int(self.edit_Xmax.text())
            ymin=int(self.edit_Ymin.text())
            ymax=int(self.edit_Ymax.text())
            self.check_x(xmin)
            self.check_x(xmax)
            self.check_y(ymin)
            self.check_x(ymax)
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
        self.timer.stop()
        self.param.save_param(self.param.path+'Param.plk')
        self.camera.release_camera()
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
        try:
            app.camera.release_camera()
        except:
            pass
        print('Error: %s' % ex)
        