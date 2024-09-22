const addQuestionButton = document.getElementById("question");
const answerButtonTexts = document.querySelectorAll('.answer-button-text');
const answerButtonContainers = document.querySelectorAll('.answer-container');
const auto_resize_textareas = document.querySelectorAll('.auto-resize');
const answerRow = document.querySelectorAll('.answer-row');
const media_url = document.querySelector('#id_media_url')
const roundingThreshold = 120;

$(document).ready(function(){
    setAnswerButtonTextareaFontSize();
    setAnswerButtonTextareaHeightAll();
    autoResizeAnswerButtons();
    setAutoResizeTextHeightAll();

    $(window).on('resize', function() {
        setAnswerButtonTextareaFontSize();
        setAnswerButtonTextareaHeightAll();
        autoResizeAnswerButtons();
        setAutoResizeTextHeightAll();
    });
    $('.auto-resize').on('input', function() {
        setTextareaHeight(this);
    })
    $('.auto-resize-answer-buttons').on('input', function() {
        setAnswerButtonTextareaFontSize();
        setAnswerButtonTextareaHeightAll();
        autoResizeAnswerButtons();
    });
});

$('.answer-button').each(function() {
    this.addEventListener('click', () => {changeCorrectAnswerState(this);});
});

$(".dropbox").each((index, dropbox) => {
    dropbox.addEventListener("dragenter", dragenter, false);
    dropbox.addEventListener("dragover", dragover, false);
})

function autoResizeAnswerButtons() {
    var maxScrollHeight = getAnswerButtonsTextMaxHeight();
    answerRow.forEach(elem => {
        elem.style.minHeight = `${maxScrollHeight + 16}px`;
    })
    setAnswerRounded(maxScrollHeight);
};

function buttonSubmit(e, button) {
    e.preventDefault();
    var formData = new FormData(document.querySelector("#question_form"));
    ajaxSubmit(event, button, formData);
}

function changeCorrectAnswerState(button) {
    var checkbox = document.querySelector(button.dataset.checkbox);
    button.classList.remove("fa-circle", "fa-check-circle")
    checkbox.checked = !checkbox.checked;
    if (checkbox.checked) {
        button.classList.add("fa-check-circle")
    } else {
        button.classList.add("fa-circle")
    }
    formChange();
}

function dragenter(e) {
    e.stopPropagation();
    e.preventDefault();
}

function dragover(e) {
    e.stopPropagation();
    e.preventDefault();
}

function dropFile(e, element, fileUploadId, messageElementId, buttonElementId) {
    e.stopPropagation();
    e.preventDefault();
    handleFiles(element, e.dataTransfer.files, fileUploadId, messageElementId, buttonElementId);
    //handleFiles(e.dataTransfer.files, mediaFileList, mediaDropbox, fileUploadMedia, multiple=true)
}

function fileButtonClick(fileUploadId, messageElementId, buttonElementId) {
    var button = document.querySelector(buttonElementId);
    var fileUpload = document.querySelector(fileUploadId);
    if (button.innerHTML == "Clear") {
        handleFiles(fileUpload.files, fileUpload, fileUploadId, messageElementId, buttonElementId);
        media_url.innerText = "";
        media_url.disabled = false;
    }
    else {
        fileUpload.click();
    }
}

function getAnswerButtonsTextMaxCharacters() {
    var maxCharacters = 0;
    answerButtonTexts.forEach(textarea => {
        if (textarea.value.length > maxCharacters) {maxCharacters = textarea.value.length;}
    })
    return maxCharacters;
}

function getAnswerButtonsTextMaxHeight() {
    var maxHeight = 0;
    answerButtonTexts.forEach(elem => {
       if (elem.scrollHeight > maxHeight) { maxHeight = elem.scrollHeight; }
    });
    return maxHeight;
}

function handleFiles(element, files, fileUploadId, messageElementId, buttonElementId) {
    var message = document.querySelector(messageElementId);
    var button = document.querySelector(buttonElementId);
    var fileUpload = document.querySelector(fileUploadId);

    if (files.length == 0) {
        return;
    }
    if (button.innerHTML == "Clear") {
        button.innerHTML = "Add Media";
        message.innerHTML = "Select media file using button or drag-drop";
        fileUpload.value = "";
        return;
    }
    var multiple = false;
    if (element.classList.contains("multiple")) {
        multiple = true;
    }
    if (multiple == false && (files.length > 1)) {
        return;
    }
    if (element.classList.multiple == false && (files.length > 1)) {
        return;
    }
    message.innerText = "";
    for (var i=0; i< files.length; i++) {
        var file = files[i]
        message.innerText = file.name;
        media_url.innerText = file.name;
        autoresizeTextareaHeight(media_url)
        //media_url.disabled = true;
    }
    button.innerText = "Clear";
    fileUpload.files = files;
    setUnsavedStatus();
}

function receiveFiles(element, fileUploadId, messageElementId, buttonElementId) {
    var fileUpload = document.querySelector(fileUploadId);
    handleFiles(element, fileUpload.files, fileUploadId, messageElementId, buttonElementId);
    //handleFiles(fileUploadMedia.files, mediaFileList, mediaDropbox, fileUploadMedia, multiple=true)
}

function saveSubmit(e, button, formId) {
    if (button.value == "Save") {
        ajaxSubmit(event, this, '#question_form')
    }
}

function setAnswerButtonTextHeight(elem) {
    autoresizeTextareaHeight(elem);
}

function setAnswerButtonTextHeightAll() {
    var maxHeight = getAnswerButtonsTextMaxHeight();
    answerButtonTexts.forEach(elem => {
        elem.style.height = "auto";
        elem.style.height = (maxHeight) + 'px';
    })
}

function setAnswerRounded(maxScrollHeight) {
    if (maxScrollHeight > roundingThreshold) {
        answerButtonTexts.forEach(elem => {elem.dataset.shape="rounded";})
        answerButtonContainers.forEach(elem => {elem.dataset.shape="rounded";})
    } else {
        answerButtonTexts.forEach(elem => {elem.dataset.shape="rounded-pill";})
        answerButtonContainers.forEach(elem => {elem.dataset.shape="rounded-pill";})
    }
}

function setAnswerButtonTextareaHeightAll() {
    answerButtonTexts.forEach(elem => {
        autoresizeTextareaHeight(elem);
    })
}

function setAutoResizeTextHeightAll() {
    auto_resize_textareas.forEach(elem => {
        autoresizeTextareaHeight(elem);
    })
}

function setAnswerButtonTextareaFontSize(elem) {
    var maxChars = getAnswerButtonsTextMaxCharacters();
    //answerButtonTexts.removeClass('font-sm font-md font-lg');
    answerButtonTexts.forEach (elem => {
        if (maxChars <= 20) {
            elem.dataset.font_size = "text-xl"
        } else if (maxChars <= 40) {
            elem.dataset.font_size = "text-lg"
        } else {
            elem.dataset.font_size = "text-md"
        }
    })
}

function savedActions() {
    //addButtons.tooltip('hide').attr('data-original-title', 'Add Quiz');
    changeTooltipText(backButton, 'Back');
    changeTooltipText(prevButton, 'Previous');
    changeTooltipText(nextButton, 'Next');
}

function setTextareaHeight(elem) {
    elem.style.height = 'auto';
    elem.style.height = (elem.scrollHeight) + 'px';
}
function unsavedActions() {
    //addButtons.tooltip('hide').attr('data-original-title', 'Save & Add Quiz');
    changeTooltipText(backButton, 'Save & Back');
    changeTooltipText(prevButton, 'Save & Previous');
    changeTooltipText(nextButton, 'Save & Next');
}
