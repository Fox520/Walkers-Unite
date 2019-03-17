# -*- coding: utf-8 -*-
import socket
import threading
import json
import time
import random
import traceback
s = socket.socket()
host = "0.0.0.0"
port = 800
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
clients = []
defo = "Walker #"

def setup_name(connection):
    toUse = len(clients) + 1;
    if toUse < 10:
        q = defo + "00" + str(toUse)
    elif toUse <100:
        q = defo + "0" + str(toUse)
    else:
        q = defo + str(toUse)
    
    template = {"name": q}

    connection.send(json.dumps(template))
    auto_reply(connection)

#send num online
def runEveryWhile():
    while True:
        for x_x in clients:
            try:
                x_x.send("")
            except:
                clients.remove(x_x)
        template = {}
        tot = len(clients)
        msg = " def msg"
        if tot > 1:
            msg = " Walkers online"
        else:
            msg = "Only you online :/"
            tot = ""
        fin_msg = str(tot) + msg
        template["message_type"] = "online_number"
        template["walkers_online"] = fin_msg
        for x_x in clients:
            try:
                x_x.send(json.dumps(template))
            except:
                pass
        
        print("runeverywhile "+ fin_msg)
        time.sleep(5)

def auto_reply(connection):

    while True:
        try:
            try:
                data = str(connection.recv(4096))
                data = json.loads(data)
            except:
                continue
            template = {}
            type_msg = data["message_type"]
            try:

                if type_msg == "broadcast":
                    template["message_type"] = "short_text"
                    template["from"] = data["from"]
                    tmpText = data["text"]
                    template["text"] = tmpText
                    
                    if(len(tmpText) > 80 and len(tmpText) < 250):
                        template["message_type"] = "long_text"
                        
                    for x_x in clients:
                        try:
                            x_x.send("")
                        except:
                            x_x.close()
                            clients.remove(x_x)
                    for c_conn in clients:
                        try:
                            c_conn.send(json.dumps(template))
                        except:
                            pass
                
                elif type_msg == "num_online":
                    for x_x in clients:
                        try:
                            x_x.send("")
                        except:
                            clients.remove(x_x)
                    template["type"] = "num_online"
                    template["msg"] = str(len(clients))
                    connection.send(json.dumps(template))
            except:
                print(traceback.format_exc())
        except:
            print(traceback.format_exc())


print "Taking care of messages - Public"

shutdown = False
threading.Thread(target=runEveryWhile).start()
while not shutdown:
    conn, addr = s.accept()
    if conn not in clients:
        clients.append(conn)

    threading.Thread(target=setup_name, args=(conn,)).start()