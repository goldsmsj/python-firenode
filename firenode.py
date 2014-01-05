#!/usr/bin/env python

"""
    python-firenode library
    Created by Steve Goldsmith
    
    
"""
    

import base64
import json
import marshal
import multiprocessing
import os
import requests
import signal
import subprocess
import sys
import time
import types
import urllib2

from flask import Flask, request


default_flask_port = 28592
default_node_port = 28593
default_host = '127.0.0.1'
default_worker_count = 5


class Firebase(object):
    node_url = None
    def __init__(self, url, node_url=None):
        self._url = url
        
        if node_url is None:
            node_url = Firebase.node_url
            
        if node_url is None:
            raise ValueError, 'firenode.start() must be called before creating any Firebase objects'
        
        self._node_url = node_url 
        
        requests.get(self._node_url, params={'func': 'new', 'url': self._url})
        
    def on(self, event_type, callback):
        pickled_callback = base64.b64encode(marshal.dumps(callback.func_code))
        requests.post(self._node_url, params={'func': 'on', 'url': self._url, 'event_type': event_type, 'callback': pickled_callback})
    
    def set(self, value):
        requests.post(self._node_url, params={'func': 'set', 'url': self._url, 'value': value})

    def parent(self):
        resp = requests.get(self._node_url, params={'func': 'parent', 'url': self._url})
        return Firebase(resp.text, self._node_url)
    
    def child(self, child_path):
        resp = requests.get(self._node_url, params={'func': 'child', 'url': self._url, 'child_path': child_path})
        return Firebase(resp.text, self._node_url)

    
class DataSnapshot(object):
    def __init__(self, snapshot):
        self._val = snapshot['val']
        self._url = snapshot['url']
        self._node_url = snapshot['node_url']
 
    def __repr__(self):
        return 'DataSnaphot - {val: ' + self._val + ', url: ' + self._url + '}' 
        
    def val(self):
        return self._val
        
    def ref(self):
        return Firebase(self._url, self._node_url)


def start(flask_port=default_flask_port, node_port=default_node_port, host=default_host, worker_count=default_worker_count):
    node_url = Firebase.node_url = 'http://' + host + ':' + str(node_port)
    flask_url = 'http://' + host + ':' + str(flask_port)

    daemon_process = _start_daemon(flask_port, node_port, host, worker_count)
    print 'Firenode Daemon started - host: %s port: %d' % (host, flask_port)

    #Block until node and flask are running
    while True:
        time.sleep(0.1)
        try:
            requests.get(node_url)
            break
        except requests.exceptions.ConnectionError:
            pass
    
    while True:
        time.sleep(0.1)
        try:
            requests.get(flask_url)
            break
        except requests.exceptions.ConnectionError:
            pass
 

def _start_daemon(flask_port, node_port, host, worker_count):
    daemon_process = subprocess.Popen(['python', 'firenode_daemon.py', str(flask_port), str(node_port), host, str(worker_count)])
    return daemon_process.pid


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if args[0] == 'start':
        if len(args) > 1:
            flask_port = int(args[1])
            node_port = int(args[2])
            host = args[3]
            worker_count = int(args[4])
        
        else:
            flask_port, node_port, host, worker_count = default_flask_port, default_node_port, default_host, default_worker_count
        
        daemon_pid = _start_daemon(flask_port, node_port, host, worker_count)
        print 'Firenode Daemon started - host: %s port: %d' % (host, flask_port)

    elif args[0] == 'stop':
        if len(args) < 2:
            print 'stop requires port as argument'
        else:
            port = args[1]
            if len(args) < 3:
                host = '127.0.0.1'
            else:
                host = args[2]
            resp = requests.get('http://%s:%s/stop' % (host, port))
            flask_pid = int(resp.text)
            os.kill(flask_pid, signal.SIGTERM)
      
    else:
        print 'First argument must be start or stop'
