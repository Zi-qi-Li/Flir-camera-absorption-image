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

If cannot setup camera after disconnecting the camera accidentally, try  Release_Camera.py

## Parameter Range for GUI
Gain: 0 - 47.99 db

Exposure Time: 0 - 5000 us

Xmin, Xmax: 0 - 3072

Ymin, Ymax: 0 - 2048

