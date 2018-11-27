import os
import sys
from os import listdir
from os.path import isfile, join
from datetime import datetime

import threading
import json
import logging
from logging.handlers import RotatingFileHandler


from flask import Flask, jsonify, request
from time import sleep
app = Flask(__name__)

DISCOMAN_AGENT_DIR  = "/etc/discoman/agents"
DISCOMAN_DIR        = "/etc/discoman"
DISCOLOG             = "/var/log/disco.log"

@app.route('/')
def hello():
    app.logger.info("(Re) Starting Discovery Manager Service version 0.11.1 ....")
    app.logger.info("Connecting to the configured controller")
    app.logger.info("Connected to host controller ... OK")
    app.logger.info("Loading existing inventory ... ")
    inventory = [f for f in listdir("/etc/discoman/") if isfile("/etc/discoman/" + f)]
    for inv in inventory:
    	app.logger.info("Loading %s ...", inv)
    	app.logger.info("Loaded %s ... OK", inv)
    return "Success!"


@app.route('/node/status', methods=['GET'])
def ReportStatus():
        responsestat = {}
        # check if at least one host has reported status
        if not os.path.exists("/etc/discoman/agents/"):
            app.logger.error("No host found...")
            return jsonify(responsestat)
            
        # Check if the host is registered already
        inventory = [f for f in os.listdir("/etc/discoman/agents") if os.path.isdir("/etc/discoman/agents/" + f)]
        for agentdir in inventory:
            _stat = {"HostName" : agentdir,
                     "Status" : "ACTIVE",
                     "Created": datetime.fromtimestamp(os.path.getctime("/etc/discoman/agents/" + agentdir)).strftime('%Y-%m-%d %H:%M:%S'),
                     "Last Updated" : datetime.fromtimestamp(os.path.getmtime("/etc/discoman/agents/" + agentdir)).strftime('%Y-%m-%d %H:%M:%S')}
            responsestat[agentdir] = _stat
        return jsonify(responsestat)

# data = {"hostname": "hostname"}
@app.route('/node/register', methods=['POST'])
def ReportRequests():
        data = request.data
        dataDict = json.loads(data)
        app.logger.info("New Host Registration Report Message Received... %s", dataDict['hostname'])
        app.logger.info("Checking if cache needs to be built up ... %s", dataDict['hostname'])
        
        # prep the folder
        if not os.path.exists("/etc/discoman/agents/"):
            os.mkdir("/etc/discoman/agents/")

        # Check if the host is registered already
        agentname = dataDict['hostname']
        inventory = [f for f in os.listdir("/etc/discoman/agents") if os.path.isdir("/etc/discoman/agents/" + f)]
        if agentname in inventory:
            app.logger.info("Host is already registered %s...", agentname)
        else:
            app.logger.info("Creating cache of connection for the host %s...", agentname)
            os.mkdir("/etc/discoman/agents/" + agentname)

        app.logger.info("Ready for inventory synchronize event from the Host %s...", agentname)
        return "Success"

# data = {"network": [], "domain": [], "volume": []}
@app.route('/node/upload/<agentname>', methods=['POST'])
def UploadRequests(agentname):
        data = request.data
        dataDict = json.loads(data)
        app.logger.info("Host %s is trying to report changes ...", agentname)
        datadict = {"domain": dataDict["domain"],
                    "network": dataDict["network"],
                    "volume": dataDict["volume"]
                    }
        app.logger.info("Host reported changes %s ...", agentname)
        app.logger.info("Change Record for host %s, Domains = %d, Networks = %d, Volumes = %d ...", agentname,
                        len(datadict["domain"]), len(datadict["network"]), len(datadict["volume"]))
        # checking is host is registered
        inventory = [f for f in os.listdir("/etc/discoman/agents") if os.path.isdir("/etc/discoman/agents/" + f)]
        if agentname not in inventory:
            app.logger.error("Host not registered %s...", agentname)
            app.logger.error("Changes will be ignored for host %s", agentname)
        
        # caches the content
        for item in ["network", "domain", "volume"]:
            with open("/etc/discoman/agents/" + agentname + '/' + item + ".json", 'w') as outfile:
                json.dump(datadict[item], outfile)
    
        app.logger.info("Change will be reported to the Openstack Controller ...")
        app.logger.info("Working posting changes to Openstack from host %s ...", agentname)
        sleep(10)
        app.logger.info("Still working posting changes from host %s ...", agentname)
        sleep(10)
        app.logger.info("Still working posting changes from host %s ...", agentname)
        sleep(10)
        app.logger.info("Still working posting changes from host %s ...", agentname)
        sleep(10)
        app.logger.info("Config upload complete for %s ...", agentname)
        app.logger.info("Verifying openstack configurations for host %s ...", agentname)
        sleep(10)
        for network in dataDict['network']:
            app.logger.info("Network Added/Updated %s: ", network)
        for vm in dataDict['domain']:
            app.logger.info("Guest Added/Updated : %s", vm)
        app.logger.info("Configuration upload completed for %s ...", agentname)
        return "Success!"

if __name__ == '__main__':
	handler = RotatingFileHandler(DISCOLOG, maxBytes=10000, backupCount=1)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)
	app.logger.setLevel(logging.INFO)

	app.run(host=sys.argv[1], port=9999)
