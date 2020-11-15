#!/bin/bash

tbot_script_file=main.py
tbot_script_path=/home/stastodd/projects/telegram-bot/
tbot_script_pid=$(ps -axx | grep telegram-bot | grep main.py | awk '{print $1}')

if [ $tbot_script_pid ]
  then
    echo "tbot script is running, it have pid: $tbot_script_pid"
  else
    cd $tbot_script_path ; ./$tbot_script_file
fi