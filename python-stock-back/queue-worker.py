from azure.storage.queue import QueueService
import json
import math
import os
import random
import requests
import time

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
    #time.sleep(5)

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

        # Start additional workers if needed
        if start_workers_count >= needed_workers and start_workers_count > 0:

            print("Need to Deploy Workers")

            # Loop through worker deployment.
            while needed_workers >= start_workers_count and needed_workers > 0:

                while needed_workers > 0:

                    print("Starting worker container")

                    # Start container .via Docker REST API.
                    headers = {'Content-Type': 'application/json'}
                    data = json.loads('{"Image": "' + image + '"}')
                    docker_start_response = json.loads(requests.post(docker + "create", data=json.dumps(data), headers=headers).text)
                    requests.post(docker + docker_start_response['Id'] + "/start")

                    # Decrement loop counter
                    needed_workers -= 1

        else:
            # Remove workers if needed. 
            if start_workers_count <= needed_workers and start_workers_count < 0:

                # Get containers
                headers = {'Content-Type': 'application/json'}
                docker_get_response = json.loads(requests.get(docker + "json?all=1&before=8dfafdbc3a40&size=1").text)

                # Set flag for list selection - this will remove 0,1,2...
                container_list_position = 0

                # Loop through count of workers to stop (negative number / remove).
                while start_workers_count <= -1:
                   
                    # Verify that container is a worker.
                    if docker_get_response[container_list_position]['Image'] == image:

                        # Remove container.
                        id = docker_get_response[container_list_position]['Id']
                        print("Removing container: " + id)
                        headers = {'Content-Type': 'application/json'}
                        requests.post(docker + id + "/stop", headers=headers)
                        requests.delete(docker + id, headers=headers)

                    # Increment list position so that next in list is removed.
                    container_list_position += 1
                    # Increment count of workers so that loop is stopped at specific position.
                    start_workers_count += 1