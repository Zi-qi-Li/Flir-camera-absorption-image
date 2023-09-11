import Camera

# This is used to reset camera after disconnecting the camera accidentally.
# If you are unable to set camera, try this first.
def Release_camera():
    try:
        camera=Camera.Camera()
        #camera.init_camera()
        try:
            camera.start_acquisition()
            camera.end_acquisition()
        except Exception as ex:
            print('Error: %s' % ex)
        camera.release_camera()
    except Exception as ex:
        print('Error: %s' % ex)

if __name__ == "__main__":
    Release_camera()