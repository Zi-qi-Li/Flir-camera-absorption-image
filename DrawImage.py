import numpy as np
from PIL import Image 
import sys
import matplotlib
matplotlib.use('agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def convert_image(path,inputname,outputname):
    image16=np.load(path+inputname+".npy")
    # convert to uint32 array
    image32=np.array(image16,dtype=np.uint32)

    #image32=np.zeros((1000,500),dtype=np.uint32)
    #for i in range(1000):
    #    for j in range(500):
    #        image32[i,j]=2**15-1
    
    im=Image.fromarray(image32,mode='I')
    im.save(path+outputname+".png")
    print("Converted %s to %s" % (inputname+".npy",outputname+".png"))

def array16_to_image(array16,path,outputname):
    #covert uint16 array to image
    array32=np.array(array16,dtype=np.uint32)
    im=Image.fromarray(array32,mode='I')
    im.save(path+outputname+".png")
    print("Converted data to %s" % (outputname+".png"))

def array32f_to_image(array32f,path,outputname):
    #covert float32 array to image
    im=Image.fromarray(array32f,mode='F')
    im.save(path+outputname+".png")
    print("Converted data to %s" % (outputname+".png"))

class Plt_Result:
    def __init__(self):
        #plt.ioff()
        self.figure=plt.figure(figsize=(15,10))
    
    def plt_result(self,background,no_atom,atom,od,xmin,xmax,ymin,ymax):
        self.figure.clear()

        nxsteps = (xmax-xmin)//400 # Draw the figure every nsteps pixels. This makes it much faster.
        if nxsteps<=0:
            nxsteps = 1

        nysteps = (ymax-ymin)//400
        if nysteps<=0:
            nysteps = 1

        print('nxsteps = %d, nysteps = %d'%(nxsteps,nysteps))
        xlist=np.linspace(xmin+1,xmax,xmax-xmin)
        ylist=np.linspace(ymin+1,ymax,ymax-ymin)
        
        #c=xlist[::nxsteps]
        #b=ylist[::nysteps]
        #a=background[ymin:ymax:nysteps,xmin:xmax:nxsteps]
        
        sub1 = self.figure.add_subplot(223)
        im1=sub1.pcolormesh(xlist[::nxsteps],ylist[::nysteps],background[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        sub1.set_title('background')
        self.figure.colorbar(im1,ax=sub1)


        sub2 = self.figure.add_subplot(222)
        im2=sub2.pcolormesh(xlist[::nxsteps],ylist[::nysteps],no_atom[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        sub2.set_title('no atom')
        self.figure.colorbar(im2,ax=sub2)
        
        sub3 = self.figure.add_subplot(221)
        im3=sub3.pcolormesh(xlist[::nxsteps],ylist[::nysteps],atom[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        sub3.set_title('atom')
        self.figure.colorbar(im3,ax=sub3)
        
        sub4 = self.figure.add_subplot(224)
        im4=sub4.pcolormesh(xlist[::nxsteps],ylist[::nysteps],od[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        sub4.set_title('optical density')
        self.figure.colorbar(im4,ax=sub4)
        print('Plot result')


    #def show_figure(self):
    #    self.figure.show()

    def plt_od(self,od,xmin,xmax,ymin,ymax,od_xmin,od_xmax,od_ymin,od_ymax):
        self.figure.clear()
        sub = self.figure.add_subplot(111)
        
        
        nxsteps = (xmax-xmin)//600 # Draw the figure every nsteps pixels. This makes it much faster.
        if nxsteps<=0:
            nxsteps = 1

        nysteps = (ymax-ymin)//600
        if nysteps<=0:
            nysteps = 1

        #print('nxsteps = %d, nysteps = %d'%(nxsteps,nysteps))

        # Draw colormap
        xlist=np.linspace(xmin+1,xmax,xmax-xmin)
        ylist=np.linspace(ymin+1,ymax,ymax-ymin)
        im1=sub.pcolormesh(xlist[::nxsteps],ylist[::nysteps],od[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        # Draw region to calculate OD
        sub.plot([od_xmin,od_xmax],[od_ymax,od_ymax],color='black')
        sub.plot([od_xmin,od_xmax],[od_ymin,od_ymin],color='black')
        sub.plot([od_xmin,od_xmin],[od_ymin,od_ymax],color='black')
        sub.plot([od_xmax,od_xmax],[od_ymin,od_ymax],color='black')
        sub.set_title('optical density')
        self.figure.colorbar(im1,ax=sub)


    def save_figure(self,filename):
        self.figure.savefig(filename+".png")
        #print('Saved figure as %s' % (filename+".png"))

    def clear(self):
        self.figure.clear()


    def release(self):
        pass
    
class QMatplotlib(FigureCanvasQTAgg):
    def __init__(self,window_magnification):
        # Change the size of UI according to the resolution of screen
        self.window_magnification=window_magnification
        
        self.image=Figure(figsize=(15,10),dpi=100)
        super(QMatplotlib,self).__init__(self.image)
        

    def plt_image(self,od,xmin,xmax,ymin,ymax):
        self.image.clear()
        self.axes=self.image.add_subplot(111)
        nxsteps = (xmax-xmin)//600 # Draw the figure every nsteps pixels. This makes it much faster.
        if nxsteps<=0:
            nxsteps = 1

        nysteps = (ymax-ymin)//int(600*self.window_magnification)
        if nysteps<=0:
            nysteps = 1

        #print('nxsteps = %d, nysteps = %d'%(nxsteps,nysteps))

        # Draw colormap
        xlist=np.linspace(xmin+1,xmax,xmax-xmin)
        ylist=np.linspace(ymin+1,ymax,ymax-ymin)
        im1=self.axes.pcolormesh(xlist[::nxsteps],ylist[::nysteps],od[ymin:ymax:nysteps,xmin:xmax:nxsteps])
        
        self.plt1,=self.axes.plot([],[],color='black')
        self.plt2,=self.axes.plot([],[],color='black')
        self.plt3,=self.axes.plot([],[],color='black')
        self.plt4,=self.axes.plot([],[],color='black')


        self.axes.set_title('optical density')
        self.image.colorbar(im1,ax=self.axes)

    def plt_od_region(self,od_xmin,od_xmax,od_ymin,od_ymax):
        # Draw region to calculate OD
        self.plt1.set_data([od_xmin,od_xmax],[od_ymax,od_ymax])
        self.plt2.set_data([od_xmin,od_xmax],[od_ymin,od_ymin])
        self.plt3.set_data([od_xmin,od_xmin],[od_ymin,od_ymax])
        self.plt4.set_data([od_xmax,od_xmax],[od_ymin,od_ymax])
        '''
        self.axes.plot([od_xmin,od_xmax],[od_ymax,od_ymax],color='black')
        self.axes.plot([od_xmin,od_xmax],[od_ymin,od_ymin],color='black')
        self.axes.plot([od_xmin,od_xmin],[od_ymin,od_ymax],color='black')
        self.axes.plot([od_xmax,od_xmax],[od_ymin,od_ymax],color='black')'''

    def release(self):
        self.image.clear()

if __name__ == "__main__":

    print("*** IMAGE CONVERSION STARTS ***")
    
    path=".\\image\\"

    print("Image to be converted: %d" % (sys.argv.__len__()-1))
    
    for i in range(1,sys.argv.__len__()):
        filename=sys.argv[i]
        print("Converting image %d: %s..." % (i,filename))
        convert_image(path,filename,filename)
    #filename='Acquisition_3_od'
    #convert_image(path,filename,filename)
    #data=np.load(path+"Acquisition_1+background.npy")
    #data2=np.array(data,dtype=np.float32)
    #array32f_to_image(data2,path,'test')

    print("*** IMAGE CONVERSION ENDS ***\n")
