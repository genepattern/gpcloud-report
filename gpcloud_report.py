#! /usr/bin/env python3 
''' This is the '''

# Order Dicts
from collections import OrderedDict
from operator import itemgetter

# Set the date range to weekly
import datetime
from datetime import timedelta
current_date = "%s" % datetime.date.today()
past_date = "%s" % (datetime.date.today() - timedelta(days=7))
# current_date = "2020-08-16"
# past_date = "2020-08-09"

# Start timing the execution of the program
import time
start_time = time.monotonic()

# Import local config file (config.json)
import json

with open('/home/ec2-user/gpcloud-report/config.json') as json_data_file:
     data = json.load(json_data_file)

#with open('config.json') as json_data_file:
#    data = json.load(json_data_file)

for key,val in data.items():
    if key == "gp":
        for k,v in val.items():
            gp_login = k
            gp_pass = v
    elif key == "smtp":
        for k,v in val.items():
            smtp_address = k
            smtp_port = v
    elif key == "serverLogin":
        for k,v in val.items():
            server_login = k
            server_key = v
    elif key == "serverSendmail":
        for k,v in val.items():
            server_from = k
            server_to = v


# Pull the usage statistics from the REST API
import requests
from requests.auth import HTTPBasicAuth
server_base = "Cloud" ## CHANGE THE BASE TO MATCH API
URL = 'http://%s.genepattern.org' % server_base.lower()
full_url = '%s:80/gp/rest/v1/usagestats/user_summary/%s/%s' %(URL, past_date, current_date)

r = requests.get(full_url, auth=HTTPBasicAuth(gp_login,gp_pass), timeout=1700)
input = r.json()

# Write file to temp folder
g = open('gp_stats_tmp/%s_%s.json' %(past_date,current_date), "w")
g.write('%s' % (input))
g.close()

# Flip date
from datetime import datetime
current_date = datetime.strptime(current_date, '%Y-%m-%d').strftime('%m-%d-%Y')
past_date = datetime.strptime(past_date, '%Y-%m-%d').strftime('%m-%d-%Y')

# Recreate all JSON into dictionaries
## Reports
report_period = {}
report_period['Report Period'] = ''
report_period['Start'] = past_date
report_period['End'] = current_date

# Total users
total_users = {}
total_users['Total Users'] = input['TotalUsersCount']

## Weekly Users
weekly_users = {}
weekly_users['New Users'] = input['NewUserRegistrations']
weekly_users['Returning Users'] = input['ReturningUsersCount']

## New Users
new_users = {}
new_users['User'] = 'Email'
new_users['Total'] = input['NewUserRegistrations']
new_key1=''
for x in range(len(input['NewUsers'])):
    for key, value1 in input['NewUsers'][x].items():
        if key == 'user_id': 
            new_key1 = value1
        elif key == 'email':
            new_value1 = value1
            new_users[new_key1] = new_value1

## Modules
modules_run = {}
# modules_run['Module'] = 'Count'
new_key2=''
for x in range(len(input['ModuleRunCounts'])):
    for key, value2 in input['ModuleRunCounts'][x].items():
        if key == 'moduleName': 
            new_key2 = value2
        elif key == 'jobsRun':
            new_value2 = value2
            modules_run[new_key2] = new_value2
sorted_modules_run = [[k,v] for k,v in modules_run.items()]
sorted_modules_run.sort(key = lambda x: x[1], reverse=True)
sorted_modules_run.insert(0,['Module','Count'])
modules = [
    sorted_modules_run[i][0]
    for i in range(len(sorted_modules_run))
] 
count = [
    sorted_modules_run[i][1]
    for i in range(len(sorted_modules_run))
] 
ordered_modules_run = []
ordered_modules_run.append(modules)
ordered_modules_run.append(count)

## User Jobs Run
user_jobs_run = {}
# user_jobs_run['User'] = 'Jobs Run'
new_key3=''
for x in range(len(input['UserRunCounts'])):
    for key, value3 in input['UserRunCounts'][x].items():
        if key == 'user_id': 
            new_key3 = value3
        elif key == 'jobsRun':
            new_value3 = value3
            user_jobs_run[new_key3] = new_value3
sorted_user_jobs_run = [[k,v] for k,v in user_jobs_run.items()]
sorted_user_jobs_run.sort(key = lambda x: x[1], reverse=True)
sorted_user_jobs_run.insert(0,['User','Jobs Run'])
users2 = [
    sorted_user_jobs_run[i][0]
    for i in range(len(sorted_user_jobs_run))
] 
count2 = [
    sorted_user_jobs_run[i][1]
    for i in range(len(sorted_user_jobs_run))
] 
ordered_user_jobs_run = []
ordered_user_jobs_run.append(users2)
ordered_user_jobs_run.append(count2)

## Total Jobs
total_jobs = {}
total_jobs['Total Jobs'] = 'Since 12-15-2017'
total_jobs['Total'] = input['TotalJobs']

## Jobs by int/ext domain
jobs_run_int_ext = {}
jobs_run_int_ext['Total Jobs'] = 'Jobs'
jobs_run_int_ext['Total'] = input['JobsRun']

## Job by domain names
# jobs_run_dom = OrderedDict()
# jobs_run_dom['Domain'] = 'Jobs'
# jobs_run_int_ext['Total'] = input['JobsRun']
# new_key4=''
# for x in range(len(input['DomainRunCounts'])):
#     for key, value4 in input['DomainRunCounts'][x].items():
#         if key == 'domain': 
#             new_key4 = value4
#         elif key == 'jobsRun':
#             new_value4 = value4
#             jobs_run_dom[new_key4] = new_value4

