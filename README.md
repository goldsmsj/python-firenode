python-firenode
===============

Firebase client for python frameworks

Just of a proof of concept for now.

Requires node.js

--------------------

Ok trying something new:

Using routes is a bad idea
It requires creating routes manually that have no real meaning.

Ideally I to just run a python script like this:

################
import firenode
from my_awesome_python_app_data_processing_module import data_processing_function 

firenode.create()

FBURL = 'URL for a firebase where the client will change data that requires processing'
ref = firenode.Firebase(FBURL)

def processing_callback(data_snapshot):
    new_val = data_processing_function(data_snapshot.val())
    data_snapshot.ref().parent().child('output').set(new_val)
    
ref.on('value', processing_callback)
################


so here's the new idea:
create a node.js server to listen to firebase
create a pool of python worker processes
connect the node.js server to the python worker manager through a socket
register callbacks as pickled python functions sent to node server
when a callback is fired the node server sends the pickled function back
then its dispatched to a worker process via a python queue

alternatively:
the python worker manager could cache pickled functions.
and then uid for each function could be passed back and forth between node <-> Python

at this point i'm not going to worry about this
I think practically it won't matter and it'll be simpler

an important implication of this is that the functions won't have context
i.e. don't use closures or globals or flask thread locals
they should be stateless and operate only on the datasnapshot anyway

The nice part of actually sending the pickled function to the node server
is for an app at scale I can seperate the listening into a dedicated node server
and dispatch jobs over the network using something like amazon SQS
but the workers could also cache the functions

anyway i'll worry about performace at scale later
focus on simplicity of implementation





