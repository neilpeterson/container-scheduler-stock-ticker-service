import json
import math
import os
import requests
from azure.storage.queue import QueueService

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
        if (requests.get(docker + "/services/" + docker_service)): # How to combine this request with the one below?

            service = json.loads((requests.get(docker + "/services/" + docker_service)).text)
            service_version = service['Version']['Index']
            replica_count = service['Spec']['Mode']['Replicated']['Replicas']
            service_id = service['ID']

            # Determine how many workers are required
            needed_workers = math.ceil(count/int(queue_length))
            start_workers_count = math.ceil(needed_workers - replica_count)

            # Output
            print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: " + str(replica_count) + " --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(start_workers_count))

            # Scale Docker service to meet queue / worker ratio.
            jstring = json.loads('{"Name":"' + docker_service + '","TaskTemplate":{"ContainerSpec":{"Image":"' + docker_image +'"}},"Mode":{"Replicated": {"Replicas":' + str(needed_workers) + '}}}')
            post = requests.post(docker + "services/" + service_id + "/update?version=" + str(service_version), data=json.dumps(jstring), headers=headers)

        else: 

            # Determine how many workers are required
            needed_workers = math.ceil(count/int(queue_length))  
            
            # Output
            print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: No Service --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(needed_workers))

            # Service does not exsist, create it
            jstring = json.loads('{"Name":"' + docker_service + '","TaskTemplate":{"ContainerSpec":{"Image":"' + docker_image +'"}},"Mode":{"Replicated": {"Replicas":' + str(needed_workers) + '}}}')
            post = requests.post(docker + "services/create", data=json.dumps(jstring), headers=headers)

    if "marathon" in os.environ:

        print("marathon")
        
        # Get marathon Task
        if (requests.get(marathon + docker_service)): # How to combine this request with the one below?

            # Get app information
            service = json.loads((requests.get(marathon + docker_service)).text)
            replica_count = service['app']['instances']

            # Determine how many workers are required
            needed_workers = math.ceil(count/int(queue_length))  
            start_workers_count = math.ceil(needed_workers - replica_count)

            # Output
            print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: " + str(replica_count) + " --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(start_workers_count))

            # Scale app to meet queue / worker ratio - getting response 409 when needed = 0, may want to check for 0 and remove app.
            headers = {'Content-Type': 'application/json'}
            jstring = json.loads('{"id": "/stock-report","cmd": null,"cpus": 0.1,"mem": 32,"disk": 0,"instances":' + str(needed_workers) + ',"container": {"type": "DOCKER","volumes": [],"docker": {"image": "neilpeterson/stock-report-service","network": "BRIDGE","privileged": false,"parameters": [],"forcePullImage": false}}}')
            post = requests.put(marathon + docker_service, data=json.dumps(jstring), headers=headers)
            print (post)


        else:

            print("No")

            # Determine how many workers are required
            needed_workers = math.ceil(count/int(queue_length))  
            
            print("Items on Queue: " + str(count) + " --- Queue/Worker Ratio: " + queue_length +  " --- Current Workers: No Service --- Needed Workers: " + str(needed_workers) + " --- To Start: " + str(needed_workers))





