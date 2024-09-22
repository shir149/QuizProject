window.addEventListener("resize", equaliseButtons);

function render_content(e) {
    var msg = JSON.parse(e.data);
    //console.log("decoded msg");
    //console.log(msg);
    //if (msg.content_type != "countdown") {
    //    console.log(msg.content_type);
    //    console.log(msg );
    //}
    if (msg.content_type == "answer_status") {
            var data = JSON.parse(msg.data);
            var status = document.querySelector('#answer-status');
            if (status != null) {
                status.innerHTML = data.answer_status;
            }
    }
    if (msg.content_type == "amend_answers_script") {
        if (msg.data != null) {
            if ('error' in msg.data) {
                var message_bar = document.querySelector('#message_bar');
                message_bar.innerText = msg.data['error'];
                message_bar.hidden = false;
                return;
            }
        }
        var container = document.querySelector('#content-container-body-outer');
        container.innerHTML = msg.html;
        equaliseButtons();
        $('.answer-button').each(function() {
            this.addEventListener('click', () => {changeAnswerState(this);});
        });
    }

    if (msg.content_type == "answers_script") {
        var data = JSON.parse(msg.data);
        var container = document.querySelector('#content-container-body-outer');
        container.innerHTML = msg.html;
        var user = document.querySelector('#nickname');
        var userData = data.member_data[user.innerText];
        var selectedAnswer = null;
        if (userData != null) {
            selectedAnswer = userData['answer'];
        }
        var answerButtons = document.querySelectorAll('.answer-div');
        answerButtons.forEach(button => {
            if (button.id == selectedAnswer) {
                button.style.borderColor = "var(--tertiary-colour)"
            } else {
                button.style.borderColor = "#ffffff"
            }
        })
        equaliseButtons();
        answers_chart(msg.data);
    }
    if (msg.content_type == "body") {
        var container = document.querySelector('#content-container-body-outer');
	    container.innerHTML = msg.html;
	    equaliseButtons();
	    if ("animation" in msg) {
	        if (msg.animation != "none") {
	            animate(msg)
	        }
	    }
	    initialiseTooltips();
    }
    if (msg.content_type == "countdown") {
        var content = JSON.parse(msg.data);
        //console.log(`Countdown timer ${content.timer}`);
        var timer = document.querySelector("#countdown");
        if (timer != null) {
            timer.innerText = content.count_value;
        }
        //var answer_status = document.querySelector("#answers-status")
        //if (answer_status) {
        //    answer_status.innerHTML = content.answers_status
        //}
        //if (content.stop_timer == true && timerId != null) {
        //    console.log ("stop timer");
        //    clearInterval(timerId);
    }
    if (msg.content_type == "footer") {
        var container = document.querySelector('#content-container-footer-outer');
	    container.innerHTML = msg.html;
	    if ("animation" in msg) {
	        if (msg.animation != "none") {
	            animate(msg)
	        }
	    }
	    initialiseTooltips();
    }
    if (msg.content_type == "header") {
        var container = document.querySelector('#content-container-header-outer');
        container.innerHTML = msg.html;
    }

    if (msg.content_type == "preview_complete") {
        var content = JSON.parse(msg.data);
        if ("url" in content) {
            window.location.replace(content.url)
        }
    }

    if (msg.content_type == "preview_script") {
        var container = document.querySelector('#content-container-body-outer');
        container.innerHTML = msg.html;
        var user = document.querySelector('#nickname');
        var data = JSON.parse(msg.data);
        if (user.innerText in data) {
            var jokerContainer = document.querySelector('#joker-container');
            if (jokerContainer != null) {
                jokerContainer.classList.remove('d-none');
            }
        }
        initialiseTooltips();
    }

    if (msg.content_type == "results_script") {
        var container = document.querySelector('#content-container-body-outer');
        container.innerHTML = msg.html;
        results(msg.data);
    }

    if (msg.content_type == "score_multiplier_script") {
        var container = document.querySelector('#content-container-inner');
        container.innerHTML = msg.html;
        explode('.score-multiplier-container', '.score-multiplier', 80, 2, 0.2)
        var data = {
                "type": "score-multiplier-end",
                "value": 0
            };
        setTimeout(() => {socket.send(JSON.stringify(data));}, 3000);

    }

    if (msg.content_type == "timer") {
        var content = JSON.parse(msg.data);
        if (content.type == "start timer") {
            startTimer(content.time_limit);
        }
        if (content.type == "stop timer") {
            stopTimer();
        }
    }
}
function changeAnswerState(button) {
    if (button.classList.contains("fa-circle")) {
        button.classList.remove("fa-circle");
        button.classList.add("fa-check-circle")
    } else {
        button.classList.remove("fa-check-circle");
        button.classList.add("fa-circle")
    }
    var message_bar = document.querySelector('#message_bar');
    message_bar.hidden = true;
}

function equaliseButtons() {
    var max_x = 0;
    var max_y = 0;
    var buttons = $('.equal-button');
    //buttons.each((index, button) => {
    //    button.style.setProperty("min-width", "", "");
    //    button.style.setProperty("max-width", "", "");
    //    button.style.setProperty("min-height", "", "");
    //    button.style.setProperty("max-height", "", "");
    //})
    buttons.each((index, button) => {
    //    if (button.offsetWidth > max_x) {
    //        max_x = button.offsetWidth;
    //    }
        if (button.offsetHeight > max_y) {
            max_y = button.offsetHeight;
        }
    })
    buttons.each((index, button) => {
    //    button.style.setProperty("min-width", max_x + "px", "important");
    //    button.style.setProperty("max-width", max_x + "px", "important");
        button.style.setProperty("min-height", max_y + "px", "important");
//        button.style.setProperty("max-height", max_y + "px", "important");
    })
}

function initialiseTooltips() {
    var icons = document.querySelector('.fa-button-pri');
    if (icons != null) {
        enableTooltips();
    }
    var tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]')
}

