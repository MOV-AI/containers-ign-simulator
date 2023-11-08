"""Module required by all lambda functions that take advantage of the lambda core functionalities."""

import json

from flask import Blueprint, request
from LambdaCore.command_factory import CommandFactorySingleton
from LambdaCore.handler import handler_get, handler_post

# The handler functions below expose the endpoints.
# They are necessary for the application to work, in this case, with the Flask framework.
# The logic for each function is implemented by its namesake on the factory side.

commands = Blueprint("commands", __name__)


@commands.before_app_first_request
def discovery():
    """Lazy instantiation of the commands discovery. Commands will be discovered on first call."""
    CommandFactorySingleton.discover_commands(__file__)


@commands.route("/api/<version>/<get_method>", methods=["GET"])
def get_call(version, get_method):
    """Forward the http get calls to the lambda core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request, version)

@commands.route("/api/<get_method>", methods=["GET"])
def get_call_no_version(get_method):
    """Forward the http get calls to the lambda core handler to take advantage of the framework functionalities"""
    return handler_get(get_method, request)


@commands.route("/api/<version>/<post_method>", methods=["POST"])
def post_call(version, post_method):
    """Forward the http post calls to the lambda core handler to take advantage of the framework functionalities"""
    return handler_post(post_method, request, version)


# Test function.
@commands.route("/")
def hello():
    """Function simply to provide a responde if you call the root of the local service. Only works in local mode."""
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Sucess. Now use 'GetCapabilities' to know the avaiable commands."
            }
        ),
    }