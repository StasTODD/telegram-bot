#!/bin/bash

tbot_script_file=main.py
tbot_script_path=/home/$USER/projects/telegram-bot/$tbot_script_file
tbot_script_pid=$(ps -axx | grep telegram | grep main.py | awk '{print $1}')

if [ $tbot_script_pid ]
  then
    echo "tbot script is running, it have pid: $tbot_script_pid"
  else
    $tbot_script_path
fi
