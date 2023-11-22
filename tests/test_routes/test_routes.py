import unittest
from simulator_api.entrypoint import app
from simulator_api.rest_server.exposed_methods import request
from unittest import mock


@mock.patch('simulator_api.rest_server.exposed_methods.handler_get')
@mock.patch('simulator_api.rest_server.exposed_methods.handler_post')
@mock.patch('simulator_api.rest_server.exposed_methods.handler_put')
@mock.patch('simulator_api.rest_server.exposed_methods.hello')
class TestRoutes(unittest.TestCase):
    def test_route_hello(self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get):

        with app.test_client() as client:
            client.get('/')
            mock_hello.assert_called_once()

    def test_route_get_call(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.get('/api/v1/dummy-command')
            expected_args = ('dummy-command', request, 'v1')
            mock_handler_get.assert_called_once_with(*expected_args)

    def test_route_get_call_no_version(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.get('/api/dummy-command')
            expected_args = ('dummy-command', request)
            mock_handler_get.assert_called_once_with(*expected_args)

    def test_route_get_status_call(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.get('/api/v1/dummy-command/1')
            expected_args = ('dummy-command', request, 'v1')
            mock_handler_get.assert_called_once_with(*expected_args, url_specifics='1')

    def test_route_get_status_call_no_version(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.get('/api/dummy-command/1')
            expected_args = ('dummy-command', request)
            mock_handler_get.assert_called_once_with(*expected_args, url_specifics='1')

    def test_route_post_call(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.post('/api/v1/dummy-command')
            expected_args = ('dummy-command', request, 'v1')
            mock_handler_post.assert_called_once_with(*expected_args)

    def test_route_post_call_no_version(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.post('/api/dummy-command')
            expected_args = ('dummy-command', request)
            mock_handler_post.assert_called_once_with(*expected_args)

    def test_route_put_call(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.put('/api/v1/dummy-command')
            expected_args = ('dummy-command', request, 'v1')
            mock_handler_put.assert_called_once_with(*expected_args)

    def test_route_put_call_no_version(
        self, mock_hello, mock_handler_put, mock_handler_post, mock_handler_get
    ):

        with app.test_client() as client:
            client.put('/api/dummy-command')
            expected_args = ('dummy-command', request)
            mock_handler_put.assert_called_once_with(*expected_args)
