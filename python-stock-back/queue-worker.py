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
docker_image = os.environ['docker_image']
docker_service = os.environ['docker_service']
queue_length = os.environ['queuelength']

if "docker" in os.environ:
    docker = os.environ['docker']

if "marathon" in os.environ:
    marathon = os.environ['marathon']

while True:

    # Set up azure queue / get count of messages on queue (count).
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)
    metadata = queue_service.get_queue_metadata(azurequeue)
    count = metadata.approximate_message_count
            
    if "docker" in os.environ:

        print("Docker")

        # Get Docker service from Docker API - check for service (docker_service)
        headers = {'Content-Type': 'application/json'}
        if (requests.get(docker + "/services/" + docker_service)):

            service = json.loads((requests.get(docker + "/services/" + docker_service)).text)
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

        else: 

            # Determine how many workers are required
            needed_workers = math.ceil(count/int(queue_length))  
            
            print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: No Service --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(needed_workers))

            # Service does not exsist, create it
            jstring = json.loads('{"Name":"' + docker_service + '","TaskTemplate":{"ContainerSpec":{"Image":"' + docker_image +'"}},"Mode":{"Replicated": {"Replicas":' + str(needed_workers) + '}}}')
            post = requests.post(docker + "services/create", data=json.dumps(jstring), headers=headers)

    if "marathon" in os.environ:

        print("Marathon")

        # Get marathon Task

        headers = {'Content-Type': 'application/json'}
        apps = json.loads((requests.get('http://172.16.0.5/marathon/v2/apps')).text)

	### WORKING HERE        

        #print(apps)        
        print(apps['apps'][2]['container'])

        # Determine how many workers are required
        #needed_workers = math.ceil(count/int(queue_length))  
        #start_workers_count = math.ceil(needed_workers - '''<update from marathon>''')

        #print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: " + str('''<update from marathon>''') + " --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(start_workers_count))

