python-firenode
===============

Firebase client for python that leverages official node.js firebase library

##### Usage:

See demo.py for a simple example of the most common use case.

Or to start the daemon manually:
    
    firenode.py start

To stop a firenode daemon:
    
    firenode.py stop <port>

##### Dependencies:

Requires node.js and flask.

##### Notes:

Callbacks should not modify any external context (or even access it at this point) because
they are going to be called from a worker in a seperate process. 

##### Motivation:

Firebase is awesome because it allows clients to access and modify data in 
the database directly without a server shoved in the middle just to move data
around.  But many applications still need a server to do some some processing
of data.

A great way to handle this is to let the server act like just another
client.  It can watch a firebase reference where a client will place some data
that need processing, and then put the resulting data in a firebase location
that the client is watching.

Firebase also comes with an officially supported node.js library that supports
doing just that.  The idea of this project is to leverage that library to give
the same functionality to any python code either running as a script or within 
an existing web app.

#### Implementation notes

The firenode daemon is started by calling firenode.create() or running firenode.py
with start as the first argument.  This will create a node.js server and a flask 
server in seperate processes and a pool of worker processes to run callbacks.

Callback functions are marshalled and sent to the node.js where they are wrapped
in a javascript function.  When the javscript callback is fired, this sends the
marshalled function and data snapshot(s) to the flask server.

The callbacks are then placed on a Queue and pulled off by the workers where the
marshalled function is turned back into a proper python function and the snapshot
data is used to create a DataSnapshot object.  Finally the callback is executed.


##### TODO:

- Callbacks don't have access to the defining context (add @firenode_callback decorator)
- Flesh out the entire API
- Tests don't work right now
- Trying to start the daemon once its already started should work gracefully
- Add a function to stop the daemon programatically
- Authenticate attempt to stop daemon (generate a random key)
- Add comprehensive tests






