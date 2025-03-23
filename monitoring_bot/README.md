[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)

# Server Monitoring Bot
Monitor your server stats and easily get notified through a Telegram bot.


## Getting started
To run the script the following variables are required, they can be set as an global ENV var on the server, it can be passed through in a `.env` file or each given as a command argument.
|ENV var|Command arg|Default value|Explain|
|-------|-----------|-------------|-------|
|n/a|-v, --verbose|n/a|Enable console logging|
|ENV|-e, --env|dev|Set env mode|
|ENV_PATH|-E, --env-path|.env|Location of the env file|
|CHAT_ID|-i, --chat-id|0|User or group ID of the Telegram chat|
|ALLOWED_USERS|-a, --allowed-users|0|Single or multiple Telegram IDs, seperated by a comma, for usage restriction|
|LOG_DIR|-l, --log-dir|/var/log/server-monitor-bot|Directory for log files|
|LOG_FILENAME|-f, --log-filename|app.log|Log filename|
|LOG_LEVEL|-L, --log-level|INFO|Log level|
|BOT_TOKEN|-t, --bot-token|change-this-token|Live bot token|
|BOT_TOKEN_DEV|-T, --bot-token-dev|change-this-token|Dev bot token|
|API_ADDRESS|-b, --api-address|0.0.0.0|Url of the monitoring API|
|API_PORT|-p, --api-port|8000|Port of the monitoring API|
|API_USER|-u, --api-user|admin|User for the monitoring API|
|API_PASSWORD|-P, --api-password|change-this-password|Password for the monitoring API|
|IP_THRESHOLD|-q, --ip-threshold|0.0.0.0|IP to check|
|APT_THRESHOLD|-A, --apt-threshold|10|APT packages threshold|
|APT_SECURITY_THRESHOLD|-s, --apt-security-threshold|1|APT security packages threshold|
|DISK_THRESHOLD|-d, --disk-threshold|5|Free disk space threshold|
|LOAD_1_THRESHOLD|-x, --load-1|5|1 min load threshold|
|LOAD_5_THRESHOLD|-y, --load-5|3|5 min load threshold|
|LOAD_15_THRESHOLD|-z, --load-15|2|15 min load threshold|
|RAM_THRESHOLD|-r, --ram-threshold-threshold|25|Free RAM threshold|
|SWAP_THRESHOLD|-S, --swap-threshold-threshold|25|Free swap threshold|
|USERS_THRESHOLD|-U, --users-threshold-threshold|2|Logged in users threshold|
|ALERT_INTERVAL|-m, --alert-interval|300|Interval for alerts te be send in seconds|
|SERVER_NAME|-n, --server-name|server-name|Name of the monitor server|
|LOG_RETENTION|-R, --log-retention|30|Log retention days, for the privacy policy|
|BOT_OWNER|-B, --bot-owner|owner|Bot owner username, for the privacy policy|


## Setup the environment
Create the python environment and install required packages
```
cd ~./server-monitor/monitoring_bot/
python3.10 -m venv env
source env/bin/activate
pip install -r requirements.txt
deactivate
```


## Usage
```
# Run the script
~./server-monitor/monitoring_bot/env/bin/python3 ~./server-monitor/monitoring_bot/main.py
# or
source ~./server-monitor/monitoring_bot/env/bin/activate
python3 ~./server-monitor/monitoring_bot/main.py
```


## Create systemd service
Create `/etc/systemd/system/server-monitor-bot.service` from `~/server-monitor/monitoring_bot/files/server-monitor-bot.service` and change where necessary.

Enable and start the service
```
sudo systemctl daemon-reload
sudo systemctl enable server-monitor-bot.service
sudo systemctl start server-monitor-bot.service
```
