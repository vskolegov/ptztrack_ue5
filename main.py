from PySide6.QtCore import QObject, Signal, Slot, QUrl, Property
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle

from time import sleep
import sys
import signal
from colorama import init, Fore, Back, Style
from onvif import ONVIFCamera

from backend.connector import *


class PTZCameras(QObject):
    cameraInitialized = Signal()
    onCamerasChanged = Signal()
    onCameraKeysChanged = Signal()
    onSceneKeysChanged = Signal()
    onSceneChanged = Signal()
    current_scene = ""


    def __init__(self):
        super().__init__()

        self.scene_list = dict()
        self.storage = dict()
# upload cameras in from client storage to json
    @Slot()
    def initialize_cameras(self):
        add_cameras_to_scene(self.current_scene, self.storage)
        self.cameraInitialized.emit()

    @Slot("QVariant")
    def add_new_scene(self, scene):
        self.storage = dict()
        add_cameras_to_scene(scene, self.storage)
        self.current_scene = scene
        self.__set_cameras(self.storage)
        self.onSceneKeysChanged.emit()

# load cameras to selected scene from json
    @Slot("QVariant")
    def load_scene(self, scene):
        self.storage = dict()
        for camera in get_camereas(scene + ".json"):
            self.store(camera['ip'], camera['port'], camera['unreal_name'])
        self.current_scene = scene
        self.onSceneKeysChanged.emit()
# load list of scenes by existed jsons
    @Slot()
    def get_scenes(self):
        self.scene_list = get_scene_names()
        self.onSceneKeysChanged.emit()

# load a new camera to the client storage
    @Slot("QVariant, QVariant, QVariant")
    def store(self, ip, port, name):
        self.storage[(ip, port)] = name
        self.__set_cameras(self.storage)

# load edited camera to the client storage
    @Slot("QVariant", "QVariant")
    def edit_camera(self, socket, new_socket):
        ip, port = socket.split(':')
        new_ip, new_port = new_socket.split(':')
        if (ip, port) not in self.storage:
            return
        if (new_ip, new_port) in self.storage:
            return
        name = self.storage[(ip, port)]
        del self.storage[(ip, port)]
        self.storage[new_ip, new_port] = name
        self.__set_cameras(self.storage)

# remove selected camera from the client storage
    @Slot("QVariant")
    def removeItem(self, socket):
        ip, port = socket.split(':')
        if (ip, port) not in self.storage:
            return
        del self.storage[(ip, port)]
        self.__set_cameras(self.storage)

    @Slot()
    def start_scene(self):
        start_server(self.scene_current)

    @Slot()
    def stop_scene(self):
        stop_server()
    
    @Slot()
    def get_storage(self):
        return self.__get_cameras()

    def __get_cameras(self):
        return self.storage

    def __set_cameras(self, new_storage):
        self.storage = new_storage
        self.onCamerasChanged.emit()
        self.onCameraKeysChanged.emit()
    
    def __get_camera_keys(self):
        aboba = [f'{ip}:{port}' for (ip, port) in self.storage.keys()]
        return aboba

    def __get_scene_keys(self):
        return self.scene_list
    
    def __get_current_scene(self):
        return self.current_scene

    cameras = Property("QJsonObject",
                       fget=__get_cameras,
                       fset=__set_cameras,
                       notify=onCamerasChanged)
    
    camera_keys = Property("QVariant",
                       fget=__get_camera_keys,
                       #fset=__set_camera_keys,
                       notify=onCameraKeysChanged)

    scene_keys = Property("QVariant",
                       fget=__get_scene_keys,
                       #fset=__set_camera_keys,
                       notify=onSceneKeysChanged)
    
    scene_current = Property("QVariant",
                       fget=__get_current_scene,
                       #fset=__set_camera_keys,
                       notify=onSceneKeysChanged)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()

    ptz_cameras = PTZCameras()

    engine.rootContext().setContextProperty('PTZCameras', ptz_cameras)

    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    qml_file = QUrl.fromLocalFile('frontend/main.qml')
    engine.load(qml_file)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())
