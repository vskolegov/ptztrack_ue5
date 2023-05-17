from loguru import logger
import uvicorn
from fastapi import FastAPI

from ptztrack_ue5.configs.backend import IP_ADDR_FASTAPI, PORT_FASTAPI


app = FastAPI()

@app.get("/")
async def main_route():
    return {"message": "Hello"}


def run():
    """
    launch uvicorn server for poetry
    """
    logger.info(f"Start server {IP_ADDR_FASTAPI}:{PORT_FASTAPI}...")
    uvicorn.run("ptztrack_ue5.server:app",
                host=IP_ADDR_FASTAPI, port=int(PORT_FASTAPI), # type: ignore
                reload=True)
