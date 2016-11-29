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
  
    # Get messages from Azure queue.
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)   
    messages = queue_service.get_messages(azurequeue, num_messages=5)
    
    for message in messages:

        # Get symbols and email address from each message.
        s = message.content.split(':')
        symbols = s[0].split(';')
        email = s[1]

        # Get stock quote and populate list.
        for symbol in symbols:
            try:
                time.sleep(5)
                r = requests.get(stockurl + symbol)
                s = json.loads(r.text[18:-1])
                price = (s['LastPrice'])
                l.append(symbol + ' = ' + str(s['LastPrice']) + '\n')

                # Delete message from queue.
                queue_service.delete_message(azurequeue, message.id, message.pop_receipt)

            except:
                
                # Temp fix for HTTP exceptions. The message should remain on the queue and re-processed.
                pass

        # Send emial stock repor.
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmuser,gmpass)
        header = 'To:' + email  + '\n' + 'From: ' + gmuser + '\n' + 'Subject:' + h + '\n'
        msg = header + ''.join(l)
        smtpserver.sendmail(gmuser, email, msg)
        smtpserver.close()

        # Clear stock report list.
        del l[:]
