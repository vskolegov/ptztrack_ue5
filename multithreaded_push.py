import aiohttp
import json
import asyncio
import random
import time
import threading
import os, sys
import requests
import signal
import numpy

paths = ['/Game/InCamVFXBP/Maps/LED_CurvedStage.LED_CurvedStage:PersistentLevel.CineCameraActor_1',
         '/Game/InCamVFXBP/Maps/LED_CurvedStage.LED_CurvedStage:PersistentLevel.CineCameraActor_0',
         '/Game/InCamVFXBP/Maps/LED_CurvedStage.LED_CurvedStage:PersistentLevel.CineCameraActor_2']


thread_list = list()
cpu_count = os.cpu_count()
last_sent = {path: [time.perf_counter()] for path in paths}
jj = {path: list() for path in paths}


def send_ptz_data():
    # Connect to the PTZ camera using the ONVIF protocol
    
    # Define the initial PTZ parameters
    position = { }
    position['Pitch'] = random.uniform(-18, 18)
    position['Yaw'] = random.uniform(-9, 9)
    position['Roll'] = random.uniform(0, 0)

    zoom = {}
    zoom['InFocalLength'] = random.uniform(10, 11)
    
    # Send 10 requests with updated PTZ data
    global i, thread_list, cpu_count, paths

    for path in paths:
        if threading.active_count() < cpu_count:
            thread = threading.Thread(target=send_jsons_to_ue, args=(position, zoom, path), daemon=True)
            thread.start()
            thread_list.append(thread)
            #await send_jsons_to_ue(position, zoom, path2)
            #await asyncio.sleep(0.1)
    while threading.active_count():
        ...


async def async_send_json(url, head, data):
    async with aiohttp.ClientSession() as session:
        r1 = await session.put(url, headers=head, data = data)


def send_json(url, head, data, path):
    global last_sent
    requests.put(url, headers=head, data = data)
    t = time.perf_counter()
    print(f'fps: {1. / (t - last_sent[path][-1])}', end='\r')
    last_sent[path].append(t)
    jj[path].append(1. / (t - last_sent[path][-2]))


def rand():
    return numpy.random.normal(scale=.1)

        
def send_jsons_to_ue(position, zoom, path):
    global cpu_count
    while True:
        #t = time.perf_counter()
        position['Pitch'] += rand()
        position['Yaw'] += rand()
        zoom['InFocalLength'] = rand()

        url = "http://127.0.0.1:30010/remote/object/call"
        head = {'Content-Type': 'application/json'}
        data1 = json.dumps({'objectPath': path, 'functionName': 'SetActorRotation', 'parameters': {'NewRotation': position}})
        data2 = json.dumps({'objectPath': path + ".CameraComponent", 'functionName': 'SetCurrentFocalLength', 'parameters': zoom})
        if threading.active_count() < cpu_count:
            thread = threading.Thread(target=send_json, args=(url, head, data1, path), daemon=True)
            thread.start()
        if threading.active_count() < cpu_count:
            thread = threading.Thread(target=send_json, args=(url, head, data2, path), daemon=True)
            thread.start()
        #te = time.perf_counter()
        #print(f'fps: {1. / (te - t)}')


def exit_func(SignalNumber, Frame):
    """ while threading.active_count() > 1:
        pass """
    j = json.dumps(jj)
    with open('timings.json', 'w') as f:
        f.write(j)
    quit()


signal.signal(signal.SIGINT, exit_func)


if __name__ == '__main__':
    # Set the IP address, username, and password of the PTZ camera here
    send_ptz_data()

#asyncio.run(main())