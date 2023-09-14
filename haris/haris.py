from __future__ import print_function
import cv2 as cv
import numpy as np
#import to_real_world as Real
#from pyzbar.pyzbar import decode
#import coordtrans as CoordTrans
import json
#import util
import math
import ssl
import subprocess
#from paho.mqtt.client import Client as MQTTClient
import time
import os
stream_name = os.getenv("stream_name")

startImageProcessing = False
startFFMPPush = False
mqttPayload = None



def restream():
    print("in restream")
    
    global startFFMPPush
    global startImageProcessing
    startFFMPPush = True
    startImageProcessing = True
    
    #mqttPayloadStr = str(mqttPayload)

    #mqtt_payload: dict = json.loads(mqttPayload)

    #agent_name = mqtt_payload["task"]["params"]["agent"]

    print(f'****Trying to restream****')
    #rtmp_url = "rtmp://localhost/app/magnus_haris"
    rtmp_url = f"rtmp://172.30.161.103/app/{stream_name}_haris"
    #rtmp_url = "rtmp://ome.waraps.org/app/Piraya14_Haris"

    command = ['ffmpeg',
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(640, 480),
                '-framerate', str(25),
                '-i', '-',
                '-c:v', 'libx264',
                '-profile:v' , 'baseline', 
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-f', 'flv',
                '-loglevel', 'error',
                '-tune', 'zerolatency',
                '-b:v', '2M',
                rtmp_url]

    if (startFFMPPush):
        p = subprocess.Popen(command, stdin=subprocess.PIPE)

    print('Read!')   
    #cap = cv.VideoCapture("Balls.mp4")
    #cap = cv.VideoCapture("rtsp://192.168.0.90/axis-media/media.amp")
    #cap = cv.VideoCapture("/dev/video0")
    #cap = cv.VideoCapture("dji0_qr_tompe.mp4")
    #cap.set(cv.CAP_PROP_POS_FRAMES, 7000)
    #cap.set(cv.CAP_PROP_POS_FRAMES, 2300)
    #cap = cv.VideoCapture("rtmp://rtmp.waraps.org/live/Piraya14", cv.CAP_FFMPEG)

    #coord = CoordTrans.CoordTrans(location="granso")
    counter = 0

    cap = cv.VideoCapture(f"rtmp://172.30.161.103:1936/live/{stream_name}", cv.CAP_FFMPEG)
    while(cap.isOpened()):

        #print('IsOpen!')  
        height = 480
        width = 640
        
        ret1, img1 = cap.read()        
        img1 = cv.resize(img1, (640, 480), interpolation=cv.INTER_AREA)
        #img1 = img1[0:height, 0:width]      
        blurred = cv.GaussianBlur(img1, (5,5),0)     
        grayFirst = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
        img_hsv = cv.cvtColor(img1, cv.COLOR_BGR2HSV)    
        gray = cv.dilate(grayFirst, None, iterations=2)
        #print('Read!')   
        
        #ret2, img2 = cap.read()
        #img2 = img2[0:height, 0:width]   
        #blurred2 = cv.GaussianBlur(img2, (3,3),0)     
        #gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)    
        #gray2 = cv.dilate(gray2, None, iterations=4)        
        #img1 = cv.imread(cv.samples.findFile(args.input1), cv.IMREAD_GRAYSCALE)
        #img2 = cv.imread(cv.samples.findFile(args.input2), cv.IMREAD_GRAYSCALE)
        try:
            if (startImageProcessing == True):
            

                if gray is None:
                    print('Could not open or find the images!')
                    exit(0)


                grayFloat = np.float32(gray)
                
                corners = cv.goodFeaturesToTrack(grayFloat, maxCorners=10, qualityLevel=0.3, minDistance=50)
                corners = np.float32(corners)

                
                #print('New Round')
                validPoint = False
                width, height, channels = img_hsv.shape
                for item in corners:
                    #print(f'Min max {item.min()}   {item.max()}  ')
                    x,y = item[0]
                    x = int(x)
                    y = int(y)
                    
                    if (y > 5 and x > 5 and y < width-5 and x < height-5):
                        subImage = img_hsv[y-5:y+5, x-5:x+5]      
                        if (subImage.max() - subImage.min() > 252):
                            #print(f'\tBigg diff {subImage.max()} {subImage.min()} ')
                            validPoint = True
                        # else:
                        #     print(f'\tNo color diff ')

                    else:
                        print(f'Close to side')
                    #c_x = 0
                    #c_y = 0
                    #for c_y in range(len(subImage[0])):  
                    #    for c_x in range(len(subImage[1])):                    
                            


                    #print(f'New Round {x}  {y}')
                    #cv.circle(img1, (x,y),6,(0,255,0), -1)
                    #cv.rectangle(img1, (x,y),6,(0,255,0), -1)
                    if (validPoint == True):
                        cv.rectangle(img1, (x-10, y-10), (x + 10, y + 10), (0, 255, 0), 2)


                #dst = cv.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)

                #dst = cv.dilate(dst, None, iterations=3)

                #ret, dst = cv.threshold(dst, 0.5*dst.max(), 255,0)
                #dst = np.uint8(dst)loop_forever
                #res = np.hstack((centroids, corners))
                #res = np.int0(res)

                #img1[res[:,1], res[:,0]] = [0,0,255]
                #img1[res[:,3], res[:,2]] = [0,255,0]

                #img1[dst > 0.50 * dst.max()] = [0,255,0]
                #img1[dst < 0.50 * dst.max()] = [0,0,0]

            dilatePresent = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)
            hsvPresent = cv.cvtColor(img_hsv, cv.COLOR_HSV2RGB)
            one = cv.resize(dilatePresent, (320, 240), interpolation=cv.INTER_AREA)
            two = cv.resize(hsvPresent, (320, 240), interpolation=cv.INTER_AREA) 
            three = cv.resize(img1, (320, 240), interpolation=cv.INTER_AREA)  
            hori = np.concatenate((one,two, three),axis = 1 )
            #cv.imshow('Good Matches', three)    
            output = img1
            if (startFFMPPush):
                if (counter % 1 == 0):
                    p.stdin.write(output.tobytes())

            counter += 1

        except Exception as exc:
            print(f'Exc {exc}')
            pass

        
        # if cv.waitKey(100) & 0xFF == ord('q'):
        #     break

    cv.waitKey()

