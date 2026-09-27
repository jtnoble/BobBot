#!/bin/bash

# The name of your application or the command to start it
APP_NAME="bobbot.py"
APP_COMMAND="python3.11 bobbot.py"

# Check if the application is running
if ! pgrep -f "$APP_NAME" > /dev/null
then
    echo "Application is not running. Starting it now..."
    $APP_COMMAND &
else
    echo "Application is running."
fi
