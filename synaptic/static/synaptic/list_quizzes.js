const addButtons = $('.add-button')

$(document).ready(function(){
    setSavedStatus();
});

function ajaxSuccessAction(response, button) {
}

function ajaxUnsuccessAction(response, button) {
}

function buttonSubmit(e, button) {
    e.preventDefault();
    hideTooltip(button);
    var formData = new FormData();
    formData.append('form', $('form').serialize());
    if (button.dataset.id != null) {
        formData.append('button-id', button.dataset.id);
    }
    ajaxSubmit(event, button, formData);
}

function deleteButton(e, button) {
    e.preventDefault();
    hideTooltip(button);
    var row = document.querySelector(`#${button.dataset.prefix}-row`);
    jRow = $(row)
    var deleted_status = document.querySelector(`#id_${button.dataset.prefix}-deleted`);
    deleted_status.checked = !deleted_status.checked;
    setUnsavedStatus();
    document.querySelector('.alert').hidden = true;
    if (deleted_status.checked == true) {
        button.classList.remove('fa-trash');
        button.classList.add('fa-trash-restore');
        changeTooltipText(button, "Restore Quiz");
        //$(button).tooltip('hide').attr('data-original-title', 'Restore Quiz');
        jRow.find('.delete-hide').prop('hidden', true);
        jRow.find('input').prop('readonly', true);
        jRow.find('.delete-opacity').fadeTo(0, 0.5);
    } else {
        button.classList.remove('fa-trash-restore');
        button.classList.add('fa-trash');
        changeTooltipText(button, "Delete Quiz");
        //$(button).tooltip('hide') .attr('data-original-title', 'Delete Quiz');
        //tooltipText =  'Delete Quiz';
        jRow.find('.delete-hide').prop('hidden', false);
        jRow.find('input').prop('readonly', false);
        jRow.find('.delete-opacity').fadeTo(0, 1);
    }
}

function formChange() {
    document.querySelector('.alert').hidden = true;
    setUnsavedStatus();
}

function savedActions() {
    changeTooltipText(addButton, "Add New Quiz");
    changeTooltipText(backButton, "Back");
}

function unsavedActions() {
    changeTooltipText(addButton, "Save & Add Quiz");
    changeTooltipText(backButton, "Save & Back");
}