import subprocess, unittest, json, time
from multiprocessing import Process
from request_utils import send_request

SERVER_URL = "http://0.0.0.0:5000"

def do_start_server():
    subprocess.call(["foreman", "start"])

def start_server():
    p = Process(target=do_start_server)
    p.daemon = False
    p.start()
    time.sleep(3)

def do_stop_server():
    subprocess.call(["fuser", "-k", "5000/tcp"])

def stop_server():
    p = Process(target=do_stop_server)
    p.daemon = False
    p.start()
    time.sleep(1)

def prepare_and_send_request(method, endpoint, client):
    headers = {
        "Accept": "application/json"
    }
    response = send_request(method, SERVER_URL + endpoint,
        headers=headers, client=client)
    return response

def perform_basic_assertions(self, response):
    self.assertTrue(response['success'])
    self.assertEqual(response['code'], 200)
    return json.loads(response['content'])

class TestServerEndpoints(unittest.TestCase):

    def test_001_get_presence_unauthenticated(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you must send presence")
        self.assertEqual(response['code'], "error")

    def test_002_authenticate(self):
        response = prepare_and_send_request('POST', '/presence/username',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "presence sent (just authenticated)")
        self.assertEqual(response['code'], "ok")

    def test_003_get_presence_authenticated(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you are username")
        self.assertEqual(response['code'], "ok")

    def test_004_authenticate_again(self):
        response = prepare_and_send_request('POST', '/presence/username',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "presence sent (already authenticated)")
        self.assertEqual(response['code'], "ok")

    def test_005_get_presence_authenticated_again(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you are username")
        self.assertEqual(response['code'], "ok")

    def test_006_authenticate_as_someone_else(self):
        response = prepare_and_send_request('POST', '/presence/another_user',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "presence fail (you are someone else)")
        self.assertEqual(response['code'], "error")

    def test_007_logout(self):
        response = prepare_and_send_request('POST', '/leave',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "username just left")
        self.assertEqual(response['code'], "ok")

    def test_008_get_presence_after_logout(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you must send presence")
        self.assertEqual(response['code'], "error")

    def test_009_logout_after_logout(self):
        response = prepare_and_send_request('POST', '/leave',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you are unauthorized")
        self.assertEqual(response['code'], "error")

    def test_010_get_presence_after_failed_logout(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you must send presence")
        self.assertEqual(response['code'], "error")

    def test_011_authenticate_again_after_logout(self):
        response = prepare_and_send_request('POST', '/presence/username',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "presence sent (just authenticated)")
        self.assertEqual(response['code'], "ok")

    def test_012_get_presence_authenticated_once_again(self):
        response = prepare_and_send_request('GET', '/presence',
            client='username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "you are username")
        self.assertEqual(response['code'], "ok")

    def test_013_someone_else_authenticates_as_me(self):
        response = prepare_and_send_request('POST', '/presence/username',
            client='another_username')
        response = perform_basic_assertions(self, response)
        self.assertEqual(response['server'],
            "presence fail (this username is taken)")
        self.assertEqual(response['code'], "error")

    @classmethod
    def tearDownClass(cls):
        stop_server()

if __name__ == "__main__": 

    start_server()
    unittest.main(failfast=True)
