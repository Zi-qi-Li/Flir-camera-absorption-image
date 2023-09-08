# Flir Camera Absorption Image
This is a program to acquire absorption image using Flir camera. It acquires image with atoms, image without atoms and background sequentially, and then calculate optical density.

## Preparation
Firstly install Spinnaker SDK at <https://www.flir.com/products/spinnaker-sdk/>

Make sure you can import PySpin after installation.

Do not use pip install pyspin, this will install another lib.

PyQt5 is needed to run with GUI.

## Start
Run Run_in_Sequence_GUI.py to start acquiring absorption image with a GUI.

Run Run_in_Sequence.py to start acquiring without GUI.

Run_in_Seqence_GUI_debug.py will display the original image to make it more convenient to debug.

If cannot setup camera after disconnecting the camera incorrectly, try Release_Camera.py

If you use a different camera, remember to change the serial number in Camera.py. This program only works with camera with this serial number.

## Parameter Range for GUI
Gain: 0 - 47.99 db

Exposure Time: 0 - unlimited us 
(It seems that the camera itself have a maximun exposure time inside. )

Xmin, Xmax: 0 - 3072

Ymin, Ymax: 0 - 2048

