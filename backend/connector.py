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
from backend.main_worker import *


def add_cameras_to_scene(scene_name, camera_list):
    """
    Function to add a list of cameras to a scene
    """
    camera_data = []
    names = [f'{name}' for (name) in camera_list.values()]
    j = 0
    for i in camera_list:
        camera_data.append({'ip': i[0], 'port': i[1], 'unreal_name': names[j]})
        j = j + 1
    with open('jsons/' + f"{scene_name}.json", 'w', encoding="utf-8") as f:
        json.dump(camera_data, f)


def get_camereas(scene_name):
    """
    Function to load list of cameras from selected scene.json
    """
    with open ('jsons/' + scene_name, 'r', encoding="utf-8") as f:
        camera_data = json.load(f)
    for camera in camera_data:
        yield camera


def get_scene_names():
    """
    Function to get the names of all scene.json files
    """
    return [f[:-5] for f in os.listdir('./jsons') if f.endswith('.json')]


def start_server(scene):
    """
    Function to start running processed() in main_worker.py
    """
    with open ('jsons/' + scene + ".json", 'r', encoding="utf-8") as f:
        camera_data = json.load(f)
        processed(camera_data)


def stop_server():
    """
    Function to stop running sequental() in main_worker.py
    """
    exit_func()


def get_info(scene):
    """
    Function to get status of elements from backend
    """
    print(scene + ' server info:')
