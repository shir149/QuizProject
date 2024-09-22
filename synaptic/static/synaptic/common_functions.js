const navbar1 = document.querySelector('#navbar1');
const navbar2 = document.querySelector('#navbar2');
const topPageElement = document.querySelector('.top-page-element')
const messageBar = document.querySelector('#message_bar');
const addButton = document.querySelector('#iconbar_add')
const backButton = document.querySelector('#iconbar_back')
const cancelButton = document.querySelector('#iconbar_cancel')
const nextButton = document.querySelector('#iconbar_next')
const prevButton = document.querySelector('#iconbar_prev')
const saveButton = document.querySelector('#iconbar_save')
const uploadButton = document.querySelector('#iconbar_upload')

enableTooltips();

function ajaxSubmit(e, button, formData) {
    e.preventDefault();
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
    formData.append('submit', button.value)

    $.ajax({
        url: '',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        headers: {'X-CSRFToken': csrftoken},
        success: function(response) {
            var success = response['success']
            clearErrorFields();
            clearMessages();
            if (success) {
                setSuccessMessage(response);
                setSavedStatus();
                ajaxSuccessAction(response, button);
            } else {
                setErrorMessage(response);
                setFieldErrors(response);
                setUnsavedStatus();
                ajaxUnsuccessAction(response, button);
            }
            if ('redirect' in response) {
                window.location.assign(response.redirect);
            }
        },
        failure: function() {
            alert('Error occurred while calling our Django view');
            doneButton.value = "Cancel";
        }
    })
}

function ajaxSuccessAction(response, button) {
}

function ajaxUnsuccessAction(response, button) {
}

function autoresizeTextareaHeight(textarea) {
    if (textarea != null) {
        textarea.style.height = "auto";
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
}

function changeTooltipText(button, text) {
    if (button != null) {
        button.setAttribute('data-bs-original-title', text);
    }
}

function clearErrorFields() {
    var errorFields = document.querySelectorAll('.error-field');
    errorFields.forEach(element => {element.innerText = "";})
}

function clearMessages() {
    messageBar.innerText = "";
    messageBar.hidden = true;
}

function disableIconButton(button) {
    if (button != null) {
        button.dataset.state = "disabled"
        button.disabled = true;
        };
}

function doNothing(e) {
    e.preventDefault();
}

function enableIconButton(button) {
    if (button != null) {
        button.dataset.state = "enabled"
        button.disabled = false;
        };
}

function enableTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {trigger : 'hover'})
    })
}

function findAncestor (el, cls) {
    while ((el = el.parentNode) && !el.classList.contains(cls));
    return el;
}

function formChange() {
    document.querySelector('.alert').hidden = true;
    setUnsavedStatus();
}



function getBottomY(elem) {
    if (elem != null) {
        const box = elem.getBoundingClientRect();
        return box.top + box.height;
    }
    return null;
}

function getMidpointY(elem) {
    const box = elem.getBoundingClientRect();
    return box.top + (box.height) / 2;
}

function getTopY(elem) {
    if (elem != null) {
        const box = elem.getBoundingClientRect();
        return box.top;
    }
    return null;
}

function hideTooltip(element) {
    var tooltip = bootstrap.Tooltip.getInstance(element);
    if (tooltip != null) {
        tooltip.hide();
    }
}

function navbarClick() {
    if (navbar1 == null) {return};
    if (navbar1.dataset.state == "show") {
        // navbar is being hidden
        navbar1.dataset.state = "hide";
        if (navbar2 != null) {navbar2.dataset.state ="hide"};
        if (topPageElement != null) {topPageElement.dataset.state ="hide"};
    } else {
        // navbar is being shown
        navbar1.dataset.state = "show";
        if (navbar2 != null) {navbar2.dataset.state ="show"};
        if (topPageElement != null) {topPageElement.dataset.state ="show"};
    }
}

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function rounded(elem) {
    elem.dataset.shape = "rounded";
}

function roundedPill(elem) {
    elem.dataset.shape = "rounded-pill";
}

function setErrorMessage(response) {
    if ('non_field_error' in response) {
        messageBar.classList.remove('alert-success');
        messageBar.classList.add('alert-danger');
        messageBar.innerText = response['non_field_error']['alert'];
        messageBar.hidden = false;
    }
}

function setFieldErrors(response) {
    if ('field_errors' in response) {
        for (var key in response['field_errors']) {
            var id = document.querySelector(key);
            if (id != null) {id.innerText = response['field_errors'][key]; }
        }
    }
}

function setSavedStatus() {
    disableIconButton(saveButton);
    disableIconButton(cancelButton);
    savedActions();
}

function setSuccessMessage(response) {
    if ('success-message' in response) {
        if (response['success-message'].length == 0) {
            messageBar.hidden = true;
        } else {
            messageBar.classList.remove('alert-danger');
            messageBar.classList.add('alert-success');
            messageBar.innerText = response['success-message'];
            messageBar.hidden = false;
        }
    }
}

function setUnsavedStatus() {
    enableIconButton(saveButton);
    enableIconButton(cancelButton);
    unsavedActions();
}
