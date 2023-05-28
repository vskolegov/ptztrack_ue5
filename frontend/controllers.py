from PySide6.QtCore import QObject, Signal, QThread
from backend.connector import *


class PTZCameras(QObject):
    def __init__(self):
        super().__init__()

        self.current_scene = None
        self.scene_list = dict()
        self.storage = dict()

    def get_scenes(self):
        return get_scene_names()

    def add_new_scene(self, scene):
        self.storage = dict()
        add_cameras_to_scene(scene, self.storage)
        self.current_scene = scene
        self.set_cameras(self.storage)

    def load_scene(self, scene):
        self.storage = dict()
        for camera in get_camereas(scene + ".json"):
            self.store(camera['ip'], camera['port'], camera['unreal_name'])
        self.current_scene = scene

    def server_unreal_status(self):
        return unreal_status()

    def store(self, ip, port, name):
        self.storage[(ip, port)] = name
        self.set_cameras(self.storage)

    def get_cameras(self):
        return self.storage

    def set_cameras(self, new_storage):
        self.storage = new_storage

    def cameras_save(self):
        add_cameras_to_scene(self.current_scene, self.storage)

    def edit_camera(self, socket, new_socket, name):
        ip, port = socket.split(':')
        new_ip, new_port = new_socket.split(':')
        if (ip, port) not in self.storage:
            return
        if (new_ip, new_port) in self.storage:
            return
        del self.storage[(ip, port)]
        self.storage[new_ip, new_port] = name
        self.set_cameras(self.storage)

    def removeItem(self, socket):
        ip, port = socket.split(':')
        if (ip, port) not in self.storage:
            return
        del self.storage[(ip, port)]
        self.set_cameras(self.storage)

    def start_scene(self):
        start_server(self.current_scene)

    def stop_scene(self):
        stop_server()

    def get_storage(self):
        return self.get_cameras()

    def __get_camera_keys(self):
        aboba = [f'{ip}:{port}' for (ip, port) in self.storage.keys()]
        return aboba

    def __get_scene_keys(self):
        return self.scene_list

    def __get_current_scene(self):
        return self.current_scene

    # cameras = Property("QJsonObject",
    #                    fget=__get_cameras,
    #                    fset=__set_cameras,
    #                    notify=onCamerasChanged)
    #
    # camera_keys = Property("QVariant",
    #                        fget=__get_camera_keys,
    #                        # fset=__set_camera_keys,
    #                        notify=onCameraKeysChanged)
    #
    # scene_keys = Property("QVariant",
    #                       fget=__get_scene_keys,
    #                       # fset=__set_camera_keys,
    #                       notify=onSceneKeysChanged)
    #
    # scene_current = Property("QVariant",
    #                          fget=__get_current_scene,
    #                          # fset=__set_camera_keys,
    #                          notify=onSceneKeysChanged)


class ServerHandler(QThread):
    unreal_status_signal = Signal(bool)

    def __init__(self, ptz: PTZCameras):
        super().__init__()
        self.ptz = ptz

    def run(self) -> None:
        while True:
            if self.ptz.current_scene:
                self.unreal_status_signal.emit(self.ptz.server_unreal_status())
            self.msleep(200)

