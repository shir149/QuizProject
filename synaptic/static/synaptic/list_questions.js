var draggables = document.querySelectorAll('.draggable');
const dropContainer = document.querySelector('.container');
const hideables = document.querySelectorAll('.hideable')
const rowContainers = document.querySelectorAll('.row-container')
//const body = document.querySelector('body');
//var scrollPosition = 0;

var longTouch = false;
var touchTimer;
var touchDuration = 1000;
var debug = false;

$(document).ready(function(){
    setSavedStatus();
});

draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', dragStart);
    draggable.addEventListener('dragend', dragEnd);

    draggable.addEventListener("touchstart", touchStart, {passive: true});
    draggable.addEventListener("touchmove", touchHandler, {passive: false});
    draggable.addEventListener("touchend", touchEnd, {passive: true});
    draggable.addEventListener("touchcancel", touchHandler, {passive: true});
})

if (dropContainer != null) {
    dropContainer.addEventListener('dragover', dragOver);
}

function ajaxSuccessAction(response, button) {
    addButtons.attr('data-original-title', 'Add Quiz');
    backButtons.attr('data-original-title', 'Back');
}

function ajaxUnsuccessAction(response, button) {
    addButtons.attr('data-original-title', 'Save & Add Quiz');
    backButtons.attr('data-original-title', 'Save & Back');
}

function buttonSubmit(e, button) {
    if (["Add", "Back", "Cancel", "Save", "Update", "Preview"].includes(button.value)) {
        var formData = new FormData();
        formData.append('questionsData', getJsonUpdatedRows());
        if (["Update", "Preview"].includes(button.value)) {
            var draggable = findAncestor(button, 'draggable');
            var questionNumber = parseInt(draggable.querySelector('.question-number').innerText);
            formData.append("selected_question_number", questionNumber)
        }
        ajaxSubmit(event, button, formData);
    }
}

function deleteButton(e, button) {
    e.preventDefault();
    hideTooltip(button);
    var draggable = findAncestor(button, 'draggable');
    draggable.classList.add('deleted');
    draggable.classList.remove('changed');
    draggable.hidden = true;

    renumberAfterDrag();
    setUnsavedStatus();
    document.querySelector('.alert').hidden = true;
}

function dragEnd(e, dragElem) {
    if (dragElem == null) {
        dragElem = this;
    }
//    scrollEnable();
    navbar1.hidden = false;
    navbar2.hidden = false;

    var changed = renumberAfterDrag();
    if (changed) {
        setUnsavedStatus();
    }
    dragElem.classList.remove('dragging');
}

function dragOver(e, type=null) {
    e.preventDefault();
    if (type != "mobile"){
        e.dataTransfer.dropEffect = "move";
    }
    if (type == "mobile") {
        if (e.clientY < window.outerHeight * 0.2) {
            window.scrollBy(0, window.outerHeight * (-0.1));
        } else if (e.clientY > window.outerHeight - (window.outerHeight * 0.2)) {
            window.scrollBy(0, window.outerHeight * 0.1);
        }
    }

    const draggable = document.querySelector('.dragging');
    const returns = getDragAfterElement(dropContainer, draggable, e.clientY);

    if (returns['direction'] == 0) {
        return
    }
    if (returns['direction'] == -1 && returns['elem'] == null) {
        return
    }
    //if (type == "mobile") {

    //}

    //const draggable = document.querySelector('.dragging');
    if (returns['direction'] == 1 && returns['elem'] == null) {
        dropContainer.appendChild(draggable);
    } else {
        dropContainer.insertBefore(draggable, returns['elem']);
    }
}

function dragStart(e, elem=this) {
    navbar1.hidden = true;
    navbar2.hidden = true;
    elem.classList.add('dragging');
}

function expandSubmit(e, button) {
    e.preventDefault();
    hideTooltip(button);
    if (button.dataset.state == "hidden") {
        button.dataset.state = "shown";
        hideables.forEach(elem => { elem.hidden=false; })
        rowContainers.forEach(elem => {elem.classList.add("border")})
        changeTooltipText(button, "Hide Details");
    } else {
        button.dataset.state = "hidden"
        hideables.forEach(elem => { elem.hidden=true; })
        rowContainers.forEach(elem => {elem.classList.remove("border")})
        changeTooltipText(button, "Show Details");
    }
    document.querySelector('.alert').hidden = true;
}

function formChange() {
    document.querySelector('.alert').hidden = true;
    setUnsavedStatus();
}

function getDragAfterElement(container, elem, y) {
    // elem is element being dragged
    // y is y position of cursor
    if (y < getTopY(elem)) {
        const prevSibling = getPrevDragAfterElement(elem);
        if (prevSibling == null) {
            return {"direction": -1, "elem": null};
        }
        if (y < getMidpointY(prevSibling)) {
            return {"direction": -1, "elem": prevSibling};
        }
    } else if (y > getBottomY(elem)) {
        const nextSibling = getNextDragAfterElement(elem, y);
        if (nextSibling == null) {
            return {"direction": 1, "elem": null};
        }
        if (y > getMidpointY(nextSibling)) {
            const beforeElem = getNextDragAfterElement(nextSibling, 0);
            return {"direction": 1, "elem": beforeElem};
        }
    }
    return {"direction": 0, "elem": null};
}

