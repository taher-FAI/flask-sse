import datetime
import json
import os
import pika

creds = pika.credentials.PlainCredentials(os.getenv('RABBIT_USER'), os.getenv('RABBIT_PASSWORD'))
connection = pika.BlockingConnection(
    pika.ConnectionParameters(os.getenv('RABBIT_HOST'), port=os.getenv('RABBIT_PORT'), credentials=creds))
channel = connection.channel()

# channel.exchange_declare(exchange='logs',exchange_type='fanout')
# result = channel.queue_declare(queue='', durable=True)
# channel.queue_bind(exchange='logs', queue=result.method.queue)

channel.queue_declare(queue=os.getenv('SSE_QUEUE'), durable=True)

message = {
    "cust_id": 101,
    "payload": {
        "case_id": 12345,
        "status": "Awaiting Validation"
    },
    "timestamp": str(datetime.datetime.now()),
    "type": "case_master_update"  
}

channel.basic_publish(exchange='',
                      routing_key=os.getenv('SSE_QUEUE'),
                      properties=pika.BasicProperties(
                          delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                      body=json.dumps(message))
connection.close()
