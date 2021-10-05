#!/bin/bash

# Serves website as a daemon
/usr/local/bin/ptgbot-web --debug /etc/ptgbot/ptgbot.config

# Run in foreground as the main process
/usr/local/bin/ptgbot -d /etc/ptgbot/ptgbot.config
