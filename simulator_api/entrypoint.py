import ssl as ssl_lib
import threading
import certifi
from flask import Flask
# from celery import Celery
import simulator_api.utils.logger as logging

from simulator_api.rest_server.exposed_methods import commands
from simulator_api.async_tasks.async_tasks import celery

def run_flask(app):
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=8081)

def run_celery():
    celery.worker_main(['worker'])

def run():
    # starts logging

    # preps to run on Flask
    app = Flask(__name__)

    # and registers a view to respond to requests, in this case, our commands
    app.register_blueprint(commands)

    # Start Flask in one thread
    flask_thread = threading.Thread(target=run_flask, args=(app,))
    flask_thread.start()

    # Start Celery in another thread
    celery_thread = threading.Thread(target=run_celery)
    celery_thread.start()

    # Wait for both threads to finish (if needed)
    flask_thread.join()
    celery_thread.join()

if __name__ == '__main__':
    run()