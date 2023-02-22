import os
import threading
import time

import redis
from flask import Flask, render_template
from flask_sse import sse
from gunicorn.app.base import Application, BaseApplication

app = Flask(__name__)

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')

app.config["REDIS_URL"] = f"redis://{redis_host}:{redis_port}"
app.register_blueprint(sse, url_prefix='/stream')


def start_listening():
    try:
        print('Start listening')
        rd = redis.StrictRedis(redis_host, redis_port, charset="utf-8", decode_responses=True)
        sub = rd.pubsub()
        sub.subscribe('mq1')
        for message in sub.listen():
            print(message)
            if message.get('type') == 'message':
                send_message(message.get('data'))
    except Exception as e:
        print(e)
        time.sleep(1)
        start_listening()


def send_message(message):
    with app.app_context():
        print('sending message', message)
        sse.publish({"message": message}, type='publish', channel='cust-1')
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
        'bind': '127.0.0.1:5000',
        'worker_class': 'gevent'
    }

    t1 = threading.Thread(target=start_listening)
    t1.start()

    StandaloneApplication(app, options).run()
