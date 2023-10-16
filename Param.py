# class to save parameters and configurations in GUI

import pickle
import os

class Param:
    def __init__(self):
        self.path=os.getcwd()+"/param/"

        # params
        self.GAIN=10.6
        self.EXPOSURE=100
        
        self.XMIN=0
        self.XMAX=3072
        self.YMIN=0
        self.YMAX=2048

        self.DIS_XMIN=0
        self.DIS_XMAX=3072
        self.DIS_YMIN=0
        self.DIS_YMAX=2048
        
        self.CURRENT_IMAGE_PATH=os.getcwd()+"/"
        self.IMAGE_SAVING_PATH=os.getcwd()+"/"

        try:
            test_file = open(self.path+"test.txt", 'w+')
            test_file.close()
            os.remove(test_file.name)
        except IOError:
            os.makedirs(self.path)

    def load_param(self,filename):
        # Try to load previous parameters. If fail, use default parameters
        try:
            #param=np.load(filename,allow_pickle=True)
            with open(filename, 'rb') as file:
                param = pickle.loads(file.read())
            self.GAIN=param.GAIN
            self.EXPOSURE=param.EXPOSURE
            
            self.XMIN=param.XMIN
            self.XMAX=param.XMAX
            self.YMIN=param.YMIN
            self.YMAX=param.YMAX

            self.DIS_XMIN=param.DIS_XMIN
            self.DIS_XMAX=param.DIS_XMAX
            self.DIS_YMIN=param.DIS_YMIN
            self.DIS_YMAX=param.DIS_YMAX
            
            self.CURRENT_IMAGE_PATH=param.CURRENT_IMAGE_PATH
            self.IMAGE_SAVING_PATH=param.IMAGE_SAVING_PATH
            pass
            
        except:
            pass

    def save_param(self,filename):
        #np.save(filename,self,allow_pickle=True)
        with open(filename,'wb') as f:
            f.write(pickle.dumps(self))