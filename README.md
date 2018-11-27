# kvmpoc
request-agent-discovery manager

# Setup
Setup a Python 2.7 environment, and do the following.

pip install -r requirements.txt 

# Run
## To start the discovery server,
1. sudo python $REPO/disco-manager/app.py "Bind IP Address"

## To start the resource agent,
1. export DISCO_SERVER = <Bind IP address of Discovery server>
2. sudo python $REPO/res-agent/app.py "Bind IP Address"

# Changes 
This program needs access to following directories
1. /var/log/disco.log
2. /etc/disco/ for Discovery server
3. /etc/resagent/resources for Resource agent
4. /var/log/resagent.log
