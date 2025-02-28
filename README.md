# Watering
Code related to the watering project

## Overview
This project implements an automated watering system for plants that can be controlled remotely using MQTT messages through AWS IoT Core. The system runs on a Raspberry Pi and uses GPIO pins to control water pumps.

## Features
- Remote control of watering via MQTT commands
- Ping/pong system to verify device connectivity
- Tracks last watering time
- Emergency stop functionality via MQTT
- Runs as a background service using Supervisor

## Requirements
- Raspberry Pi 4
- An AC submersible pump connected to GPIO pin
- AWS IoT Core account with proper certificates
- A 4 channel isolated relay module
- An 8G (16G recommended) microSD card
- A 5v 2A / 2.5A power supply
- A portable charger(to serve energy to the pump).
- Some jumper cables. 
- A container that can hold enough water
- A garden micro drip irrigation hose
- Some drip fittings

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
3. Place your AWS IoT certificates in the IOT-core-aws directory
4. Configure Supervisor to run the service

## Usage
The system uses MQTT topics for control:

- Start watering: plants/watering/{profile}
- Stop watering: plants/watering/stop
- Check device status: plants/device/ping

## Supervisor Commands
To update the supervisor config, from the folder /etc/supervisor run:

```
sudo supervisorctl reread
sudo supervisorctl update
```

Restart all services:

```
sudo supervisorctl restart all
```

For more information on Supervisor: [Supervisor as a Background Service Manager](https://www.piawesome.com/how-tos/Supervisor%20as%20a%20Background%20Service%20Manager.html)

## Project Structure
- src: Source code
  - plugins/: Plugin system for different watering behaviors
  - pubsub.py: AWS IoT Core MQTT communication
  - shared/: Constants and shared utilities
  - main.py: Entry point
- IOT-core-aws: AWS IoT certificates and keys
- water.supervisor.conf: Supervisor configuration

## TODO
- Run once a day automatically
  - Run automatically only if there was not a manual run through - MQTT messaging
- Store the running entries in a local DB like SQLite
- Through AWS MQTT, cancel today's auto run
- Notification system when water is running