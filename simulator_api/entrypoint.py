from flask import Flask
from simulator_api.rest_server.exposed_methods import commands

app = Flask(__name__)
app.register_blueprint(commands)
# TODO: fix CSRF security issue
# from flask_wtf.csrf import CSRFProtect
# app.config.update(SECRET_KEY="hello")
# csrf = CSRFProtect()
# csrf.init_app(app)  # Compliant

if __name__ == '__main__':
    app.run(port=8081)
