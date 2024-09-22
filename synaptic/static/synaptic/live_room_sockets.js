loc = window.location

var wsStart = 'ws://'
if (loc.protocol == 'https:') {
    wsStart = 'wss://'
}
var endpoint = wsStart + loc.host + loc.pathname;
console.log("endpoint: ", wsStart, loc.host, loc.pathname);
var socket = new ReconnectingWebSocket(endpoint);

// const chatSocket = new WebSocket(
//     'ws://'
//     + window.location.host
//     + '/ws/synaptic/'
//     + roomName
//     + '/'

socket.onmessage = function (e) {
    //console.log("message", e)
    render_content(e)
}

socket.onopen = function (e) {
    //console.log("open", e)
}