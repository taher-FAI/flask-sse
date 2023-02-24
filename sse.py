import json
import os
import threading
import time

from flask import Flask, render_template, request, current_app, stream_with_context
from flask_sse import ServerSentEventsBlueprint
from gunicorn.app.base import Application, BaseApplication
import pika

app = Flask(__name__)

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')

app.config["REDIS_URL"] = f"redis://{redis_host}:{redis_port}"


class CustomBlueprint(ServerSentEventsBlueprint):
    def stream(self):
        channel = request.args.get('channel') or 'sse'

        @stream_with_context
        def generator():
            for message in self.messages(channel=channel):
                yield str(message)

        return current_app.response_class(
            generator(),
            mimetype='text/event-stream',
            headers={'Access-Control-Allow-Origin': '*'}
        )


sse = CustomBlueprint('sse', __name__)
sse.add_url_rule(rule="", endpoint="stream", view_func=sse.stream)

app.register_blueprint(sse, url_prefix='/stream')


def new_message(ch, method, properties, body):
    try:
        print(" ---------[x]--------- Received %r" % body)
        message = json.loads(body)
        cust_id = message.get('cust_id')
        channel_id = f'cust-{cust_id}'
        send_message(message, channel=channel_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # TODO Deal with currupted messages
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(e)


def start_listening():
    print('Start listening to rabbitmq')
    channel = get_rabbit_connection()
    channel.queue_declare(queue=os.getenv('SSE_QUEUE'), durable=True)
    channel.basic_consume(queue=os.getenv('SSE_QUEUE'),
                          on_message_callback=new_message)
    channel.start_consuming()


def get_rabbit_connection():
    creds = pika.credentials.PlainCredentials(
        os.getenv('RABBIT_USER'), os.getenv('RABBIT_PASSWORD'))
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        os.getenv('RABBIT_HOST'), port=os.getenv('RABBIT_PORT'), credentials=creds))
    return connection.channel()


def send_message(message, channel):
    with app.app_context():
        print(f'Sending message to client {channel}', message,)
        sse.publish({"message": message}, type='publish', channel=channel)
        print('Sent')


@app.route('/')
def index():
    return render_template('index.html')


class StandaloneApplication(Application):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '0.0.0.0:5000',
        'worker_class': 'gevent'
    }

    t1 = threading.Thread(target=start_listening)
    t1.start()

    StandaloneApplication(app, options).run()
    # app.run(port=5001)
