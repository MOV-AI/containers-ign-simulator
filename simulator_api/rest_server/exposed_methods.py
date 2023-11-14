"""Module required by all WebServer functions that take advantage of the WebServer core functionalities."""

import json

from flask import Blueprint, request
from WebServerCore.command_factory import CommandFactorySingleton
from WebServerCore.handler import handler_get, handler_post, handler_put
import simulator_api.utils.logger as logging

# The handler functions below expose the endpoints.
# They are necessary for the application to work, in this case, with the Flask framework.
# The logic for each function is implemented by its namesake on the factory side.

commands = Blueprint("commands", __name__)

def discovery():
    """Lazy instantiation of the commands discovery. Commands will be discovered on first call."""
    CommandFactorySingleton.discover_commands(__file__)

# Test function.
def hello():
    """Function simply to provide a responde if you call the root of the local service. Only works in local mode."""
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Sucess. Now use 'api/get-capabilities' to know the avaiable commands."
            }
        ),
    }

@commands.before_app_first_request
def flask_discovery():
    """Lazy instantiation of the commands discovery. Commands will be discovered on first call."""
    discovery()

@commands.route("/api/v<version>/<get_method>", methods=["GET"])
def get_call(version, get_method):
    """Forward the http get calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request, f"v{version}")

@commands.route("/api/<get_method>", methods=["GET"])
def get_call_no_version(get_method):
    """Forward the http get calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request)

@commands.route("/api/v<version>/<get_method>/<task_id>", methods=["GET"])
def get_status_call(version, get_method, task_id):
    """Forward the http get calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request, f"v{version}", url_specifics=task_id)

@commands.route("/api/<get_method>/<task_id>", methods=["GET"])
def get_status_call_no_version(get_method, task_id):
    """Forward the http get calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request, url_specifics=task_id)

@commands.route("/api/v<version>/<post_method>", methods=["POST"])
def post_call(version, post_method):
    """Forward the http post calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_post(post_method, request, f"v{version}")

@commands.route("/api/<post_method>", methods=["POST"])
def post_call_no_version(post_method):
    """Forward the http post calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_post(post_method, request)

@commands.route("/api/v<version>/<put_method>", methods=["PUT"])
def put_call(version, put_method):
    """Forward the http put calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_put(put_method, request, f"v{version}")

@commands.route("/api/<put_method>", methods=["PUT"])
def put_call_no_version(put_method):
    """Forward the http put calls to the WebServer core handler to take advantage of the framework functionalities"""
    return handler_put(put_method, request)

# Test function.
@commands.route("/")
def flask_hello():
    """Function simply to provide a responde if you call the root of the local service. Only works in local mode."""
    return hello()