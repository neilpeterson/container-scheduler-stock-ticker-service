from azure.storage.queue import QueueService
import argparse
import json
import os
import requests
import smtplib
import socket
import time

# TODO - test all of this, move parse into function, move delete message (queue) into functon, deal with http exceptions.

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

# functions

def getmessage ():

    # Get messages from Azure queue.
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)   
    messages = queue_service.get_messages(azurequeue, num_messages=5)
    return messages

def sendemail ( to_email, from_email, password, subject ):

    # Send email - stock report.
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(from_email, password)
    header = 'To:' + to_email  + '\n' + 'From: ' + from_email + '\n' + 'Subject:' + subject + '\n'
    msg = header + ''.join(l)
    smtpserver.sendmail(from_email, to_email, msg)
    smtpserver.close()

def getstockprice (stockurl, symbol):

    r = requests.get(stockurl + symbol)
    s = json.loads(r.text[18:-1])
    price = (s['LastPrice'])
    return price

def deletemessage (id, popreceipt):
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    queue_service.delete_message(azurequeue, message.id, message.pop_receipt) 

while True:
  
    # Get messages from Azure queue.
    messages = getmessage()
    
    for message in messages:

        # Get symbols and email address from each message - TODO, moves these into function.
        s = message.content.split(':')
        symbols = s[0].split(';')
        email = s[1]

        # Get stock quote and populate list.
        for symbol in symbols:
                
            stockquote = getstockprice (stockurl, symbol)

            print(s[1])
                            
            if stockquote:

                #print(s[0])
            
                l.append(symbol + ' = ' + str(stockquote) + '\n')

                print(stockquote)

                # Delete message from queue.
                deletemessage(message.id, message.pop_receipt)
                #queue_service.delete_message(azurequeue, message.id, message.pop_receipt)

                # Send email - stock report.
                #sendemail (email, gmuser, gmpass, h)

                print("email sent")

                # Clear stock report list.
                del l[:]                    
            
            else:

                print("else")