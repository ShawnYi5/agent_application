#!/bin/bash

if [ ! -f "agent_application.tar.gz" ]; then
  echo "******** not agent_application.tar.gz ********"
  exit 1
fi

scp agent_application.tar.gz 172.16.1.199:/home/package/linux_module/x64/
scp agent_application.tar.gz 172.16.1.199:/home/package/Release/linux_module/x64/
scp agent_application.tar.gz 172.16.1.199:/home/package/Release_plus/linux_module/x64/

if [ $? -ne 0 ]  
then  
  echo "******** scp agent_application.tar.gz failed ********"
  exit 1
fi
