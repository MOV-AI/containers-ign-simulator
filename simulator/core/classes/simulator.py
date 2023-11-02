import aiohttp.web
import aiohttp
import os

class Simulator:
    def __init__(self):

        # create a web application
        self.app = aiohttp.web.Application()

        # add a route to the application to respond to GET requests
        # map the /health URL to the handle function
        self.app.router.add_get('/health', self.handle)

    async def handle(self, request):
        # Run smoke tests 

        # make sure the query is a get with no params
        if request.method != "GET" or len(request.query.keys()) > 0:
            return aiohttp.web.Response(status=405)
        
        ok_code = 200
        nok_code = 502

        # send back the status
        # params = global_status
        # self._logger.info(f"Status GET:\n{params}")

        # queue_size = -1
        # if self._queue is not None:
        #     queue_size = self._queue.qsize()

        # if params["status"] == "running":
        #     if global_status["health"]["manager"] is not None:
        #         global_status["health"]["manager"]["queue_size"] = queue_size

        # return aiohttp.web.json_response(params) 

        return aiohttp.web.json_response(ok_code) 
        # return aiohttp.web.Response(status=ok_code)       

    def run(self):
        
        aiohttp.web.run_app(self.app, host='0.0.0.0', port=8081)

if __name__ == '__main__':

    simulator = Simulator()

    simulator.run()
