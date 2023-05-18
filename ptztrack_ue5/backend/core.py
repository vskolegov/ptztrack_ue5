"""
Модуль устанавливает соединения с камерами, а также пробрасывает его
в UnrealEngine
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable
from enum import Enum

from httpx import AsyncClient, Response, ConnectError
from onvif import ONVIFCamera
from onvif.client import ONVIFService

from loguru import logger
from ptztrack_ue5.backend.json_settings import reload_scenes

from ptztrack_ue5.configs.backend import (
    pantilt_x_coef,
    pantilt_y_coef,
    zoom_coef,
    PATH_SERVER_FOR_REQUEST,
    URL_UNREAL_SERVER_STRING,
    WSDL_PATH,
    BackendError
)
from ptztrack_ue5.schemas.control import Camera, CameraStatus, Scene


class ControlInterface():
    """
    This class is responsible for state and work connection cameras and
    Unreal Engine
    """
    __scenes = None
    __tasks = []
    __default_scene = None

    def __init__(self):
        self.__tasks = []
        self.__scenes = None
        self.__default_scene = None

    async def get_default_scene(self) -> Scene:
        """
        Getter for default scene. Function implemented without
        @property, because setter for default scene is awaitable
        """
        if self.__default_scene is None:
            await self.set_default_scene()
        return Scene(
            name=self.__default_scene, # type: ignore
            cameras=self.__scenes.scenes[self.__default_scene] # type: ignore
        )

    async def set_default_scene(self, name: str | None = None) -> None:
        """
        Async setter for default_scene
        """
        if self.__scenes is None:
            self.__scenes = await reload_scenes()
        if name is None:
            self.__default_scene = list(self.__scenes.scenes.keys())[0] # type: ignore
        if name in self.__scenes.scenes.keys():
            self.__default_scene = name

    @staticmethod
    async def __get_media_profiles_token(camera: ONVIFCamera) -> str:
        """
        Function get media profile
        """
        media = await camera.create_media_service()
        media_profile = await media.GetProfiles()
        return media_profile[0].token

    @asynccontextmanager
    async def _connect_camera(self, camera_params: Camera):
        """
        Corutine connect and return camera description
        """
        camera = ONVIFCamera(str(camera_params.ip), camera_params.port,
                             camera_params.login, camera_params.password,
                             WSDL_PATH) # type: ignore
        try:
            await camera.update_xaddrs()
            # Create ptz
            ptz = await camera.create_ptz_service()
            request_ptz_status = ptz.create_type("GetStatus") # type: ignore
            request_ptz_status.ProfileToken = (
                await ControlInterface.__get_media_profiles_token(camera)
            )
            # Create devicemgmt
            device = await camera.create_devicemgmt_service()
            resp = await device.GetHostname()
        except Exception as err:
            camera_params.status = CameraStatus.OFF
            raise BackendError(f"Can't connect to ONVIF Camera: {err}")
        else:
            logger.info(f"Successfully connect to ONVIF Camera: {resp.Name}")
            camera_params.status = CameraStatus.ON
            yield ptz, request_ptz_status
        finally:
            logger.info(f"disconnect from camera {camera_params.ip}")
            await camera.close()

    @staticmethod
    async def _update_unreal_camera(data: dict,
                                    owl: bool = False) -> Response:
        """
        Update location in Unreal Engine with PUT request
        'owl' variable used for logging zoom effect
        """
        try:
            async with AsyncClient() as client:
                resp = await client.put(
                    f"{URL_UNREAL_SERVER_STRING}/{PATH_SERVER_FOR_REQUEST}",
                    json=data,
                )
            # raise exception if status is not Ok
            if resp.status_code != 200 and not owl:
                raise BackendError(f"Unreal Engine didnt' return OK")
            elif resp.status_code != 200:
                logger.warning(f"OWL plugin is not installed in Unreal Engine")
        except Exception as err:
            raise BackendError(f"Problem with UnrealEngine server: {err}")
        else:
            return resp

    @staticmethod
    async def __compute_rotation(ptz: ONVIFService,
                                 req_ptz_status: Any) -> dict[str, float]:
        """
        Corutine compute rotation for unreal engine API
        """
        status = await ptz.GetStatus(req_ptz_status)
        return {
            "Pitch": pantilt_y_coef(status.Position.PanTilt.y),
            "Yaw": pantilt_x_coef(status.Position.PanTilt.x),
        }

    @staticmethod
    async def __compute_zoom(ptz: ONVIFService,
                             req_ptz_status: Any) -> dict[str, float]:
        """
        Corutine compute Zoom for OWL cameras
        """
        status = await ptz.GetStatus(req_ptz_status)
        return {
            "InFocalLength": zoom_coef(status.Position.Zoom.x),
        }

    @staticmethod
    def __create_request_body_rotation_for_unreal(
        rotation: dict[str, float], unreal_name: str) -> dict[str, Any]:
        """
        Funtion return dict for json request Unreal Engine Server
        """
        return {
            "objectPath": unreal_name,
            "functionName": "SetActorRotation",
            "parameters": {
                'NewRotation': rotation,
            }
        }

    @staticmethod
    def __create_request_body_zoom_for_unreal(
        zoom: dict[str, float], unreal_name: str) -> dict[str, Any]:
        """
        Funtion return dict for json request Unreal Engine Server
        """
        return {
            "objectPath": f"{unreal_name}.CameraComponent",
            "functionName": "SetCurrentFocalLength",
            "parameters": zoom,
        }


    async def __prepare_and_send_requests(self, ptz: ONVIFService,
                                          req_ptz_status: Any,
                                          camera: Camera):
        """
        This corurine is supply function for update_unreal_real_camera.
        """
        try:
            zoom = await ControlInterface.__compute_zoom(ptz, req_ptz_status)
            rotation = await ControlInterface.__compute_rotation(ptz, req_ptz_status)
            resp = await ControlInterface._update_unreal_camera(
                data=ControlInterface.__create_request_body_rotation_for_unreal(
                    rotation, camera.unreal_name))
            logger.debug(
                f"Status updating rotation"
                f"(new data: {rotation['Pitch']}, {rotation['Yaw']}) for "
                f"{camera.ip}: {resp.json()['ReturnValue']}"
            )
            resp = await ControlInterface._update_unreal_camera(
                data=ControlInterface.__create_request_body_zoom_for_unreal(
                    zoom, camera.unreal_name), owl=True)
            if resp.json():
                logger.debug(
                    f"Status updating zoom"
                    f"(new zoom {zoom['InFocalLength']}) for "
                    f"{camera.ip}: {resp.json()}"
                )
        except BackendError as err:
            logger.error(f"Sending request error: {err}")

    def stop(self):
        """
        Stop task and clear list
        """
        for task in self.__tasks:
            task.cancel()

    async def run(self):
        """
        Run tasks
        """
        # Set default scene if is not exsist
        if self.__default_scene is None:
            await self.set_default_scene()
        self.stop()
        default_scene = await self.get_default_scene()
        cameras = default_scene.cameras
        for camera in cameras:
            self.__tasks.append(asyncio.create_task(
                self._update_unreal_real_camera(camera)
            ))
        for task in self.__tasks:
            await task

    async def _update_unreal_real_camera(self, camera: Camera):
        """
        Corutine create connect to OnvifCameras, and update virtual camera.
        """
        try:
            async with self._connect_camera(camera) as (ptz, req_ptz_status):
                while True:
                    await self.__prepare_and_send_requests(ptz, req_ptz_status,
                                                           camera)
        except asyncio.CancelledError:
            logger.info(f"Recive command for cancel task for "
                        f"{camera.ip}")
        except BackendError as err:
            logger.error(f"Problem with OnvifCamera: {err}")
