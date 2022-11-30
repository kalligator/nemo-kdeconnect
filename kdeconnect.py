from subprocess import run, check_output
from re import search, sub
from urllib.parse import unquote
from urllib.request import url2pathname

def send_files(files, device_id, device_name):
    #print("KDEConnectExtension: Sharing Files:")
    for file in files:
        #print("  "+sub("^file://","",url2pathname(file.get_uri()))) # +": "), end='')
        result = run(["kdeconnect-cli", "-d", device_id, "--share", file.get_uri()],capture_output=True)
        #if result.returncode == 0: # TODO: KDEConnect-cli doesn’t seem to block, and so can’t return an error code on failure. Stupid pseudo-cli!
        #    print("Sucess")
        #else:
        #    print("Failed!\n    "+("\n    ".join(result.stderr.decode("utf-8").strip().split("\n"))))

def get_available_devices():
    devices_a = []
    devices = run(["kdeconnect-cli", "-a"],capture_output=True).stdout.decode("utf-8").strip().split("\n")
    #print("KDEConnectExtension: Found "+str(len(devices))+" device(s)")
    for device in devices:
        device_name = search("(?<=-\s).+(?=:\s)"         , device).group(0)
        device_id   = search("(?<=:\s)[a-z0-9_]+(?=\s\()", device).group(0).strip()
        devices_a.append({ "name": device_name, "id": device_id })
        #print("  " +device_name+" ("+device_id+")")
    return devices_a
