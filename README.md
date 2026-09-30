Hello this is a monitoring and security tool built for Raspberry pi 2b. This uses Grafana, docker, postgresql, Grafana and discord.

## Features

- Docker container monitoring
- PostgreSQL data storage
- Grafana dashboards
- Discord slash commands
- Discord alerts
- Honeypot attack logging
- Automated database backups
- Off-device backup replication
- UFW firewall protection

## Discord Commands

### /health
Displays system health information.

### /status
Shows container status.

### /honeypot
Shows recent honeypot activity and top attackers.

### /backup
Shows the latest backup information.

### /dashboard
Returns a screenshot of the Grafana dashboard.

## Technologies Used

- Python
- Docker
- PostgreSQL
- Grafana
- Discord.py
- Raspberry Pi OS

## Architecture

Ubuntu Laptop
→ Discord Bot

Raspberry Pi
→ PostgreSQL
→ Grafana
→ Monitoring Containers
→ Honeypot
→ Backup Service

## Future Improvements

- Fail2Ban integration
- TLS encryption
- MFA
- Enhanced honeypot capabilities

