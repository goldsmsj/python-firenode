''' 
    Tests for firenode

    Usage:  py.test -v test_flask.py

    Dependencies:
        python: pytest, flask, requests
        node.js: url, http, request, firebase
    
    Notes:
        An attempt is made to reduce dependencies on other firebase projects or 
    other functions/methods within firenode. So all tests try to read and write
    data using a plain old request using python's requests module.  
    
'''


import json
import time
import requests
import multiprocessing
import pytest

from firenode import Firebase, create
from flask import Flask, request

       
def setup_module(module):
    '''
    Does all one time setup for the tests.  This includes creating the node and 
    flask servers and defining routes for the flask app.
    
    '''
    
    global firebase_url
    global data
    global flask_port, node_port, host
    global flask_process, node_process

    
    #In order to run tests you must create your own Firebase
    #BEWARE!!! - Tests will overwrite all data at this Firebase!
    firebase_url = 'https://python-firenode-test2.firebaseIO.com/'
    
    flask_port = 17501
    node_port = 17502
    host = '127.0.0.1'

    #Load test data from test.json
    with open('test.json') as stream:
        json_data_as_string = stream.read()
    data = json.loads(json_data_as_string) 
    
    #Load test data into our test firebase
    requests.put(firebase_url + '.json', data=json.dumps(data))

    #Create the flask app
    app = Flask(__name__)

    
    #Callback routes for tests
    @app.route('/uppercase')
    def uppercase():
        input_string = request.args['val']
        output_string = input_string.upper()
        
        #Set works like normal
        output_ref.set(output_string)
        
        return ''
 
    #Start the node.js server in a seperate process
    node_process = create(flask_port=flask_port, node_port=node_port, host=host)   
    
    #Start the flask server in a seperate process
    def start_flask_server():
        app.run(port=flask_port, host=host, debug=True, use_reloader=False)
    flask_process = multiprocessing.Process(target=start_flask_server)
    flask_process.start()
    
    #Wait until the flask app is running before running tests 
    flask_url = 'http://' + host + ':' + str(flask_port)
    while True:
        time.sleep(0.1)
        try:
            requests.get(flask_url)
            break
        except requests.exceptions.ConnectionError:
            pass
 
def teardown_module(module):
    ''' Terminate server processes after tests are done'''
    flask_process.terminate()
    node_process.kill()


###############################
#Tests

def test_setup_loaded_test_data_properly():
    r = requests.get(firebase_url + '.json')
    assert(json.dumps(data) == r.text)

def test_create_root_ref():
    ''' Just tests that creating a ref doesn't throw any exceptions '''
    root_ref = Firebase(firebase_url)
    
def test_set_string():
    test_set_string_url = firebase_url + 'test_set_string'
    test_string = 'a_test_string_at_test_set_string'
    
    ref = Firebase(test_set_string_url)
    ref.set(test_string)
    time.sleep(2.0)
    r = requests.get(test_set_string_url + '.json')
    
    assert(r.text == '"' + test_string + '"')
 
#def test_on_string(firenode_test_fixture):
#    ref = Firebase(firebase_url + '/)
#    input_ref.on('value', '/uppercase')
    

