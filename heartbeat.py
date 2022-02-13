import requests
import time
def heartbeat(server_name,port_num,player_count):
    while (True):
        url = "http://classicube.net/heartbeat.jsp"

        parameters = {}
        parameters["port"] = port_num
        parameters["max"] = player_count
        parameters["name"] = server_name
        parameters["public"] = True
        parameters["version"] = 7
        parameters["salt"] = "0123456789abcdef"
        parameters["software"] = "PyCube 0.0.2"

        r = requests.get(url = url, params = parameters)

        print("Sending heartbeat to classicube")
    
        time.sleep(45)

