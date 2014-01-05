var http = require('http');
var url = require('url');
var request = require('request');
var Firebase = require('firebase');


var flaskPort = Number(process.argv[2]);
var nodePort = Number(process.argv[3]);
var host = process.argv[4];

var node_url = 'http://' + host + ':' + nodePort.toString();
var firebaseRefs = {};


var createSnapshot = function(snapshot) {
    var json_snapshot = {'val': snapshot.val(), 'url': snapshot.ref().toString(), 'node_url': node_url};
    return JSON.stringify(json_snapshot);
};

var createCallback = function(callback) {
    return function(snapshot) {
        request({
            uri: 'http://' + host + ':' + flaskPort.toString() + '/fire_callback',
            method: "GET",
            qs: {
                callback: callback,
                snapshot: createSnapshot(snapshot)
            }},
            function(error, response, body) {});
    };
};

http.createServer(function (req, response) {
    var params = url.parse(req.url, true).query;
    console.log(params);
    
    var responseText = '';
    
    switch (params.func) {
        case 'new':
            if (!(params.url in firebaseRefs)) {
                firebaseRefs[params.url] = new Firebase(params.url);
            }
            break;
            
        case 'on':
            firebaseRefs[params.url].on(params.event_type, createCallback(params.callback));
            break;
            
        case 'set':
            firebaseRefs[params.url].set(params.value);
            break;
            
        case 'parent':
            var parentRef = firebaseRefs[params.url].parent();
            responseText = parentRef.toString();
            break;
        
        case 'child':
            var childRef = firebaseRefs[params.url].child(params.child_path);
            responseText = childRef.toString();
            break;
    }
    
    response.writeHead(200, {
        'Content-Type': 'text/plain'
    });
    response.end(responseText, 'ascii');
}).listen(nodePort, host);
    
console.log('Firebase - node.js server running at ' + node_url);