function getNextDragAfterElement(elem, y) {
    var nextSibling = elem.nextElementSibling;
    while (true) {
        if (nextSibling == null) {
            return null;
        }
        if (!nextSibling.classList.contains('draggable')) {
            return null;
        }
//        console.log("nextSiblingY");
//        console.log(nextSibling);
//        console.log(getMidpointY(nextSibling));
//        console.log(y);
        if (!nextSibling.classList.contains('deleted')) {
            return nextSibling;
        }
        nextSibling = nextSibling.nextElementSibling;
    }
}

function getJsonUpdatedRows() {
    var questions  = [];
    var rowId = 0;
    var currQuestionNumber = 0;
    draggables.forEach(draggable => {
        var questionData = {};
        questionData['question_id'] = parseInt(draggable.querySelector('.question-id').value);
        questionData['new_question_number'] = parseInt(draggable.querySelector('.question-number').innerText);
        questionData['changed'] = 0
        if (draggable.classList.contains("changed")) {
            questionData['changed'] = 1;
        }
        questionData['deleted'] = 0
        if (draggable.classList.contains("deleted")) {
            questionData['deleted'] = 1;
        }
        questions.push(questionData);
    })
    return(JSON.stringify(questions));
}

function getQuestionNumber(elem) {
    if (elem == null) {
        return null;
    }
    var questionNumberElem = elem.document.querySelector('.question_number');
    if (questionNumberElem == null) {
        return null;
    }
    return questionNumberElem.innerText;
}

function getPrevDragAfterElement(elem) {
    var prevSibling = elem.previousElementSibling;
    while (true) {
        if (prevSibling == null) {
            return null;
        }
        if (!prevSibling.classList.contains('draggable')) {
            return null;
        }
        if (!prevSibling.classList.contains('deleted')) {
            return prevSibling;
        }
        prevSibling = prevSibling.previousElementSibling;
    }
}

function onLongTouch(event, elem) {
    //console.log("long touch");
    //console.log(elem);
    //document.querySelector('body').style.overflow = 'hidden';
    dragStart(event, elem);
    longTouch = true;
}

function renumberAfterDrag() {
    var changed = false;
    const changedElements = document.querySelectorAll('.draggable:not(.deleted)');
    var questionCount = 1;
    changedElements.forEach(element => {
        var questionNumberElem = element.querySelector('.question-number');
        var questionNumber = parseInt(questionNumberElem.innerText);
        if (questionNumber != questionCount) {
            questionNumberElem.innerText = questionCount;
            element.classList.add('changed');
            changed = true;
        }
        questionCount ++;
    })
    return changed;
}

function savedActions() {
    changeTooltipText(addButton, 'Add Question');
    changeTooltipText(backButton, 'Back');
}

//function scrollDisable() {
//    scrollPosition = window.pageYOffset;
//    body.style.overflow = 'hidden';
//    body.style.position = 'fixed';
//    body.style.top = `-${scrollPosition}px`;
//    body.style.width = '100%';
//}
//
//function scrollDisable2() {
//    body.style.overflow = 'hidden';
//}
//
//function scrollEnable() {
//    body.style.removeProperty('overflow');
//    body.style.removeProperty('position');
//    body.style.removeProperty('top');
//    body.style.removeProperty('width');
//    window.scrollTo(0, scrollPosition);
//}
//
//function scrollEnable2() {
//    body.style.removeProperty('overflow');
//}

function touchHandler(event) {
    if (!longTouch) {
        return;
    }
    var touch = event.changedTouches[0];

    var simulatedEvent = document.createEvent("MouseEvent");
        simulatedEvent.initMouseEvent({
        touchmove: "dragOver",
    }[event.type], true, true, window, 1,
        touch.screenX, touch.screenY,
        touch.clientX, touch.clientY, false,
        false, false, false, 0, null);

    if (simulatedEvent.type == "dragOver") {
        dragOver(simulatedEvent, "mobile");
    }

    touch.target.dispatchEvent(simulatedEvent);
    event.preventDefault();
}

function touchStart(event) {
    timer = setTimeout(onLongTouch, touchDuration, event, this);
}

function touchEnd(event) {
    //document.querySelector('body').style.removeProperty('overflow');
    if (timer) {
        clearTimeout(timer);
    }
    if (longTouch) {
        longTouch = false;
        dragEnd(null, this);
    }

}

function unsavedActions() {
    changeTooltipText(addButton, 'Save & Add Question');
    changeTooltipText(backButton, 'Save & Back');
}

