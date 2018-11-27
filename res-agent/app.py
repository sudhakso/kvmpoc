import os
import sys
from os import listdir
from os.path import isfile, join
from datetime import datetime
import subprocess


import threading
import json
import logging
from logging.handlers import RotatingFileHandler


from flask import Flask, jsonify, request

import time
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler 
from dirwatcher import Watcher

app = Flask(__name__)

RES_AGENT_RESOUIRCES_DIR       = "/etc/resagent/resources/"
RES_AGENT_DIR                  = "/etc/resagent/"
RES_LOG                        = "/var/log/resagent.log"


# data = {"network": [], "domain": [], "volume": []}
@app.before_first_request
def activate_watcher():
    w = Watcher(app.logger)
    def run_watcher():
        while True:
            app.logger.info("Discovering new / updated resources in your environment ...")
            w.run()
    thread = threading.Thread(target=run_watcher)
    thread.start()

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
