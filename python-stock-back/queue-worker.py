from azure.storage.queue import QueueService
import json
import math
import os
import random
import requests
import time

## CURENT NOTES - Things are not efficient, workers are stopping before queue cleared, which starts up more, etc. etc. Process works but not well.

# Grab environment variables.
azurestoracct = os.environ['azurestoracct']
azurequeue = os.environ['azurequeue']
azurequeuekey = os.environ['azurequeuekey'] + "==;"
image = os.environ['image']
queue_length = os.environ['queuelength']

if "docker" in os.environ:
    docker = os.environ['docker']

if "chronos" in os.environ:
    chronos = os.environ['chronos']

while True:

    print("Top")
    time.sleep(1)

    # Set up azure queue / get count of messages on queue (count).
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    metadata = queue_service.get_queue_metadata(azurequeue)
    count = metadata.approximate_message_count
            
    if "docker" in os.environ:

        # Get containers from Docker API.
        headers = {'Content-Type': 'application/json'}
        containers = json.loads((requests.get(docker + "json?all=1&before=8dfafdbc3a40&size=1")).text)

        # Initialize count ticker
        containers_count = 0

        # Determine how many containers match worker / set number for loop.
        for container in containers:
            if container['Image'] == image:
                containers_count += 1

        # Determine how many workers are required
        needed_workers = math.ceil(count/int(queue_length))  
        start_workers_count = math.ceil(needed_workers - containers_count)

        print("Items on Queue: " + str(count) + " --- Current Workers: " + str(containers_count) + " --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(start_workers_count))

        #### STUCK RIGHT HERE - OPERATOR IS NOT WORKING
        # Start additional workers if needed
        if start_workers_count >= needed_workers and start_workers_count > 0:

            print("Need to Deploy Workers")

            # Loop through worker deployment.
            #while start_workers_count >= needed_workers:
            while needed_workers >= start_workers_count and needed_workers > 0:

                i = needed_workers
                needed_workers = 0
                while i > 0:

                    print("Starting worker container")

                    # Start container .via Docker REST API.
                    headers = {'Content-Type': 'application/json'}
                    data = json.loads('{"Image": "' + image + '"}')
                    docker_start_response = json.loads(requests.post(docker + "create", data=json.dumps(data), headers=headers).text)
                    requests.post(docker + docker_start_response['Id'] + "/start")

                    # Decrement loop counter
                    i -= 1
                    print(i)

        else: 
            if start_workers_count <= needed_workers and start_workers_count < 0:

                print("Need to Remove Workers")

                # Stop and remove workers
                while start_workers_count < needed_workers:

                    headers = {'Content-Type': 'application/json'}
                    docker_get_response = json.loads(requests.get(docker + "json?all=1&before=8dfafdbc3a40&size=1").text)

                    for container in docker_get_response:                        
                        
                        if container['Image'] == image:

                            print("Removing contianer: " + container['Image'])
                            
                            id = container['Id'] 
                            headers = {'Content-Type': 'application/json'}
                            requests.post(docker + id + "/stop", headers=headers)
                            requests.delete(docker + id, headers=headers)      

                            # Increment loop counter
                            start_workers_count += 1