## Modules errors
module_error_count = []
a = ['Module']
b = ['Count']
for x in range(len(input['ModuleErrorCounts'])):
    for key, value in input['ModuleErrorCounts'][x].items():
        if key == 'moduleName':
            a.append(input['ModuleErrorCounts'][x][key]) 
        elif key == 'jobsRun':
            b.append(input['ModuleErrorCounts'][x][key])
module_error_count.append(a)
module_error_count.append(b)

# Dictionary to List function
def dict_to_list(dict_var):
    h = []
    a = []
    b = []
    for key, value in dict_var.items():
        if key != '':
            a.append(key)
            b.append(value)
        elif key == '':
            b.append(value)
    h.append(a)
    h.append(b)
    return h    

# Merge list names
# names_list = [report_period, total_users, weekly_users, new_users, modules_run, total_jobs, jobs_run_int_ext, user_jobs_run,  jobs_run_dom]
names_list = [report_period, total_users, weekly_users, new_users, total_jobs, jobs_run_int_ext]

# Convert all dict to lists 
new_list = []
for name in names_list[:4]:
    new_list.append(dict_to_list(name))
new_list.append(ordered_modules_run)
for name in names_list[4:]:
    new_list.append(dict_to_list(name))
new_list.append(ordered_user_jobs_run)

# Create list of readable titles 
titles_list = ['Report Period', 'Total Users', 'User login statistics, this week', 'New Users, this week', 'Modules run this week, by number', 'Total Jobs Run', 'Jobs run this week', 'Jobs run this week, by User']

# Convert list to styled html table function
def list_to_htmltable(dictObj):
    p = []
    p.append('<h2>%s</h2>'%(titles_list[new_list.index(dictObj)]))
    dict2list = [list(i) for i in zip(*dictObj)]
    p.append('<table>')
    for x in range(len(dict2list)):
        p.append('<tr>')
        for y in range(len(dict2list[x])):
            if dict2list[x][y] == 'Module' or dict2list[x][y] == "Count" or dict2list[x][y] == "Total Jobs" or dict2list[x][y] == "Since %s" % (past_date) or dict2list[x][y] == "Domain" or dict2list[x][y] == "Jobs" or dict2list[x][y] == "User" or dict2list[x][y] == "Email" or dict2list[x][y] == "Total Users" or dict2list[x][y] == "Report Period" or dict2list[x][y] == "" or dict2list[x][y] == "Jobs Run" :
                p.append('<th>'+ '%s' % (dict2list[x][y]) + '</th>')
            else:
                p.append('<td>'+ '%s' % (dict2list[x][y])+ '</td>')
        p.append('</tr>')
    p.append('</table><br>')
    report_html.append("".join(p))
    return

# Create a full html page from newly styled tables
report_html = []
report_html.append(
    '''<html><head>
    <style>
    .column {float: left; width: 50%;} 
    .row:after {content: "";display: table;clear: both;}
    table{border: 1px solid black; padding: 5px; border-collapse: collapse; margin-bottom: 2px;}
    th{border: 1px solid black; padding: 5px; border-collapse: collapse;}
    td{border: 1px solid black; padding: 5px; border-collapse: collapse;}
    h2{margin-top: 0px;}
    </style>
    </head>
    <div class="row">
    <div class="column">''')
for x in new_list[:5]:
    list_to_htmltable(x) 

report_html.append('</div><div class="column">') 

for x in new_list[5:]:
    list_to_htmltable(x)

report_html.append('</div></div>') 
report_html.append('</html>')
string = " ".join(report_html)

# Send out email to desired recipients
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

html = "<h2>GP %s Server Report (%s), <br>week ending %s</h2><br>%s" % (server_base,full_url,current_date,string)
message = MIMEMultipart(
    "alternative", None, [MIMEText(html,'html')])
message['Subject'] = 'GP %s Server Usage Statistics: %s to %s' % (server_base,past_date,current_date)

# Define server and login information
smtp_server = smtplib.SMTP('%s' % (smtp_address),smtp_port)
smtp_server.ehlo()
smtp_server.starttls()
smtp_server.login('%s' % (server_login), '%s' % (server_key))
smtp_server.sendmail('%s' % (server_from), server_to, message.as_string())
smtp_server.quit()

# Validate the success of the command
end_time = time.monotonic()
print(timedelta(seconds=end_time - start_time))
print('Email sent successfully')

# # Send out exception email
# from tabulate import tabulate
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib

# html = "<h2>TIMEOUT EXCEPTION: GP %s Server Report (%s), <br>week ending %s</h2><br>" % (server_base,full_url,current_date)
# message = MIMEMultipart(
# "alternative", None, [MIMEText(html,'html')])
# message['Subject'] = 'TIMEOUT EXCEPTION: GP %s Server (%s) User Statistics: %s to %s' % (server_base,full_url,past_date,current_date)

# # Define server and login information
# smtp_server = smtplib.SMTP('%s' % (smtp_address),smtp_port)
# smtp_server.ehlo()
# smtp_server.starttls()
# smtp_server.login('%s' % (server_login), '%s' % (server_key))
# smtp_server.sendmail('%s' % (server_from), server_to, message.as_string())
# smtp_server.quit()

# # Validate the success of the command
# end_time = time.monotonic()
# print(timedelta(seconds=end_time - start_time))
# print('Timeout exception. Email sent')

