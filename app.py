from flask import Flask, render_template
from flask_sse import sse
from flask import render_template
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new():
    sse.publish({"message": datetime.datetime.now()}, type='publish', channel='a-1')
    sse.publish({"message": datetime.datetime.now()}, type='publish', channel='a-2')
    return 'Published'
