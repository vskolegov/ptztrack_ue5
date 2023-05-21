"""
This module defines funtions and corutines for creating,
read and remove scenes
"""
from os.path import join
from os import walk
import aiofiles
from slugify import slugify
from ptztrack_ue5.configs.backend import JSON_PATH

from ptztrack_ue5.schemas.control import Scene, Scenes


async def create_or_update_scene(scene: Scene):
    """
    Function create scene
    """
    file_name = join(JSON_PATH, f"{slugify(scene.name)}_scene.json")
    async with aiofiles.open(file_name, "wt") as f:
        await f.write(scene.json())


async def read_scene(file_name: str) -> Scene:
    """
    Read file
    """
    async with aiofiles.open(file_name, "r") as f:
        text = await f.read()
    return Scene.parse_raw(text)


async def reload_scenes() -> Scenes:
    """
    walking into json folder and read jsons files.
    """
    scenes_list = []
    for root, _, files in walk(JSON_PATH, topdown=False):
        for file in files:
            if "_scene.json" in file:
                scenes_list.append(await read_scene(join(root, file)))
    return Scenes(scenes={ scene.name: scene.cameras for scene in scenes_list })
