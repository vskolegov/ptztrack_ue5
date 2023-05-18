"""
This file defines pydantic models for controling interface
"""
from pydantic import BaseModel
from ipaddress import IPv4Address
from enum import Enum


class CameraStatus(str, Enum):
    """
    Status working ONVIF camera
    """
    ON = "On"
    OFF = "Off"
    NOT_DATA = "Not data"


class Camera(BaseModel):
    """
    Model for each ONVIFCamera
    """
    ip: IPv4Address
    port: int = 80
    login: str
    password: str
    unreal_name: str
    status: CameraStatus = CameraStatus.NOT_DATA


class Scene(BaseModel):
    """
    Model for scene
    """
    name: str
    cameras: list[Camera]


class Scenes(BaseModel):
    """
    Model scenes for runtime
    """
    scenes: dict[str, list[Camera]]
