"""
Модуль устанавливает соединения с камерами, а также пробрасывает его
в UnrealEngine
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable
from enum import Enum

from httpx import AsyncClient, Response
from onvif import ONVIFCamera
from onvif.client import ONVIFService

from loguru import logger

from ptztrack_ue5.configs.backend import (
    pantilt_x_coef,
    pantilt_y_coef,
    zoom_coef,
    PATH_SERVER_FOR_REQUEST,
    URL_UNREAL_SERVER_STRING,
    WSDL_PATH,
    BackendError
)


class StateServer(Enum):
    """
    States type server
    """
    OFF = 0
    ON = 1


class Interface():
    """
    This class is responsible for state and work connection cameras and
    Unreal Engine
    """
    __state = StateServer.OFF
    __cameras = None

    def __init__(self, cameras: list[dict[str, Any]] | None= None):
        if cameras is not None:
            self.cameras = cameras

    @property
    def cameras(self) -> list[dict[str, Any]] | None:
        return self.__cameras

    @cameras.setter
    def cameras(self, cameras: list[dict[str, Any]]):
        if not isinstance(cameras, list):
            raise TypeError("Cameras must be list[dict[str, Any]]")
        self.__cameras = cameras
        self.__state = StateServer.OFF

    @property
    def state(self) -> StateServer:
        return self.__state

    @state.setter
    def state(self, state: StateServer):
        self.__state = state

    @staticmethod
    async def __get_media_profiles_token(camera: ONVIFCamera) -> str:
        """
        Function get media profile
        """
        media = await camera.create_media_service()
        media_profile = await media.GetProfiles()
        return media_profile[0].token

    @staticmethod
    @asynccontextmanager
    async def _connect_camera(real_camera: dict):
        """
        Corutine connect and return camera description
        {
            ip: value,
            port: value,
            login: value,
            password: value,
        }
        """
        camera = ONVIFCamera(real_camera["ip"], real_camera["port"],
                             real_camera["login"], real_camera["password"],
                             WSDL_PATH) # type: ignore
        try:
            await camera.update_xaddrs()
            # Create ptz
            ptz = await camera.create_ptz_service()
            request_ptz_status = ptz.create_type("GetStatus") # type: ignore
            request_ptz_status.ProfileToken = (
                await Interface.__get_media_profiles_token(camera)
            )
            # Create devicemgmt
            device = await camera.create_devicemgmt_service()
            resp = await device.GetHostname()
        except Exception as err:
            raise BackendError(f"Can't connect to ONVIF Camera: {err}")
        else:
            logger.info(f"Successfully connect to ONVIF Camera: {resp.Name}")
            yield ptz, request_ptz_status
        finally:
            logger.info(f"disconnect from camera {real_camera['ip']}")
            await camera.close()

    @staticmethod
    async def _update_unreal_camera(data: dict,
                                    owl: bool = False) -> Response:
        """
        Update location in Unreal Engine with PUT request
        'owl' variable used for logging zoom effect
        """
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

    @staticmethod
    async def __prepare_and_send_requests(ptz: ONVIFService, req_ptz_status: Any,
                                          camera: dict[str, Any]):
        """
        This corurine is supply function for update_unreal_real_camera.
        """
        try:
            zoom = await Interface.__compute_zoom(ptz, req_ptz_status)
            rotation = await Interface.__compute_rotation(ptz, req_ptz_status)
            resp = await Interface._update_unreal_camera(
                data=Interface.__create_request_body_rotation_for_unreal(
                    rotation, camera["unreal_name"]))
            logger.debug(
                f"Status updating rotation"
                f"(new data: {rotation['Pitch']}, {rotation['Yaw']}) for "
                f"{camera['ip']}: {resp.json()['ReturnValue']}"
            )
            resp = await Interface._update_unreal_camera(
                data=Interface.__create_request_body_zoom_for_unreal(
                    zoom, camera["unreal_name"]), owl=True)
            if resp.json():
                logger.debug(
                    f"Status updating zoom"
                    f"(new zoom {zoom['InFocalLength']}) for "
                    f"{camera['ip']}: {resp.json()}"
                )
        except BackendError as err:
            logger.error(f"Sending request error: {err}")

    async def run(self):
        """
        Run tasks
        """
        if self.__cameras is None:
            raise BackendError("Cameras aren't set")
        tasks = []
        for camera in self.__cameras:
            try:
                await self._update_unreal_real_camera(camera)
            except BackendError as err:
                logger.error(f"Problem with OnvifCamera: {err}")
        for task in tasks:
            await task

    async def _update_unreal_real_camera(self, camera: dict[str, Any]):
        """
        Corutine create connect to OnvifCameras, and update virtual camera.
        """
        async with Interface._connect_camera(camera) as (ptz, req_ptz_status):
            while True:
                await Interface.__prepare_and_send_requests(ptz,
                                                            req_ptz_status,
                                                            camera)
                # If server runing, but not StateServer.ON, then break
                if self.__state == StateServer.OFF:
                    break
