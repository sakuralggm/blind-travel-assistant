# Mobility assistance systems for the blind，盲人出行辅助系统
from distance_sensor import CSB
from acceleration import Accelerator
from camera import CAMERA
from time import sleep
import threading, signal
from flask import Flask, render_template, Response, stream_with_context, request
app = Flask('__name__')


def A():
    while True:
        if is_exit:
            break
        sensor.check_distance_sensor()
        adxl345.check_adxl345()

def B():
    app.run(host='0.0.0.0', port='5000', debug=False)


def handler(signum, frame):
    global is_exit
    is_exit = True
    print("receive a signal %d, is_exit = %d"%(signum, is_exit))

@app.route('/camera')
def mycamera():
    return render_template('camera.html')


@app.route('/video_feed')
def video_feed():
    return Response(camera.capture(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    sensor = CSB()
    adxl345 = Accelerator()
    camera = CAMERA()
    system_run = True
    is_exit = False
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    funcs = [A, B]
    threads = []
    for func in funcs:
        t = threading.Thread(target=func)
        t.setDaemon(True)
        threads.append(t)
        t.start()
        
    while 1:
        alive = False
        for thread in threads:
            alive = alive or thread.is_alive()
        if not alive:
            break
        
