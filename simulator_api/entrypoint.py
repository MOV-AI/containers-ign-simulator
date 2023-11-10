import ssl as ssl_lib
import threading
import certifi
import sys
from flask import Flask

from simulator_api.rest_server.exposed_methods import commands
from simulator_api.celery_tasks.celery_tasks import celery

def run_celery():
    celery.worker_main(['worker','--loglevel','info'])

def run():

    # starts logging

    # preps to run on Flask
    app = Flask(__name__)

    # and registers a view to respond to requests, in this case, our commands
    app.register_blueprint(commands)

    # Start Celery in another thread
    celery_thread = threading.Thread(target=run_celery)
    celery_thread.start()

    # Start Flask
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=8081)

    # Wait for both threads to finish (if needed)
    celery_thread.join()

    sys.exit(0)

if __name__ == '__main__':
    run()