# myPlanet
_An Air Quality Monitoring Bot for Expedition 2016 using Planet OS_  
**by [Collective Acuity](https://collectiveacuity.com)**

## Features
- Collects personal location and air quality data every hour
- Message "air" to bot returns air quality data at current location
- Ready to deploy to a docker container

## Requirements
- Python dependencies listed in Dockerfile
- **Valid OAuth2 access token from Moves App**

## Components
- Alpine Edge (OS)
- Python 3.5.2 (Environment)
- Gunicorn 19.4.5 (Server)
- Flask 0.11.1 (Framework)
- Gevent 1.1.2 (Thread Manager)
- SQLAlchemy 1.1.1 (Database ORM)
- TelegramBot API (Messaging)
- Moves App (Location Tracking)
- Planet OS (Air Quality Data)

## Dev Env
- Docker (Provisioning)
- GitHub (Version Control)
- Postgres (JobStore Database)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.5