import asyncio
import sys

from loguru import logger
import uvicorn
from fastapi import FastAPI
from ptztrack_ue5.backend.core import ControlInterface
from ptztrack_ue5.backend.json_settings import create_or_update_scene, read_scene, reload_scenes

from ptztrack_ue5.configs.backend import IP_ADDR_FASTAPI, PORT_FASTAPI
from ptztrack_ue5.schemas.control import Scene, Scenes

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>"
)

app = FastAPI()
control = ControlInterface()


@app.post("/update_scene")
async def update_scene(scene: Scene):
    """
    This function add or update scene, after that reload scenes and
    return them.
    """
    await create_or_update_scene(scene)
    scenes = await reload_scenes()
    return scenes


@app.get("/scenes")
async def scenes() -> Scenes:
    """
    This function update scenes and return them
    """
    return await reload_scenes()


@app.get("/default_scene")
async def default_scene() -> Scene:
    """
    This function return defaul scene from ControlInterface
    """
    return await control.get_default_scene()


@app.post("/default_scene")
async def set_default_scene(value: str) -> Scene:
    """
    This function change default scene and stop control interface
    """
    control.stop()
    await control.set_default_scene(value)
    return await control.get_default_scene()


@app.get("/start")
async def start_uploading() -> Scene:
    """
    Start control interface
    """
    asyncio.ensure_future(control.run())
    return await control.get_default_scene()


@app.get("/stop")
async def stop_uploading() -> Scene:
    """
    Stop control interface
    """
    control.stop()
    return await control.get_default_scene()


def run():
    """
    launch uvicorn server for poetry
    """
    logger.info(f"Start server {IP_ADDR_FASTAPI}:{PORT_FASTAPI}...")
    uvicorn.run("ptztrack_ue5.server:app",
                host=IP_ADDR_FASTAPI, port=PORT_FASTAPI, # type: ignore
                reload=True)
