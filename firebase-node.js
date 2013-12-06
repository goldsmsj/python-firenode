var http = require('http');
var url = require('url');
var request = require('request');
var Firebase = require('firebase');


var flaskPort = Number(process.argv[2]);
var nodePort = Number(process.argv[3]);

var firebaseRefs = {};


var createCallback = function(callback_route) {
    return function(snapshot) {
        request({
            uri: 'http://127.0.0.1:' + flaskPort.toString() + callback_route,
            method: "GET",
            qs: {
                val: snapshot.val() //Other things should go here too
            }},
            function(error, response, body) {});
    }
}

http.createServer(function (req, response) {
    params = url.parse(req.url, true).query;
    console.log(params);
    
    switch (params.func) {
        case 'new':
            if (params.url in firebaseRefs) {
                ref = firebaseRefs[params.url];
            } else {
                firebaseRefs[params.url] = new Firebase(params.url);
            }
            break;
            
        case 'on':
            firebaseRefs[params.url].on(params.event_type, createCallback(params.callback_route));
            break;
            
        case 'set':
            firebaseRefs[params.url].set(params.value);
            break;
    }
    
    response.writeHead(200, {
        'Content-Type': 'text/plain'
    });
    response.end('');
}).listen(nodePort, '127.0.0.1');
    
console.log('Firebase - node.js server running on port ' + nodePort.toString());
