import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image,ImageTk
from threading import Thread
import os
from multiprocessing import  Process

import tkinter as tk 

path=".\\image\\"

bg=np.load(path+"Acquisition_1+background.npy")
na=np.load(path+"Acquisition_2_no_atom.npy")
at=np.load(path+"Acquisition_3_atom.npy")
od=np.load(path+"Acquisition_3_od.npy")

im=plt.figure(figsize=(10,10))
ny=len(bg)
nx=len(bg[0])
nsteps=3
xlist=np.linspace(1,nx,nx)
ylist=np.linspace(1,ny,ny)

sub1 = im.add_subplot(221)
im1=sub1.pcolormesh(xlist[::nsteps],ylist[::nsteps],bg[::nsteps,::nsteps])
sub1.set_title('background')
im.colorbar(im1,ax=sub1)

sub2 = im.add_subplot(222)
im2=sub2.pcolormesh(xlist[::nsteps],ylist[::nsteps],na[::nsteps,::nsteps])
sub2.set_title('no atom')
im.colorbar(im2,ax=sub2)

sub3 = im.add_subplot(223)
im3=sub3.pcolormesh(xlist[::nsteps],ylist[::nsteps],at[::nsteps,::nsteps])
sub3.set_title('atom')
im.colorbar(im3,ax=sub3)

sub4 = im.add_subplot(224)
im4=sub4.pcolormesh(xlist[::nsteps],ylist[::nsteps],od[::nsteps,::nsteps])
sub4.set_title('optical density')
im.colorbar(im4,ax=sub4)

#im.show()
im.savefig(path+"test.png")

c=od[20:40,30:40]
b=sum(od[20:40,30:40])
a=sum(sum(od[20:40,30:40]))
a2=sum(a)

def run():
    window=tk.Toplevel()
    window.title("Window")
    window.geometry("1500x1000")
    img = Image.open(path+'result_1.png')  # 打开图片
    photo = ImageTk.PhotoImage(img)  # 用PIL模块的PhotoImage打开
    imglabel = tk.Label(window, image=photo)
    imglabel.grid(row=0, column=0, columnspan=3)

    tk.Label(window, text="Answer:").grid(row=1, column=0)

    answerEntry = tk.Entry(window)
    btn = tk.Button(window, text="Submit", command='submit')

    answerEntry.grid(row=1, column=1)
    btn.grid(row=1, column=2)
    window.mainloop()

run()
os.chmod()