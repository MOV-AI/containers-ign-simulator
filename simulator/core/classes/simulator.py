import os
import aiohttp
import subprocess
import aiohttp.web
from simulator.core.utils import StdoutLogger

class Simulator:
    def __init__(self):
        self._logger = StdoutLogger("simulator.mov.ai")
        self._logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        self._logger.info("initializing simulator instance")

        # create a web application
        self.app = aiohttp.web.Application(logger=self._logger, debug=False)

        # add a route to the application to respond to GET requests
        # map the /health URL to the handle function
        self.app.router.add_get('/health', self.handle)

    async def handle(self, request: aiohttp.web.Request):
        """Handles GET requests inside the container.

        Args:
            request: GET request.

        """

        # make sure the query is a get with no params
        if request.method != "GET" or len(request.query.keys()) > 0:
            return aiohttp.web.Response(status=405)
        
        # Run communication smoke tests
        # Test that Ignition is running (/clock, /stats)
        # Test that the world is loaded correctly (/world/empty/clock, /world/empty/stats)
        # Test spawner to sim communication through topic /test
        for topic in ["/clock","/stats","/world/empty/clock","/world/empty/stats","/test"]:
            exitcode = self.ign_topic_is_published(topic)
            if exitcode == 124:
                self._logger.info(f"The topic '{topic}' is not published")
                return aiohttp.web.Response(text=f"The topic {topic} is not published\n", content_type='text/plain')
            if exitcode != 0: 
                return aiohttp.web.Response(status=exitcode) 

        return aiohttp.web.Response(status=200)  

    def ign_topic_is_published(self, topic: str):
        """Check that a given ign topic is being published inside the container.

        Args:
            topic: Topic string.

        """

        try:
            cmd = f"ign topic -e -n 1 -t {topic}"
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, timeout=1)
            output = result.stdout
            self._logger.info(f"Result of echoing topic {topic}: {output}")
        except subprocess.TimeoutExpired as e:
            self._logger.info(f"The command '{cmd}' timed out")
            return 124
        except subprocess.CalledProcessError as e:
            self._logger.info(f"The command '{cmd}' returned a non-zero exit status")
            return e.returncode

        return result.returncode

    def run(self):
        """Run the simulator web server."""

        self._logger.info("starting http server locally")
        
        aiohttp.web.run_app(self.app, host='0.0.0.0', port=8081)

if __name__ == '__main__':

    simulator = Simulator()

    simulator.run()
