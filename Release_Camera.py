import Camera

# This is used to reset camera after disconnecting the camera accidentally.
# If you are unable to set camera, try this first.

try:
    camera=Camera.Camera()
    camera.init_camera()
    try:
        camera.start_acquisition()
        camera.end_acquisition()
    except:
        print('Error')
    camera.release_camera()
except Exception as ex:
    print('Error: %s' % ex)
