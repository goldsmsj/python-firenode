from flask import Flask, request

app = Flask(__name__)
flask_port = 3000


import firenode
from firenode import Firebase

#Start the node.js server and connect
firenode.create(flask_port=flask_port, node_port=5000)

#Create firebase refs
FBURL = 'https://python-firenode-test.firebaseIO.com'
input_ref = Firebase(FBURL + '/input');
output_ref = Firebase(FBURL + '/output');

#The callback is now a route instead of a function
input_ref.on('value', '/uppercase')


@app.route('/uppercase')
def uppercase():
    input_string = request.args['val']
    output_string = input_string.upper()
    
    #Set works like normal
    output_ref.set(output_string)
    
    return ''


if __name__ == "__main__":
    #Start flask
    app.run(port=flask_port, host='127.0.0.1', debug=True, use_reloader=False)
