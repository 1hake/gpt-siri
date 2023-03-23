#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title voice-gpt
# @raycast.mode fullOutput
# @raycast.argument1 { "type": "text", "placeholder": "input"}

# Optional parameters:
# @raycast.icon 🤖

filepath=/tmp/chat.txt
touch -c $filepath > $filepath

# activate venv
source $(pwd)/venv/bin/activate

echo $1

# Read the .env file and construct the command with environment variables
cmd="echo '' | sudo -S "
while IFS="=" read -r key value; do
    cmd+=" $key=$value"
done < $(pwd)/.env
# Add the Python script command to the end
cmd+=" python $(pwd)/gpt-siri.py $filepath &"
# Run the constructed command
eval "$cmd"

PID1=$!

tail -f $filepath &
PID2=$!


# Trap the interrupt signal (Ctrl+C) to stop both the Python script and the tail command
trap "kill $PID1 $PID2" SIGINT

# Wait for the Python script to finish
wait $PID1

# Once the Python script is done, terminate the tail command
kill $PID2
