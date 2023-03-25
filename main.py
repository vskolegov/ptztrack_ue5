import requests
import json
import signal, sys
from colorama import init, Fore, Back, Style


init(autoreset=True)


address = 'http://127.0.0.1:30010'
headers = {'Content-Type': 'application/json'}

try:
    response = requests.get(address + "/remote/info")
    if response.status_code != 200:
        raise Exception
    else:
        print(Back.GREEN + "Successfully connected to Unreal Engine")
except:
    print(Back.RED + "Can't connect to Unreal Engine")
    sys.exit()


while True:
    try:
        print()
        func = input(Style.BRIGHT + "Type a command\n\t[p] - set position\n\t[r] - set rotation\n\t[CTRL + c] - exit the program\ncommand: " + Style.RESET_ALL)
        print()
        if func == 'p':
            nPos = tuple(map(int, input(Style.BRIGHT + "Input new position\n\tX Y Z: " + Style.RESET_ALL).split()))
            if len(nPos) != 3:
                raise IndexError
            position = {
                'X': nPos[0],
                'Y': nPos[1],
                'Z': nPos[2]
            }
            data = {'objectPath': '/Game/InCamVFXBP/Maps/LED_CurvedStage.LED_CurvedStage:PersistentLevel.CineCameraActor_1', 'functionName': 'SetActorLocation', 'parameters': {'NewLocation': position, 'bSweep': True}, 'generateTransaction': True}
        
        elif func == 'r':
            nRot = tuple(map(int, input(Style.BRIGHT + "Input new rotation\n\tPitch Yaw Roll: " + Style.RESET_ALL).split()))
            if len(nRot) != 3:
                raise IndexError
            rotation = {
                "Pitch": nRot[0],
                "Yaw": nRot[1],
                "Roll": nRot[2]
            }
            data = {'objectPath': '/Game/InCamVFXBP/Maps/LED_CurvedStage.LED_CurvedStage:PersistentLevel.CineCameraActor_1', 'functionName': 'SetActorRotation', 'parameters': {'NewRotation': rotation, 'bSweep': True}, 'generateTransaction': True}
        
        else:
            print(Back.RED + 'Wrong command')
            continue

        response = requests.put(address + "/remote/object/call", headers = headers, data = json.dumps(data))
        if json.loads(response.text)["ReturnValue"]:
            print(Fore.GREEN + 'Responce: ' + "done")
        else:
            print(Fore.RED + 'Responce: ' + 'error')
    except KeyboardInterrupt:
        sys.exit(0)
    except TypeError:
        print(Back.RED + "Wrong input format")
    except ValueError:
        print(Back.RED + "Wrong input format")
    except IndexError:
        print(Back.RED + "Not enough args")
    except:
        print(Back.RED + "Something went wrong")
