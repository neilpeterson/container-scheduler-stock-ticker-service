from azure.storage.queue import QueueService
import json
import os
import random
import requests

# grab environment variables
azurestoracct = os.environ['azurestoracct']
azurequeue = os.environ['azurequeue']
azurequeuekey = os.environ['azurequeuekey'] + "==;"
image = os.environ['image']
queuelength = os.environ['queuelength']

if "docker" in os.environ:
    docker = os.environ['docker']

if "chronos" in os.environ:
    chronos = os.environ['chronos']

while True:

    # set up azure queue
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    metadata = queue_service.get_queue_metadata(azurequeue)
    count = metadata.approximate_message_count
    print(count)    
            
    if "docker" in os.environ:

        # get report container count

        print(docker)
        
        #reportcount = <docker query>
        headers = {'Content-Type': 'application/json'}
        r2 = requests.get(docker + "json?all=1&before=8dfafdbc3a40&size=1")
        print(r2.Content)

        #if count > reportcount * queuelength

        # docker container header
        #data = json.loads('{"Image": "' + image + '"]}')
        #print(data)
    
        # create and start docker container
        #headers = {'Content-Type': 'application/json'}
        #r = requests.post(docker + "create", data=json.dumps(data), headers=headers)
        #b = json.loads(r.text)
        #x = requests.post(docker + b['Id'] + "/start")

    if "chronos" in os.environ:

        # docker container header
        randomint = random.randint(1, 100000)            
        data = json.loads('{"schedule": "R0/2016-09-28T22:55:00Z/PT24H","name":"' + str(randomint) + '","cpus": "0.1","mem": "32","command": "docker run ' + image + '"}')
        print(data)

        # create and start docker container
        headers = {'Content-Type': 'application/json'}
        r = requests.post(chronos + "scheduler/iso8601", data=json.dumps(data), headers=headers)
        print (r)
        x = requests.put(chronos + 'scheduler/job/' + str(randomint))

    #else

        # remove report containers

        #queue = 4, container = 2 = no change
        #queue = 4, containers = 1 = add 1
        #queue = 10, containers = 2 = add 4