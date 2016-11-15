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
docker_image = os.environ['image']
docker_service = os.environ['docker_service']
queue_length = os.environ['queuelength']

if "docker" in os.environ:
    docker = os.environ['docker']

if "chronos" in os.environ:
    chronos = os.environ['chronos']

while True:

    # Set up azure queue / get count of messages on queue (count).
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    metadata = queue_service.get_queue_metadata(azurequeue)
    count = metadata.approximate_message_count
            
    if "docker" in os.environ:

        # Get Docker service from Docker API.
        headers = {'Content-Type': 'application/json'}
        services = json.loads((requests.get(docker + "/services")).text)

        for service in services:
      
            if service['Spec']['Name'] == docker_service:
                service_version = service['Version']['Index']
                replica_count = service['Spec']['Mode']['Replicated']['Replicas']
                service_id = service['ID']
             
                # Determine how many workers are required
                needed_workers = math.ceil(count/int(queue_length))  
                start_workers_count = math.ceil(needed_workers - replica_count)

                print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: " + str(replica_count) + " --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(start_workers_count))

                # Scale Docker service to meet queue / worker ratio.
                jstring = json.loads('{"Name":"' + docker_service + '","TaskTemplate":{"ContainerSpec":{"Image":"' + docker_image +'"}},"Mode":{"Replicated": {"Replicas":' + str(needed_workers) + '}}}')
                post = requests.post(docker + "services/" + service_id + "/update?version=" + str(service_version), data=json.dumps(jstring), headers=headers)