#!/bin/bash

set -v on

rm -rf agent_application

rm -f cp_ice_.sh
cp cp_ice.sh cp_ice_.sh
chmod 754 cp_ice_.sh

./cp_ice_.sh

cxfreeze application_main.py --target-dir agent_application
if [ $? -ne 0 ]  
then
  echo "******** cxfreeze application_main.py failed ********"
  exit 1
fi

cxfreeze register.py --target-dir agent_application
if [ $? -ne 0 ]  
then
  echo "******** cxfreeze application_main.py failed ********"
  exit 1
fi

cp -vf remote_agent.config ./agent_application
cp -vf remote_agent.ini ./agent_application
cp -vf agent_application.initd_cfg ./agent_application
cp -vf agent_application.service ./agent_application

tar -zcvf ./agent_application.tar.gz ./agent_application
if [ $? -ne 0 ]  
then
  echo "******** tar -zcvf ./agent_application.tar.gz ./agent_application failed ********"
  exit 1
fi
