from azure.storage.queue import QueueService
import argparse
import json
import os
import requests
import smtplib
import socket
import time

# variables and enumerate list
stockurl = "http://dev.markitondemand.com/MODApis/Api/v2/Quote/jsonp?symbol="
gmpass = os.environ['gmpass']
gmuser = os.environ['gmuser']
azurestoracct = os.environ['azurestoracct']
azurequeue = os.environ['azurequeue']
azurequeuekey = os.environ['azurequeuekey'] + "==;"
l = []

# get host name (container id)
h = socket.gethostname()

while True:
    
    # set up azure queue
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    
    # get message from azure queue
    messages = queue_service.get_messages(azurequeue, num_messages=5)
    
    for message in messages:

         # delete message from azure queue
        queue_service.delete_message(azurequeue, message.id, message.pop_receipt)

        # data from queue
        s = message.content.split(':')
        symbols = s[0].split(';')
        email = s[1]

        # get stock quote and populate list
        for symbol in symbols:
            r = requests.get(stockurl + symbol)
            s = json.loads(r.text[18:-1])
            price = (s['LastPrice'])
            l.append(symbol + ' = ' + str(s['LastPrice']) + '\n')  

        # send email
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmuser,gmpass)
        header = 'To:' + email  + '\n' + 'From: ' + gmuser + '\n' + 'Subject:' + h + '\n'
        msg = header + ''.join(l)
        smtpserver.sendmail(gmuser, email, msg)
        smtpserver.close()

        del l[:]
