import logging
import os

from simulator.core.classes.simulator import Simulator

def run():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)

    # disable requests and urllib3 warnings
    logging.getLogger("requests").setLevel(level=log_level)
    logging.getLogger("urllib3").setLevel(level=log_level)
    logging.getLogger("aiohttp").setLevel(level=log_level)

    simulator = Simulator()
    try:
        exit(simulator.run())
    except Exception as e:
        logging.log(logging.CRITICAL, "Error: " + str(e))
        exit(1)

if __name__ == '__main__':
    run()