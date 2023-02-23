import pika

creds = pika.credentials.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', credentials=creds))
channel = connection.channel()
channel.queue_declare(queue='mq1', durable=True)

# channel.exchange_declare(exchange='logs',
#                          exchange_type='fanout')

# result = channel.queue_declare(queue='', exclusive=True)
# queue_name = result.method.queue
# channel.queue_bind(exchange='logs', queue=result.method.queue)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(queue='mq1',
                      on_message_callback=callback)

channel.start_consuming()