"""Module that contains a wrapper logger to ease interacting with the python logging module"""
import logging
from os import environ

logging.basicConfig(level=environ.get("PYLOGLEVEL", "INFO"))


def error(msg, *args, **kwargs):
    """Wrapping the error method from logging."""
    logging.error(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """Wrapping the warning method from logging."""
    logging.warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """Wrapping the info method from logging."""
    logging.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    """Wrapping the debug method from logging."""
    logging.debug(msg, *args, **kwargs)


def log(level, msg, *args, **kwargs):
    """Wrapping the log method from logging."""
    logging.log(level, msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    """Wrapping the exception method from logging."""
    logging.exception(msg, *args, **kwargs)
