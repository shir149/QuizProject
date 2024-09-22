var timerId = null;
function startTimer(duration) {
    var countdown = duration;
    if (timerId != null) {
        clearInterval(timerId);
        timerId = null;
    }
    timerId = setInterval(function () {
        countdown--;
        //console.log(`Countdown: ${countdown}`);

    var data = {
            "type": "countdown",
            "value": countdown
        };
    socket.send(JSON.stringify(data));

        if (countdown <= 0) {
            clearInterval(timerId);
            timerId = null;
        }
    }, 1000);
}
function stopTimer() {
    clearInterval(timerId);
    timerId = null;
}