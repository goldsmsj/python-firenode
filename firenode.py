import subprocess
import requests
import time
import atexit


node_url = ''
node_process = None


def create(flask_port, node_port=28593):
    global node_url, node_process
    
    node_url = 'http://127.0.0.1:' + str(node_port)
    node_process = subprocess.Popen(['node', 'firebase-node.js', str(flask_port), str(node_port)])
    
    #Kill the node server when the python interpreter exits
    atexit.register(destroy)
    
    #Make sure the node.js server has actually started and we can connect
    while True:
        time.sleep(0.1)
        try:
            requests.get(node_url)
            break
        except requests.exceptions.ConnectionError:
            pass
        
def destroy():
    node_process.kill()


class Firebase(object):
    def __init__(self, url):
        self._url = url
        requests.post(node_url, params={'func': 'new', 'url': self._url})
        
    def on(self, event_type, callback_route):
        requests.post(node_url, params={'func': 'on', 'url': self._url, 'event_type': event_type, 'callback_route': callback_route})
    
    def set(self, value):
        requests.post(node_url, params={'func': 'set', 'url': self._url, 'value': value})
        