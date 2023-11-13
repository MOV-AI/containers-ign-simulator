from flask import Flask
from simulator_api.rest_server.exposed_methods import commands

app = Flask(__name__)
app.register_blueprint(commands)

if __name__ == '__main__':

    app.run()