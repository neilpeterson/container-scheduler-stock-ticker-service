from azure.storage.queue import QueueService

azurestoracct = "twoqueue"
azurequeue = "myqueue"
azurequeuekey = "vCUrUB+0H0MAI/uozyqJ1NW0MFlIsCs31BJihIwIIxCEb7CXHR2luRb2fopNMPmvWFDrNZpqxCW5uKdJQjxVtA==;"

while True:

# set up azure queue
    queue_service = QueueService(account_name=azurestoracct, account_key=azurequeuekey)

    metadata = queue_service.get_queue_metadata(azurequeue)
    count = metadata.approximate_message_count
    print(count)

    # get messages from azure queue
    #messages = queue_service.get_messages(azurequeue, num_messages=5)

    #if messages:
    #    print(messages.count.text)