# def on_message(client, userdata, message) -> None:
#         global mqttPayload
#         try:
#             # print(f'Receive {str(message.payload.decode("utf-8"))}')
#             # print(f'Messsge {message.topic}')
#             mqttPayload = str(message.payload.decode("utf-8"))
#             restream()
#         except json.decoder.JSONDecodeError as e:
#             pass

# def on_connect(self, client, userdata, flags) -> None:
#     #print(f'Subscribe')  
#     mqtt.subscribe("waraps/service/virtual/real/kockums/exec/command")
#     #waraps/service/virtual/real/providence/exec/command
    
# def on_subscribe(self, client, userdata, flags) -> None:
#     print(f'Has subscribed')  

# def nothing(x):
#     pass

# mqtt = nothing
# try:
#     mqtt = MQTTClient("HarisCorner")
#     #mqtt.tls_set()
#     #mqtt.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
#     #mqtt.tls_insecure_set(True)
#     mqtt.username_pw_set("","")
#     #mqtt.enable_logger
#     mqtt.on_connect = on_connect
#     mqtt.on_subscribe = on_subscribe
#     mqtt.on_message = on_message
#     error =  mqtt.connect("10.10.10.16",1883)
#     #mqtt.loop_start()
#     mqtt.loop_start()
#     while True:
#         time.sleep(1)

#     print(f'Connected {error}')  
# except Exception as exc:
#     print(f'Exception {exc}')  
#     pass
restream()