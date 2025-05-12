#!/bin/bash
python3 /home/ec2-user/gpcloud-report/gpcloud-report.py

id >> /home/ec2-user/gpcloud-report/cron_exec_times.txt
date >> /home/ec2-user/gpcloud-report/cron_exec_times.txt
