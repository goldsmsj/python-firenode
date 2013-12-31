import firenode

#Start the node.js server and connect
firenode.create()

#Create firebase refs
FBURL = 'https://python-firenode-test.firebaseIO.com/demo'
input_ref = Firebase(FBURL + '/input');

def uppercase(snapshot):
    output_string = snapshot.val().upper()
    snapshot.ref().parent().child('output').set(output_string)
    
input_ref.on('value', uppercase)

while True:
    pass
