[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)

# Server Monitoring API
Monitor your server stats and make them easily accessable through an API.


## Getting started
To run the script the following variables are required, they can be set as an global ENV var on the server, it can be passed through in a `.env` file or each given as a command argument.
|ENV var|Command arg|Default value|Explain|
|-------|-----------|-------------|-------|
|n/a|-v", "--verbose",|n/a|Enable console logging|
|ENV_PATH|-e", "--env-path"|.env|Path to the env file|
|LOG_DIR|-l", "--log-dir"|/var/log/server-monitor-api|Directory for log files|
|LOG_FILENAME|-f", "--log-filename"|app|Log filename|
|LOG_LEVEL|-L", "--log-level"|INFO|Log level|
|HOST_IP|-i", "--host-ip"|0.0.0.0|API server IP address|
|HOST_PORT|-p", "--host-port"|8000|API server port|
|MONITORED_DISKS|-d", "--monitored-disks"|/|Comma-separated list of monitored disks|
|MONITORED_PROCESSES|-P", "--monitored-processes"|ssh|Comma-separated list of monitored processes|
|OAUTH_SECRET_KEY|-s", "--oauth-secret-key|change-this-secret-key|The secret key to encode JWT tokens|
|OAUTH_ALGORITHM|-a", "--oauth-algorithm"|HS256|OAuth2 algorithm to encode JWT tokens|
|OAUTH_TOKEN_EXPIRE|-t", "--oauth-token-expire|60|Time in minutes the OAuth2 token expires|
|API_RATE_LIMIT|-r", "--api-rate-limit|5|Maximum request per second|
|FAILED_ATTEMPT_LIMIT|-F", "--failed-attempt-limit|5|Max failed attempts before blocking token request|
|BLOCK_TIME_MINUTES|-b", "--block-time-minutes|10|Block duration in minutes|
|DB_NAME|-D", "--db-name"|users.db|Name of the database|
|n/a|--add-users||Add a new user to the database|
|n/a|--db-username||Username for the new user|
|n/a|--db-password||Password for the new user|


## Setup the environment
Create the python environment and install required packages
```
cd ~./server-monitor/monitoring_api/
python3.10 -m venv env
source env/bin/activate
pip install -r requirements.txt
deactivate
```


## Usage
### Create a user
```
# Run the script
~./server-monitor/monitoring_api/env/bin/python3 ~./server-monitor/monitoring_api/main.py --add-users --db-username foo --db-password bar
# or
source ~./server-monitor/monitoring_api/env/bin/activate
python3 ~./server-monitor/monitoring_api/main.py --add-users --db-username foo --db-password bar
```

### Start the API
```
# Run the script
~./server-monitor/monitoring_api/env/bin/python3 ~./server-monitor/monitoring_api/main.py
# or
source ~./server-monitor/monitoring_api/env/bin/activate
python3 ~./server-monitor/monitoring_api/main.py
```


## Create systemd service
Create `/etc/systemd/system/server-monitor-api.service` from `~/server-monitor/monitoring_api/files/server-monitor-api.service` and change where necessary.

Enable and start the service
```
sudo systemctl daemon-reload
sudo systemctl enable server-monitor-api.service
sudo systemctl start server-monitor-api.service
```
