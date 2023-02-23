import datetime
import time
import pika

creds = pika.credentials.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', credentials=creds))
channel = connection.channel()

# channel.exchange_declare(exchange='logs',exchange_type='fanout')
# result = channel.queue_declare(queue='', durable=True)
# channel.queue_bind(exchange='logs', queue=result.method.queue)

channel.queue_declare(queue='mq1', durable=True)

channel.basic_publish(exchange='',
                      routing_key='mq1',
                      properties=pika.BasicProperties(
                          delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                      body=str(datetime.datetime.now().timestamp()))
connection.close()
