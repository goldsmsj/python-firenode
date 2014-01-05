"""
    python-firenode daemon

    node process <--http--> flask_process -> manager process
        ^                                    (python queue)
        |                                     |  |  |  |  |
        -------------------------------------worker processes

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
import logging


from flask import Flask, request

from firenode import DataSnapshot

def _process_callbacks(q):
    while True:
        #Pull next job off the queue 
        callback_as_string, snapshot = q.get()

        #Log that a callback is begin processed
        #logging.basicConfig(filename='worker%d.log' % os.getpid(), level=logging.DEBUG)
        #logging.debug('%d processing callback - c: %s s: %s' % (os.getpid(), callback_as_string, str(snapshot)))

        #Convert callback from string representation into a function
        callback_code = marshal.loads(base64.b64decode(callback_as_string))
        callback = types.FunctionType(callback_code, {}, "callback")

        #Do the actual call
        callback(snapshot)


def _start_daemon(flask_port, node_port, host, python_workers):
    #Create worker pool
    worker_manager = multiprocessing.Manager()
    callback_queue = worker_manager.Queue()
    worker_pool = multiprocessing.Pool(processes=python_workers)

    #Flask app
    flask_app = Flask(__name__)
    
    @flask_app.route('/fire_callback')
    def fire_callback():
        #Create callback function from request
        callback = request.args['callback']
        
        #Create DataSnapshot object from request    
        json_snapshot = request.args['snapshot']
        snapshot = DataSnapshot(json.loads(json_snapshot))
    
        print 'adding to Q'
        #Add callback to the queue
        callback_queue.put((callback, snapshot))
    
        return ''

    @flask_app.route('/stop')
    def stop():
        node_process.kill()
        worker_pool.terminate()
        worker_manager.shutdown()
        return str(os.getpid())
    

    #Start node process       
    node_process = subprocess.Popen(['node', 'firebase-node.js', str(flask_port), str(node_port), host])

    #Start workers
    for i in range(python_workers):
        worker_pool.apply_async(_process_callbacks, [callback_queue])
        
    #Start flask process
    flask_app.run(port=flask_port, host=host, debug=True, use_reloader=False)


if __name__ == '__main__':
    flask_port, node_port, host, worker_count = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    _start_daemon(flask_port, node_port, host, worker_count)
