import pickle
import os

class Param:
    def __init__(self):
        # params
        self.path=".\\param\\"
        self.GAIN=10.6
        self.XMIN=0
        self.XMAX=3072
        self.YMIN=0
        self.YMAX=2048
        self.EXPOSURE=100

        try:
            test_file = open(self.path+"test.txt", 'w+')
            test_file.close()
            os.remove(test_file.name)
        except IOError:
            os.makedirs(self.path)

    def load_param(self,filename):
        try:
            #param=np.load(filename,allow_pickle=True)
            with open(filename, 'rb') as file:
                param = pickle.loads(file.read())
            self.GAIN=param.GAIN
            self.XMIN=param.XMIN
            self.XMAX=param.XMAX
            self.YMIN=param.YMIN
            self.YMAX=param.YMAX
            self.EXPOSURE=param.EXPOSURE
        except:
            pass

    def save_param(self,filename):
        #np.save(filename,self,allow_pickle=True)
        with open(filename,'wb') as f:
            f.write(pickle.dumps(self))