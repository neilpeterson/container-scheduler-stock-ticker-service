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
emailbody = []

# get host name (container id)
hostname = socket.gethostname()

# functions
def getmessage ():

    # Get messages from Azure queue.
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)   
    messages = queue_service.get_messages(azurequeue, num_messages=5)
    return messages

def sendemail ( to_email, from_email, password, subject, body):

    # Send email - stock report.
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(from_email, password)
    header = 'To:' + to_email  + '\n' + 'From: ' + from_email + '\n' + 'Subject:' + subject + '\n'
    msg = header + ''.join(body)
    smtpserver.sendmail(from_email, to_email, msg)
    smtpserver.close()

def getstockprice (stockurl, symbol):

    try:
        r = requests.get(stockurl + symbol)
        s = json.loads(r.text[18:-1])
        price = (s['LastPrice'])
        #print(r.text[18:-1])
        return price
    except:
        print("Request Error - will retry")

def deletemessage (messageid, popreceipt):
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    queue_service.delete_message(azurequeue, messageid, popreceipt) 

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
                       
            if stockquote:
          
                emailbody.append(symbol + ' = ' + str(stockquote) + '\n')                
            
        if emailbody:
            sendemail (email, gmuser, gmpass, hostname, emailbody)
            del emailbody[:]

            # Delete message from queue.
            deletemessage(message.id, message.pop_receipt) 

        
