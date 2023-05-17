"""
functions and tests are for the backend module
"""
import asyncio
from contextlib import nullcontext as does_not_raise
from os import environ

import pytest
import pytest_asyncio

import httpx


environ["IP_ADDR_UNREAL_REMOTE_CONTROL"] = "127.0.0.1"
environ["PORT_UNREAL_REMOTE_CONTROL"] = "30010"

from ptztrack_ue5.configs.backend import (
    PATH_SERVER_FOR_INFO,
    URL_UNREAL_SERVER_STRING,
    BackendError
)
from ptztrack_ue5.backend.core import StateServer, Interface


#  @pytest.fixture(scope=module)
#  def interface(event_loop):
#      yield Interface()
#

@pytest_asyncio.fixture(scope="function")
async def client(event_loop):
    async with httpx.AsyncClient() as client:
        yield client


@pytest.mark.asyncio
async def test_info_unreal(client):
    """
    Testing unreal server connect
    """
    tasks = []
    for _ in range(10):
        tasks.append(asyncio.create_task(
            client.get(f"{URL_UNREAL_SERVER_STRING}/{PATH_SERVER_FOR_INFO}")
        ))
    for idx, task in enumerate(tasks):
        response = await task
        print(f"Запрос №{idx}: {response.text[:100]}")
        assert response.status_code == 200


@pytest.mark.parametrize("params, exc", [
    (
        {
            'ip': '172.18.191.193',
            'port': 2000,
            'login': 'admin',
            'password': 'Supervisor',
        },
        does_not_raise()
    ),
    (
        {
            'ip': '127.0.0.1',
            'port': 2000,
            'login': 'admin',
            'password': 'Supervisor',
        },
        pytest.raises(BackendError)
    )
])
@pytest.mark.asyncio
async def test_connect_onvif_camera(params, exc):
    """
    Testing connect to onvif camera
    """
    with exc:
        async with Interface._connect_camera(params) as (ptz, req_ptz_status):
            status = await ptz.GetStatus(req_ptz_status)
            print(f"Pitch: {status.Position.PanTilt.y}")
            print(f"Yaw: {status.Position.PanTilt.x}")
            print(f"InFocalLength: {status.Position.Zoom.x}")


@pytest.mark.parametrize("req, exc",[
    (
        {
            "objectPath": "/Game/VProdProject/Maps/Main.Main:PersistentLevel.CameraActor_3",
            "functionName": "SetActorRotation",
            "parameters": {
                "NewRotation": {
                    "Pitch": -20.2083327,
                    "Yaw": -31.0416668,
                }
            }
        },
        does_not_raise()
    ),
    (
        {
            "objectPath": "ERROR",
            "functionName": "SetActorRotation",
            "parameters": {
                "NewRotation": {
                    "Pitch": -20.2083327,
                    "Yaw": -31.0416668,
                    #  "InFocalLength": 37.29797365,
                }
            }
        },
        pytest.raises(BackendError)
    ),
])
@pytest.mark.asyncio
async def test_update_location(req, exc):
    with exc:
        resp = await Interface._update_unreal_camera(req)
        print(f"unreal return {resp.json()}")


@pytest.mark.asyncio
async def test_update_unreal_real_camera(cameras):
    """
    Checking run server
    """
    async def print_random(interaface: Interface):
        await asyncio.sleep(5)
        interface.state = StateServer.OFF
        print("Turned off server...")
    interface = Interface(cameras)
    interface.state = StateServer.OFF
    task1 = asyncio.create_task(interface.run())
    task2 = asyncio.create_task(print_random(interface))
    await task1
    await task2
