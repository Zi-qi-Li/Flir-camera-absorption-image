import os
import PySpin
import numpy as np
import time


class Camera:
    def __init__(self):
        # Set path where images are saved
        print("\n*** INITIALIZING CAMERA ***")
        
        self.path=".\\image\\"
        if  not self.check_path():
            os.makedirs(self.path)
            print('Makedirs :%s' % self.path)
        
        # Serial number of camera, this prevents using other cameras connected to the computer by mistake
        self.cam_serial='23365134'

        # number of images which have already been acquired
        self.image_cnt=0
        
        self.find_camera()
        
        #self.create_image_processor()

        print("*** INITIALIZATION COMPLETE ***\n")


    def find_camera(self):

        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()

        # Get current library version
        version = self.system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

        # Retrieve list of cameras from the system
        cam_list = self.system.GetCameras()

        num_cameras = cam_list.GetSize()

        print('Number of cameras detected: %d' % num_cameras)

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()

            # Release system instance
            self.system.ReleaseInstance()

            raise Exception("Not enough cameras")

        # Run example on each camera
        #for i, cam in enumerate(cam_list):

        #    print('Running example for camera %d...' % i)

        #    result &= self.run_single_camera(cam)
        #    print('Camera %d example complete... \n' % i)

        # Release reference to camera
        # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
        # cleaned up when going out of scope.
        # The usage of del is preferred to assigning the variable to None.
        #del cam

        # Clear camera list before releasing system
        isfound = False

        for i, runningCam in enumerate(cam_list):
            device_serial_number = runningCam.TLDevice.DeviceSerialNumber.GetValue()
            print("Camera detected: %s" % device_serial_number)
            if device_serial_number == self.cam_serial:
                self.cam = runningCam
                isfound = True
                try:
                    self.cam.EndAcquisition()   # I have the impression it prevents from rising an error if an acquisition got aborted before
                except:
                    pass
        if not isfound:# or str(type(self.cam)) != "<class 'PySpin.PySpin.CameraPtr'>":
            # Clear camera list before releasing system
            cam_list.Clear()

            # Release system instance
            self.system.ReleaseInstance()

            raise Exception("No camera matches")
        
        del runningCam

        cam_list.Clear()
        print("Camera found")
        # Release system instance
        #self.system.ReleaseInstance()

        #input('Done! Press Enter to exit...')


    def set_path(self,new_path):
        # set directory to save data
        if not self.check_path():
            print('Set path %s failed...' % new_path)
            return False

        print('Set path %s successfully.' % new_path)
        self.path=new_path
        return True


    def check_path(self):
        # check permissions to write in the directory
        try:
            test_file = open(self.path+"test.txt", 'w+')
        except IOError:
            #print('Unable to write to current directory. Please check permissions.')
            return False
        test_file.close()
        os.remove(test_file.name)
        return True

    def init_camera(self):
        try:
            self.cam.Init()
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)


    def setup_camera(self):
        """
        This function configures the camera basic settings.
         :return: True if successful, False otherwise.
         :rtype: bool
        """
    
        print('\n*** CONFIGURING ACQUISITION SETTINGS OF CAMERA ***')

        try:
            result = True
            # Initialize camera
            self.cam.Init()
            
            # Retrieve GenICam nodemap
            nodemap = self.cam.GetNodeMap()
            #nodemap = self.cam.GetTLDeviceNodeMap()
            
            if self.cam.DeviceLinkThroughputLimit.GetAccessMode() != PySpin.RW:
                print('Unable to set device link throughput limit (node retrieval). Aborting...')
                return False
            self.cam.DeviceLinkThroughputLimit.SetValue(43000000)
            print('Device link throughput limit set to 43000000')
            
            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
            print('Trigger mode disabled...')
            
            # Set TriggerSelector to FrameStart
            # For this example, the trigger selector should be set to frame start.
            # This is the default for most cameras.
            if self.cam.TriggerSelector.GetAccessMode() != PySpin.RW:
                print('Unable to get trigger selector (node retrieval). Aborting...')
                return False
            self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
            print('Trigger selector set to frame start...')
            
            # Select trigger source
            # The trigger source must be set to hardware or software while trigger
    		# mode is off.
            if self.cam.TriggerSource.GetAccessMode() != PySpin.RW:
                print('Unable to set trigger source (node retrieval). Aborting...')
                return False
            self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
            print('Trigger source set to hardware...')

            # Set trigger activation
            if self.cam.TriggerActivation.GetAccessMode() != PySpin.RW:
                print('Unable to set trigger activation. Aborting...')
                return False
            self.cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
            print('Trigger activation set to rising edge...')

            # # Select trigger delay
            # # Acquisition will start at a specified time after the trigger. Sync 
            # if self.cam.TriggerDelay.GetAccessMode() != PySpin.RW:
            #     print('Unable to set trigger delay (node retrieval). Aborting...')
            #     return False

            # #This value seems a bit inaccurate
            # self.cam.TriggerDelay.SetValue(30)
            # print('Trigger delay set to 30us...')

            # Turn off automatic exposure mode
            #
            # *** NOTES ***
            # Automatic exposure prevents the manual configuration of exposure
            # times and needs to be turned off for this example. Enumerations
            # representing entry nodes have been added to QuickSpin. This allows
            # for the much easier setting of enumeration nodes to new values.
            #
            # The naming convention of QuickSpin enums is the name of the
            # enumeration node followed by an underscore and the symbolic of
            # the entry node. Selecting "Off" on the "ExposureAuto" node is
            # thus named "ExposureAuto_Off".
            #
            # *** LATER ***
            # Exposure time can be set automatically or manually as needed. This
            # example turns automatic exposure off to set it manually and back
            # on to return the camera to its default state.
    
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
            
            if self.cam.ExposureMode.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure mode to trigger width. Aborting...')
                return False
            #self.cam.ExposureMode.SetValue(PySpin.ExposureMode_TriggerWidth)
            #print('Exposure time is set to be Trigger Wdith \n')
            self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)
            print('Exposure time is set to be Timed (Fixed) ')
            
            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False
            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = min(self.cam.ExposureTime.GetMax(), 200)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Exposure time set to %s us...' % exposure_time_to_set)
            
            # Select trigger overlap
            # Acquisition will start at a specified time after the trigger. Sync 
            if self.cam.TriggerOverlap.GetAccessMode() != PySpin.RW:
                print('Unable to set trigger overlap (node retrieval). Aborting...')
                return False
            #This value seems a bit inaccurate
            self.cam.TriggerOverlap.SetValue(PySpin.TriggerOverlap_ReadOut)
            print('Trigger overlap allowed')
            
            # Change Gain Conversion Mode to HCG
            #node_gain_conversion = PySpin.CEnumerationPtr(nodemap.GetNode('GainConversion'))
            #if not PySpin.IsReadable(node_gain_conversion) or not PySpin.IsWritable(node_gain_conversion):
            #    print('Unable to set GainConversion 1 .. Aborting...')
            #    return False
            
            #node_hcg = node_gain_conversion.GetEntryByName('HCG')
            #if not PySpin.IsReadable(node_hcg):
            #    print('Unable to set GainConversion 2 .. Aborting...')
            #    return False
            #node_gain_conversion.SetIntValue(node_hcg.GetValue())

            ### Turn off binning
            #if self.cam.BinningHorizontal.GetAccessMode() != PySpin.RW:
            #    print('Unable to set horizontal binning. Aborting...')
            #    return False
            #self.cam.BinningHorizontal.SetValue(1)
            #if self.cam.BinningVertical.GetAccessMode() != PySpin.RW:
            #    print('Unable to set vertical binning. Aborting...')
            #    return False
            #self.cam.BinningVertical.SetValue(1)

            if (self.cam.Width.GetAccessMode() != PySpin.RO and self.cam.Width.GetAccessMode() != PySpin.RW):
                print('Unable to check expected image size. Aborting...')
                return False
            if (self.cam.Height.GetAccessMode() != PySpin.RO and self.cam.Height.GetAccessMode() != PySpin.RW):
                print('Unable to check expected image size. Aborting...')
                return False
            self.image_width  = self.cam.Width.GetValue()
            self.image_height = self.cam.Height.GetValue()
            print("Expected image size: %dpx x %dpx"%(self.image_width,self.image_height))

            if self.cam.PixelFormat.GetAccessMode() != PySpin.RW:
                print('Unable to set PixelFormat. Aborting...')
                return False
            self.cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono16)

            #Set trigger mode back to on
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to enable trigger mode (node retrieval). Aborting...')
                return False
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            print('Trigger mode enabled...')

            self.image = np.zeros((3,self.image_height,self.image_width),dtype=np.uint16)
            

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        print('*** CONFIGURATION COMPLETE ***\n')
        return result


    def trigger_mode_on(self):
        try:
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to enable trigger mode (node retrieval). Aborting...')
                return False
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
            print('Trigger mode enabled...')
            

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    def trigger_mode_off(self):
        try:
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
            print('Trigger mode disabled...')
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    def set_exposure_time(self,time):
        try:
            if time<=0 or time >200:
                return False
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
            
            if self.cam.ExposureMode.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure mode to trigger width. Aborting...')
                return False
            #self.cam.ExposureMode.SetValue(PySpin.ExposureMode_TriggerWidth)
            #print('Exposure time is set to be Trigger Wdith \n')
            self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)
            print('Exposure time is set to be Timed (Fixed) ')
            
            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False
            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = min(time, 200)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Exposure time set to %s us...' % exposure_time_to_set)
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return True

    def set_gain(self,gain):
        # :Param gain: Gain to be set. In the unit of db.
        try:
            if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable GainAuto. Aborting...')
                return False
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            
            print('GainAuto disabled...')

            if self.cam.Gain.GetAccessMode() != PySpin.RW:
                print('Unable to set Gain. Aborting...')
                return False
            self.cam.Gain.SetValue(gain)
            print('Set Gain to %f' % gain)
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    def auto_gain(self):
        # enable GainAuto
        try:
            if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable GainAuto. Aborting...')
                return False
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)

            print('GainAuto enabled...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    def set_continuous_mode(self):
        # Set acquisition mode to continuous
        #
        #  *** NOTES ***
        #  Because the example acquires and saves 10 images, setting acquisition
        #  mode to continuous lets the example finish. If set to single frame
        #  or multiframe (at a lower number of images), the example would just
        #  hang. This would happen because the example has been written to
        #  acquire 10 images while the camera would have been programmed to
        #  retrieve less than that.
        #
        #  Setting the value of an enumeration node is slightly more complicated
        #  than other node types. Two nodes must be retrieved: first, the
        #  enumeration node is retrieved from the nodemap; and second, the entry
        #  node is retrieved from the enumeration node. The integer value of the
        #  entry node is then set as the new value of the enumeration node.
        #
        #  Notice that both the enumeration and the entry nodes are checked for
        #  availability and readability/writability. Enumeration nodes are
        #  generally readable and writable whereas their entry nodes are only
        #  ever readable.
        #
        #  Retrieve enumeration node from nodemap

        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = PySpin.CEnumerationPtr(self.cam.GetNodeMap().GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsReadable(node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')


    def reset_camera(self):
        """
        This function configures some exposure settings of the camera back.
         :return: True if successful, False otherwise.
         :rtype: bool
        """
    
        print('Resetting camera...')

        try:
            result = True
            # Initialize camera
            if not self.cam.IsInitialized():
                self.cam.Init()
                                    
            # Turn off automatic exposure mode
            #
            # *** NOTES ***
            # Automatic exposure prevents the manual configuration of exposure
            # times and needs to be turned off for this example. Enumerations
            # representing entry nodes have been added to QuickSpin. This allows
            # for the much easier setting of enumeration nodes to new values.
            #
            # The naming convention of QuickSpin enums is the name of the
            # enumeration node followed by an underscore and the symbolic of
            # the entry node. Selecting "Off" on the "ExposureAuto" node is
            # thus named "ExposureAuto_Off".
            #
            # *** LATER ***
            # Exposure time can be set automatically or manually as needed. This
            # example turns automatic exposure off to set it manually and back
            # on to return the camera to its default state.
            
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False
    
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
            
            if self.cam.ExposureMode.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure mode to trigger width. Aborting...')
                return False
            
            self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)
            print('Exposure time is set to be Timed (Fixed)')

            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False
            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = min(self.cam.ExposureTime.GetMax(), 100)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Shutter time set to %s us...' % exposure_time_to_set)
            

            # Ensure trigger mode off
            # The trigger must be disabled in order to configure whether the source
            # is software or hardware.
            if self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False
    
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    
            print('Trigger mode disabled...')
            
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        print('Camera reset')
        return result


    def start_acquisition(self):
        print('\n*** IMAGE ACQUISITION START ***')
        try:
            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images. Because the example calls for the
            #  retrieval of 10 images, continuous mode has been set.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.cam.BeginAcquisition()

            print('Acquiring images...')
        
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        return True


    def end_acquisition(self):
            #  End acquisition
            #
            #  *** NOTES ***
            #  Ending acquisition appropriately helps ensure that devices clean up
            #  properly and do not need to be power-cycled to maintain integrity.
        try:
            self.cam.EndAcquisition()
            print('*** IMAGE ACQUISITION END ***\n')
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        
        
        return True
            

    def acquire_single_image(self):
        # Retrieve, convert, and save images

        # Create ImageProcessor instance for post processing images
        try:

            #  Retrieve next received image
            #
            #  *** NOTES ***
            #  Capturing an image houses images on the camera buffer. Trying
            #  to capture an image that does not exist will hang the camera.
            #
            #  *** LATER ***
            #  Once an image from the buffer is saved and/or no longer
            #  needed, the image must be released in order to keep the
            #  buffer from filling up.
            image_result = self.cam.GetNextImage(0)


            #  Ensure image completion
            #
            #  *** NOTES ***
            #  Images can easily be checked for completion. This should be
            #  done whenever a complete image is expected or required.
            #  Further, check image status for a little more insight into
            #  why an image is incomplete.
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                return False
            else:

                self.image_cnt+=1
                self.image[(self.image_cnt-1)%3][:][:] = image_result.GetNDArray()
                print('Complete image %d' % self.image_cnt)
                #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

        except PySpin.SpinnakerException as ex:
            #print('Error: %s' % ex)
            return False
        
        return True


    def auto_filename(self,index=-1):
        if index <= 0:
            return "Acquisition_%d" % self.image_cnt
        return "Acquisition_%d" % index


    def save_data(self,outputname,index=-1):
        #  Save image
        #
        #  *** NOTES ***
        #  The standard practice of the examples is to use device
        #  serial numbers to keep images of one device from
        #  overwriting those of another.
        if index<=0:
            np.save(self.path+outputname,self.image[(self.image_cnt-1)%3][:][:])
        else:
            np.save(self.path+outputname,self.image[(index-1)%3][:][:])
        #self.image.Save(self.path + filename)
        print('Data saved at %s' % (self.path + outputname + '.npy'))


    def get_image(self,index=-1):
        if index <= 0:
            return self.image[(self.image_cnt-1)%3][:][:]
        return self.image[(index-1)%3][:][:]


    def print_device_info(self):
        # Unless function. Copied from example, cannot run successfully.
        """
        This function prints the device information of the camera from the transport
        layer; please see NodeMapInfo example for more in-depth comments on printing
        device information from the nodemap.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """

        print('\n*** DEVICE INFORMATION ***')

        try:
            result = True
            node_device_information = PySpin.CCategoryPtr(self.cam.GetNodeMap().GetNode('DeviceInformation'))

            if PySpin.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                for feature in features:
                    node_feature = PySpin.CValuePtr(feature)
                    print('%s: %s' % (node_feature.GetName(),
                                    node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

            else:
                print('Device control information not readable.')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        print('*** DEVICE INFORMATION END***\n')
        return result


    def release_camera(self):
        try:
            self.end_acquisition()
        except:
            pass
        print('\n*** RELEASING CAMERA ***')
        try:
            self.trigger_mode_off()
            self.reset_camera()
            #self.configure_default_mode()
            self.cam.DeInit()
            # Release reference to camera
            # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
            # cleaned up when going out of scope.
            # The usage of del is preferred to assigning the variable to None.
            del self.cam

            # Release system instance
            self.system.ReleaseInstance()
            del self.system
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

        
        
        print('*** CAMERA RELEASED ***\n')


if __name__ == "__main__":
    try:
        camera=Camera()

        if not camera.setup_camera():
            raise Exception("Unable to set camera")
        
        camera.trigger_mode_off()

        
        camera.set_gain(10.6) # set gain to 10.6 db
        camera.start_acquisition()
        #time.sleep(1)
        
        if camera.acquire_single_image():
            camera.save_data('test')
        
        #time.sleep(1)
        camera.end_acquisition()
        #camera.auto_gain()
        
        camera.release_camera()
        del camera
    
    except Exception as ex:
        try:
            camera.release_camera()
        except:
            pass
        print('Error: %s' % ex)