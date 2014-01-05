import firenode

#Start the firenode service if it hasn't been started already
firenode.start()

#Create firebase refs
FBURL = 'https://python-firenode-test.firebaseIO.com/demo'
input_ref = firenode.Firebase(FBURL + '/input');

def uppercase(snapshot):
    output_string = snapshot.val().upper()
    snapshot.ref().parent().child('output').set(output_string)
    print 'Uppercase: %s' % output_string
    
input_ref.on('value', uppercase)

