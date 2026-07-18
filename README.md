# FitGirl Repack RSS Telegram Notifier

A lightweight, systemd-managed Python daemon that monitors the FitGirl Repacks RSS feed and sends immediate notifications to a Telegram chat whenever a new repack is published. RSS Feed is taken from https://fitgirl-repacks.site/ official website. The project has been made for educational purpose only.

## Features

* Automated RSS parsing using native Python standard libraries.
* Dynamic state tracking via a local JSON file that reloads continuously.
* Safe HTML escaping to comply with strict Telegram API formatting rules.
* Resilient network handling with explicit timeouts to prevent socket hangs.
* Systemd integration for persistent background monitoring and auto-restarts.

## Prerequisites

* Linux environment with systemd.
* Python 3.x installed.
* A Telegram Bot Token.
* A Telegram Chat ID.

## Installation

1. Deploy the Script: Save the Python monitoring script to the following path:
/usr/local/bin/fitgirlrss
2. Set Permissions: Apply execution permissions to the binary:
chmod +x /usr/local/bin/fitgirlrss

3. Deploy the Service Unit: Save the systemd configuration file to:
/etc/systemd/system/fitgirlrss.service

4. Configure Credentials: Edit the service unit file to include your live Telegram API credentials in the environment variables:
Environment="TELEGRAM_BOT_TOKEN=your_token_here"
Environment="TELEGRAM_CHAT_ID=your_id_here"

## Execution

Reload the systemd daemon to recognize the new service unit:systemctl daemon-reload

Enable the service to start automatically on system boot:systemctl enable fitgirlrss.service

Start the active monitoring loop:systemctl start fitgirlrss.service

## Tracking and Maintenance

* Database Location: /var/local/fitgirlrss.json
* Log Inspection: journalctl -u fitgirlrss.service -f

The service dynamically reads the JSON database from the disk at the start of every iteration. To force the script to re-send an alert for a specific repack, open the JSON database and delete the corresponding URL string. The service will detect the missing entry on the next cycle and dispatch a fresh Telegram notification.