# ptztrack_ue5
Using onvif-based ptz cameras for virtual production in Unreal Engine 5

## Usage

```bash
python3 main.py
```

This is a desktop application, so you can see the interface.

## Dependencies

To install the dependencies, run:

```bash
pip3 install -r requirements.txt
```

Also, to run, you must have Unreal Engine 5.1 with the Remote Control API installed and the Web Server running on it at 127.0.0.1:30010

## Scenes

The jsons folder that contains json files, the filename is the name of the scene, and the content is the cameras in it. These files can be created using the interface or manually.