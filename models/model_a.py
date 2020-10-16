"""
This model is Baidu Hand Keypoint Detector API
APP_ID is 19251377, API_KEY is 'Zune7nva3cS6LcXZoj7lEN9r'
SECRET_KEY is '1pIzEKLfP3xUQ4UbRpM5ZUwHmsE3eVOd'
剩余可用量：50000次图片检测，See https://ai.baidu.com/ai-doc/FACE/yk37c1u4t for more details.
"""
from __future__ import division
import cv2
import time
import numpy as np
import base64
import os,sys
from .model_a_src.aip import AipFace
APP_ID='22770491'
API_KEY='nsjC2B2HefNFqR818zYD4HhZ'
SECRET_KEY='Muwbnt1itag0b4AMW200gNtO4cBQDi7n'

'''
150点示例图：https://ai.bdstatic.com/file/4F9308E3218642B896306DE4200FAE2A
1. 上左：28 x 26 y; 上右 45 x 43 y 取平均
2. 左边 72 
3. 右边 83
4. 下边 121和122 中间的 x 121 122 取平均的y
'''
def getSkeletonStr(points):
    skeleton_str=''
    for i in range(150):
        try:
            x=points[i][0]
            y=points[i][1]
            skeleton_str+=' '+str(x)+' '+str(y)
        except Exception:
            skeleton_str+=' Placeholder Placeholder'
    return skeleton_str

def drawSkeleton(points, frame, color=(0, 0, 255)):
    left_up=(points[28][0],points[26][1])
    right_up=(points[45][0],points[43][1])
    bottom=(int((points[121][0]+points[122][0])/2.0),int((points[121][1]+points[122][1])/2.0))
    x1=points[72][0]
    y1=int((left_up[1]+right_up[1])/2)
    x2=points[83][0]
    y2=bottom[1]
    cv2.rectangle(frame, (x1,y1), (x2,y2), (255, 255, 0), 1)
    cv2.circle(frame, left_up, 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    cv2.circle(frame, right_up, 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    cv2.circle(frame, points[72], 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    cv2.circle(frame, points[83], 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    cv2.circle(frame, bottom, 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
    width=x2-x1
    height=y2-y1
    ratio=float(width/height)
    return ratio,frame

def getContent(filePath):
    with open(filePath, 'rb') as fp:
        str_url = base64.b64encode(fp.read())
        str_url=str(str_url,'utf-8')
        return str_url

def parse(frame, frameCopy, img_path):
    res_string=''
    imageType = "BASE64"
    client=AipFace(APP_ID, API_KEY, SECRET_KEY)
    image= getContent(img_path)  
    options = {}
    options["face_field"] = "expression,landmark150,emotion,rotation,angle,yaw"
    options["max_face_num"] = 1
    content = ''
    points=[]
    status = 'success'
    status_desc = ''

    try:

        content=client.detect(image,imageType,options)


        if content:
           data=content
           result=data['result']
           face=result['face_list'][0]
           angle=face['angle']['yaw']
           #三维旋转之左右旋转角[-90(左), 90(右)]
           expression=face['expression']['type']
           #expression_level=face['expression']['probability']
           #angry:愤怒 disgust:厌恶 fear:恐惧 happy:高兴 sad:伤心 surprise:惊讶 neutral:无情绪
           emotion=face['emotion']['type']
           #emotion_level=face['emotion']['probability']
           if float(angle) < -10:
               res_string+=' 左偏'+str(angle)+'度'
           elif float(angle) > 10:
               res_string+=' 右偏'+str(angle)+'度'
           else:
               res_string+=' 无偏移'
           res_string+=' '+expression+' '+emotion
           cnt_part=1
           for point in face['landmark150']:
               #print(point)
               value=face['landmark150'][point]
               pin=(int(value['x']),int(value['y']))
               points.append(pin)
               cnt_part+=1

    
        res,frame=drawSkeleton(points, frame, (0, 0, 255))
        skeleton_str=getSkeletonStr(points)
        res_string+=' '+str(np.around(res, decimals=2))
        return status, status_desc, frame, res_string, skeleton_str

    except Exception as e:
        if content=='':
            content = str(repr(e))
        return 'error',content,'','',''



def parseImage(img_dir, img_name, result_dir):
    if os.path.exists(result_dir+'images_visualization')==False:
        os.mkdir(result_dir+'images_visualization')
    res_string=str(img_name)
    skeleton_string=str(img_name)
    img_path=os.path.join(img_dir,img_name)
    frame=cv2.imread(img_path)
    frameCopy=np.copy(frame)
    status,status_desc,frame,res_str,skeleton_str=parse(frame, frameCopy, img_path)

    if status == 'success':
        res_string+=res_str
        skeleton_string+=skeleton_str
        cv2.imwrite(result_dir+'images_visualization/s_'+img_name, frame)
        return res_string,skeleton_string
    else:
        return 'fail',status_desc

