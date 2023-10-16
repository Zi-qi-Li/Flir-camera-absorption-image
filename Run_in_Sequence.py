# acquire image without GUI

import numpy as np
import Camera
import DrawImage


def aquire_image():
    try:
        if not camera.acquire_single_image():
            return False
    except Exception as ex:
        print('Error: %s' % ex)
        return False
    if camera.image_cnt > 0 and camera.image_cnt % 3 == 0 :
        
        # Calculate OD
        try:
            background=camera.get_image(camera.image_cnt)
            no_atom=camera.get_image(camera.image_cnt-1)
            atom=camera.get_image(camera.image_cnt-2)
            od=-np.log((atom-background)/(no_atom-background),dtype=np.float32)
        
            image.plt_result(background,no_atom,atom,od)
            image.save_figure(camera.path+'result_%d'%(camera.image_cnt//3))
            #image.show_figure()
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
        camera=Camera.Camera()
        
        # trigger mode is turned on in setup_camera()
        if not camera.setup_camera():
                raise Exception("Unable to set camera")
        
        camera.set_gain(10.6) # set gain to 10.6 db
        #camera.auto_gain()

        camera.start_acquisition()

        image=DrawImage.Plt_Result()

        while True:
            try:
                if not camera.acquire_single_image():
                    break
            except Exception as ex:
                print('Error: %s' % ex)
                break
            if camera.image_cnt > 0 and camera.image_cnt % 3 == 0 :
                
                # Calculate OD
                try:
                    background=camera.get_image(camera.image_cnt)
                    no_atom=camera.get_image(camera.image_cnt-1)
                    atom=camera.get_image(camera.image_cnt-2)
                    od=-np.log((atom-background)/(no_atom-background),dtype=np.float32)
                
                    image.plt_result(background,no_atom,atom,od)
                    image.save_figure(camera.path+'result_%d'%(camera.image_cnt//3))
                    #image.show_figure()
                except Exception as ex:
                    print('Error: %s' % ex)
                    break


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

        
        camera.end_acquisition()
        camera.auto_gain()

        camera.release_camera()
        del camera
    except Exception as ex:
        try:
            camera.release_camera()
            del camera
        except:
            pass
        print('Error: %s' % ex)