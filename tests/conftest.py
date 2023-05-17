"""
Shared fixtures and test settings are for the all project
"""
import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """
    Создание event_loop чтобы тесты работали ассинхронно
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def cameras():
    """
    fixture create cameras
    """
    yield [
        {
            'ip': '172.18.191.103',
            'port': 80,
            'login': 'admin',
            'password': 'Supervisor',
            'unreal_name': "/Game/VProdProject/Maps/Main.Main:PersistentLevel.CameraActor_3",
        },
        {
            'ip': '172.18.191.102',
            'port': 80,
            'login': 'admin',
            'password': 'Supervisor',
            'unreal_name': "/Game/VProdProject/Maps/Main.Main:PersistentLevel.CameraActor_1",
        },
    ]
