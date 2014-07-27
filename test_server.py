import subprocess, unittest, json, time
from multiprocessing import Process
from request_utils import send_request

def start_server():
    subprocess.call(["python", "server.py"])

def stop_server():
    subprocess.call(["sudo", "fuser", "-k", "5000/tcp"])

class TestServerEndpoints(unittest.TestCase):

    def setUp(self):
        p = Process(target=start_server)
        p.daemon = False
        p.start()
        time.sleep(1)

    def test_get_presence_unauthenticated(self):
        headers = {
            "Accept": "application/json"
        }
        response = send_request('GET',
            "http://0.0.0.0:5000/presence", headers=headers)
        self.assertTrue(response['success'])
        self.assertEqual(response['code'], 200)
        response = json.loads(response['content'])
        self.assertEqual(response['server'], "you must send presence")
        self.assertEqual(response['code'], "error")

    def tearDown(self):
        p = Process(target=stop_server)
        p.daemon = False
        p.start()
        time.sleep(1)

if __name__ == "__main__": 

    unittest.main()
