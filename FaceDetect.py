from __future__ import division
from models import model_a
import cv2
import time
import numpy as np
import base64
import os,sys,shutil
import time

if __name__ == "__main__":

    img_dir = 'images/'
    result_dir = 'result/'

    if os.path.exists(img_dir)==False:
        print("No 'images' Directory!")
        sys.exit()
    if os.path.exists(result_dir) == True:
        shutil.rmtree(result_dir)
    os.mkdir(result_dir)
    
    cnt=0
    with open(result_dir+'images_list.txt','w') as f:
        for i in os.listdir(img_dir):
            img_name=i.strip()
            f.write(img_name+'\n')
            cnt+=1
    
    total_cnt=0
    failure_cnt = 0 
    success_cnt = 0

    f_key =open(result_dir+'images_keypoints.txt','w')
    f_fail =open(result_dir+'images_failed.txt','w')

    with open(result_dir+'images_result.txt','w') as f_o:
        with open(result_dir+'images_list.txt') as f_i:
            for img in f_i:
                if img.find('.jpeg') < 0 and img.find('.jpg') < 0 and img.find('.png') < 0:
                    continue 
                img_name=img.strip()

                if img_name.find(' ') > -1:
                    print('Illegal Name: '+img_name)
                    sys.exit()

                res_string,skeleton_string=model_a.parseImage(img_dir, img_name, result_dir)

                if res_string!='fail':
                    f_o.write(res_string+'\n')
                    f_key.write(skeleton_string+'\n')
                    success_cnt+=1
                    print('Success: ', success_cnt, img_name)
                else:
                    f_fail.write(img_name+'\n')
                    failure_cnt+=1
                    print('Failure: ', failure_cnt, img_name)
                total_cnt+=1

                time.sleep(0.5)

    print('Total: ', total_cnt)
