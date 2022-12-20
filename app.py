#!/usr/bin/env python

from flask import Flask, render_template, jsonify, Response
import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)
#app = Flask(__name__)

#--------------------------------------------------------------------------
# Variables that store the counts of detected items
#--------------------------------------------------------------------------
inventory_numbers = {
    "bottle":0,
    "box_drink":0
}
#--------------------------------------------------------------------------


runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True
if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

def now():
    return round(time.time() * 1000)

def get_webcams():
    port_ids = []
    for port in range(10):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, 'modelfile/' ,'modelfile.eim')

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()

            #frame = cv2.resize(frame, (640, 640), interpolation = cv2.INTER_LINEAR)
            
            ret = camera.read()
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, 0))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here

            #print(" ==== Getting classification runner res.. ====")
            for res, img in runner.classifier(0):
                if (next_frame > now()):
                    time.sleep((next_frame - now()) / 1000)
                
                #print("..printing classification runner response..")
                #print('classification runner response', res)
                if "classification" in res["result"].keys():
                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                    for label in labels:
                        score = res['result']['classification'][label]
                        print('%s: %.2f\t' % (label, score), end='')
                    print('', flush=True)

                elif "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    for bb in res["result"]["bounding_boxes"]:
                        print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                        cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)

                        #--------------------------------------------------------------------------
                        # Increament bottle and box drinks based on the number of bounding boxes
                        #--------------------------------------------------------------------------
                        if(bb['label'] == 'bottle'):
                            inventory_numbers["bottle"] +=1
                        elif(bb['label'] == 'box_drink'):
                            inventory_numbers["box_drink"] +=1

                ret, buffer = cv2.imencode('.jpg', img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                img = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
              
                next_frame = now() + 100

            print("..completed classifier response..")
        finally:
            if (runner):
                print("stopping runner..")
                runner.stop()


@app.route('/')
def index():
    # video streaming home page
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(main(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_inventory_counts') # returns counts of the found objects
def get_inventory_counts():
    global inventory_numbers
    send_inventory_numbers = inventory_numbers # copy numbers to a new variable

    # reset the counts after sending
    inventory_numbers = {
        "bottle":0,
        "box_drink":0
    }
    return jsonify(send_inventory_numbers)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')