import multiprocessing
import time
from time import sleep
import random
import json
import time
import threading
import os
import sys
import requests
import signal
from colorama import init, Fore, Back, Style
from onvif import ONVIFCamera

def onvif_connect(scenes):
    cam_login = 'admin'
    cam_pass = 'Supervisor'
    cameras = []
    print(scenes)
    for camera in scenes:
        onvif_camera = ONVIFCamera(camera['ip'], camera['port'], cam_login, cam_pass)
        cameras.append(onvif_camera)
        try:
            media = onvif_camera.create_media_service()
            media_profile = media.GetProfiles()[0]
            ptz = onvif_camera.create_ptz_service()
            resp = onvif_camera.devicemgmt.GetHostname()
            requestPtzStatus = ptz.create_type('GetStatus')
            requestPtzStatus.ProfileToken = media_profile.token
            if ptz.url == '':
                raise Exception
            else:
                print("Successfully connected to " + str(resp.Name))
        except:
            print("Can't connect to ONVIF camera" + str(resp.Name))
        yield ptz, requestPtzStatus, camera['unreal_name']

def unreal_status():
    try:
        response = requests.get(address + "/remote/info")
        if response.status_code != 200:
            raise Exception
        else:
            print("Successfully connected to Unreal Engine")
    except:
        print("Can't connect to Unreal Engine")

def heavy(url, head, data):
    response = requests.put(url, headers=head, data=data)
    print(response.elapsed.total_seconds())
    # print(f'fps: {1. / (t - last_sent[path][-1])}', end='\r')
    # jj[path].append(1. / (t - last_sent[path][-2]))

def sequential(path, ptz, requestPtzStatus):
    cpu_count = os.cpu_count()
    position = {}
    position['Pitch'] = 0
    position['Yaw'] = 0
    position['Roll'] = 0
    zoom = {}
    zoom['InFocalLength'] = 0
    while True:
        print(path)
        status = ptz.GetStatus(requestPtzStatus)
        position['Pitch'] = status.Position.PanTilt.y * 90
        position['Yaw'] = status.Position.PanTilt.x * 170
        zoom['InFocalLength'] = status.Position.Zoom.x * 50 + 10
        data1 = json.dumps({'objectPath': path, 'functionName': 'SetActorRotation', 'parameters': {'NewRotation': position}})
        data2 = json.dumps({'objectPath': path + ".CameraComponent", 'functionName': 'SetCurrentFocalLength', 'parameters': zoom})
        url = "http://127.0.0.1:30010/remote/object/call"
        head = {'Content-Type': 'application/json'}
        if threading.active_count() < cpu_count:
            thread = threading.Thread(target=heavy, args=(
                url, head, data1), daemon=True)
            thread.start()
        if threading.active_count() < cpu_count:
            thread = threading.Thread(target=heavy, args=(
                url, head, data2), daemon=True)
            thread.start()
        
def processed(scenes):
    """ processes = []
    for ptz, requestPtzStatus, unreal_name in onvif_connect(scenes):
        p = multiprocessing.Process(target=sequential, args=(unreal_name, ptz, requestPtzStatus))
        processes.append(p)
        p.start()
    for p in processes:
        p.join() """

    for ptz, requestPtzStatus, unreal_name in onvif_connect(scenes):
        sequential(unreal_name, ptz, requestPtzStatus)


def exit_func():
    # print(jj)
    """ while threading.active_count() > 1:
        pass """
    # j = json.dumps(jj)
    # with open('timings.json', 'w') as f:
    # f.write(j)
    print('exit')
    quit()


if __name__ == "__main__":
    n_proc = multiprocessing.cpu_count()
    cpu_count = os.cpu_count()
    thread_list = list()

    address = 'http://127.0.0.1:30010'
