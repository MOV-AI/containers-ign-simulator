import ssl as ssl_lib

import certifi
from flask import Flask

from simulator_api.rest_server.exposed_methods import commands

def run():
    # starts logging

    # preps to run on Flask
    app = Flask(__name__)

    # and registers a view to respond to requests, in this case, our commands
    app.register_blueprint(commands)

    # if explicitly started, that is not called by another module or function, begins listening for requests
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=8081)

if __name__ == '__main__':
    run()