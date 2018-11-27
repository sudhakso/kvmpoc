import os
import sys
from os import listdir
from os.path import isfile, join
from datetime import datetime
import subprocess
import requests

import threading
import json
import logging
from logging.handlers import RotatingFileHandler


from flask import Flask, jsonify, request

import time
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler 

app = Flask(__name__)

RES_AGENT_RESOUIRCES_DIR       = "/etc/resagent/resources/"
RES_AGENT_DIR                  = "/etc/resagent/"
RES_LOG                        = "/var/log/resagent.log"


# data = {"network": [], "domain": [], "volume": []}
@app.before_first_request
def activate_watcher():
    
    def run_watcher():
        try:
            while True:
                app.logger.info("Discovering new / updated resources in your environment ...")
                if os.listdir(RES_AGENT_RESOUIRCES_DIR):
                    try:
                        # export the file
                        inventory = [f for f in listdir(RES_AGENT_RESOUIRCES_DIR) if isfile(RES_AGENT_RESOUIRCES_DIR + f)]
                        for afile in inventory:
                            with open(RES_AGENT_RESOUIRCES_DIR + afile) as json_file:
                                json_data = json.load(json_file)
                                payload = {afile : json_data}
                                # Send HTTP request
                                if 'DISCO_SERVER' in os.environ:
                                    base_url= os.enviro["DISCO_SERVER"]
                                    final_url="/{0}/node/upload/{1}".format(base_url,os.environ['HOSTNAME'])
                                    response = requests.post(final_url, data=payload)
                                    app.logger.info("Response %s :", response.text) #TEXT/HTML
                                    app.logger.info("Response Code = %d, Reason = %s", response.status_code, response.reason) #HTTP
                                else:
                                    app.logger.error("ERROR: Set the environment variable DISCO_SERVER")
                                    break
                    except Exception as e:
                        app.logger.error("Format Exception : %s", str(e))
                else:
                    app.logger.info("Nothing new to upload...")
                # graceful sleep
                time.sleep(10)
        except KeyboardInterrupt:
            sys.exit(0)
            
    thread = threading.Thread(target=run_watcher)
    try:
        thread.start()
    except KeyboardInterrupt:
        sys.exit(0)

@app.route('/')
def hello():
    app.logger.info("(Re) Starting Resource Agent version 0.11.1 ....")
    app.logger.info("Connecting to the discovery server ...")
    app.logger.info("Connected to dsicovery server ... OK")
    app.logger.info("Locking the inventory directory %s ...", RES_AGENT_RESOUIRCES_DIR)
    if not os.path.exists(RES_AGENT_RESOUIRCES_DIR):
        app.logger.error("ERROR : Resource directory not found %s ...", RES_AGENT_RESOUIRCES_DIR)
        app.logger.error("ERROR : Create the resource directory %s ...", RES_AGENT_RESOUIRCES_DIR)
    else:
    	app.logger.info("Locked %s ... OK", RES_AGENT_RESOUIRCES_DIR)
    return "Success!"

# data = {"cmd": "/usr/bin/virsh stop <vm-id"}
@app.route('/node/cmd', methods=['POST'])
def CmdRequests():
        data = request.data
        dataDict = json.loads(data)
        cmd = dataDict['cmd']
        app.logger.info("Execute command %s ... ", cmd)
        
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            app.logger.info("Response %s ... ", line)
        retval = p.wait()
        return "Success"

if __name__ == '__main__':
	handler = RotatingFileHandler(RES_LOG, maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.INFO)

	app.run(host=sys.argv[1], port=10000)
