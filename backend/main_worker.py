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

running_flag = True
#locker = threading.Lock()
event = threading.Event()


def onvif_connect(scenes):
    """
    Формирование объектов OnvifCamera для каждой камеры в сцене и проверка доступа к камерам
    """
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
    """
    Проверка ответа от веб-сервера Unreal Engine
    """
    try:
        response = requests.get(address + "/remote/info")
        if response.status_code != 200:
            raise Exception
        else:
            print("Successfully connected to Unreal Engine")
    except:
        print("Can't connect to Unreal Engine")


def heavy(url, head, data):
    """
    Отправка координат на виртуальную камеру
    """
    event.wait()
    response = requests.put(url, headers=head, data=data)
    print(response.elapsed.total_seconds())
    # print(f'fps: {1. / (t - last_sent[path][-1])}', end='\r')
    # jj[path].append(1. / (t - last_sent[path][-2]))
    #print(data)


def sequential(path, ptz, requestPtzStatus):
    """
    Получение координат реальной камеры в пространстве, формирование json и передача его в heavy() для отправки в UE5
    """
    position = {}
    position['Roll'] = 0
    zoom = {}
    url = "http://127.0.0.1:30010/remote/object/call"
    head = {'Content-Type': 'application/json'}
    while running_flag:
        event.wait()
        event.clear()
        status = ptz.GetStatus(requestPtzStatus)
        position['Pitch'] = status.Position.PanTilt.y * 90
        position['Yaw'] = status.Position.PanTilt.x * 170
        zoom['InFocalLength'] = status.Position.Zoom.x * 50 + 10
        data1 = json.dumps({'objectPath': path, 'functionName': 'SetActorRotation', 'parameters': {'NewRotation': position}})
        data2 = json.dumps({'objectPath': path + ".CameraComponent", 'functionName': 'SetCurrentFocalLength', 'parameters': zoom})
        t1 = threading.Thread(target=heavy, args=(url, head, data1), daemon=True)
        t2 = threading.Thread(target=heavy, args=(url, head, data2), daemon=True)
        t1.start()
        t2.start()
        event.set()
        #print(f"thread count: {threading.active_count()}")
        t1.join()
        t2.join()

def processed(scenes):
    """
    Запуск sequential() в отдельном потоке для каждой камеры в сцене
    """
    i = 0
    event.clear()
    for ptz, requestPtzStatus, unreal_name in onvif_connect(scenes):
        threading.Thread(target=sequential, args=(unreal_name, ptz, requestPtzStatus), daemon = True, name=str(i)).start()
        i = i + 1
    if threading.active_count() >= (i + 1):
        event.set()

def exit_func():
    print('exit')
    #event.clear()
    event.clear
