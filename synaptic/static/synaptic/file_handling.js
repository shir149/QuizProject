const fileUploadExcel = document.getElementById("id_file_upload_excel");
const fileUploadMedia = document.getElementById("id_file_upload_media");
const excelDropbox = document.getElementById("xl_dropbox");
const mediaDropbox = document.getElementById("media_dropbox");
const submitButton = document.getElementById("upload_submit");
const doneButton = document.getElementById("exit");
const clearExcelButton = document.querySelector('#clear_excel');
const clearMediaButton = document.querySelector('#clear_media');
const selectExcelButton = document.querySelector('#xl_file_select');
const selectMediaButton = document.querySelector('#media_file_select');

const introExcel = document.querySelector('#intro-excel');
const introMedia = document.querySelector('#intro-media');
var excelFileList = [];
var mediaFileList = [];

$(".dropbox").each((index, dropbox) => {
    dropbox.addEventListener("dragenter", dragenter, false);
    dropbox.addEventListener("dragover", dragover, false);
})
excelDropbox.addEventListener("drop", dropExcel, false);
mediaDropbox.addEventListener("drop", dropMedia, false);
fileUploadExcel.addEventListener("change", receiveFilesExcel, false);
fileUploadMedia.addEventListener("change", receiveFilesMedia, false);
//submitButton.addEventListener("click", ajaxSubmit, false);
//set_state();
window.addEventListener("resize", resize, false);

resize();

function buttonSubmit(e, button) {
    e.preventDefault();
    //var formData = new FormData();
    //formData.append('form', $('#upload_files_form').serialize());
    var formData = new FormData(document.querySelector("#upload_files_form"));
    //formData.append('button-id', button.dataset.id);
    ajaxSubmit(event, button, formData);
}

function clearExcel() {
    excelFileList = [];
    excelDropbox.innerHTML = "";
    fileUploadExcel.value = "";
    set_state();
    var excel_error = document.querySelector('#id_file_upload_excel_error');
    if (excel_error != null) {
        excel_error.innerText = "";
    }
}

function clearMedia() {
    mediaFileList = [];
    mediaDropbox.innerHTML = "";
    fileUploadMedia.value = "";
    set_state();
    var media_error = document.querySelector('#id_file_upload_media_error');
    if (media_error != null) {
        media_error.innerText = "";
    }
}

function dragenter(e) {
    e.stopPropagation();
    e.preventDefault();
}

function dragover(e) {
    e.stopPropagation();
    e.preventDefault();
}

function dropExcel(e) {
    e.stopPropagation();
    e.preventDefault();
    handleFiles(e.dataTransfer.files, excelFileList, excelDropbox, fileUploadExcel, multiple=false);
}

function dropMedia(e) {
    e.stopPropagation();
    e.preventDefault();
    handleFiles(e.dataTransfer.files, mediaFileList, mediaDropbox, fileUploadMedia, multiple=true)
}

function handleFiles(files, fileList, dropbox, fileUpload, multiple=false) {
    if (files.length == 0) {
        return;
    }
    if (multiple == false && (files.length > 1 || fileList.length > 0)) {
        return;
    }
    dropbox.innerHTML = "";
    for (var i=0; i< files.length; i++) {
        var file = files[i]
        if (dropbox.innerHTML.length == 0) {
            dropbox.innerHTML = file.name;
        }
        else {
            dropbox.innerHTML += "<br>" + file.name
        }
    }
    fileUpload.files = files;
    var errors = document.getElementById("excel-errors");
    if (errors != null) {
        errors.remove();
    }
    set_state();
    setUnsavedStatus();
};

function receiveFilesExcel() {
    handleFiles(fileUploadExcel.files, excelFileList, excelDropbox, fileUploadExcel, multiple=false);
}

function receiveFilesMedia() {
    handleFiles(fileUploadMedia.files, mediaFileList, mediaDropbox, fileUploadMedia, multiple=true);
}

function resize() {
    var targetHeight = `${Math.max(introExcel.offsetHeight, introMedia.offsetHeight)}px`;
    introExcel.style.minHeight = targetHeight;
    introMedia.style.minHeight = targetHeight;
}

function set_state() {
    if (excelDropbox.innerHTML.length == 0) {
        selectExcelButton.disabled = false;
        clearExcelButton.disabled = true;
    }
    else {
        selectExcelButton.disabled = true;
        clearExcelButton.disabled = false;
    }

    if (mediaDropbox.innerHTML.length == 0) {
        selectMediaButton.disabled = false;
        clearMediaButton.disabled = true;
    }
    else {
        selectMediaButton.disabled = true;
        clearMediaButton.disabled = false;
    }

    if (excelDropbox.innerHTML.length > 0 || mediaDropbox.innerHTML.length > 0) {
        setUnsavedStatus();
        //submitButton.disabled = false;
        //doneButton.disabled = true;
    }
    else {
        setSavedStatus();
        //submitButton.disabled = true;
        //doneButton.disabled = false;
    }

}

function savedActions(response, button) {
    changeTooltipText(backButton, "Back");
    disableIconButton(uploadButton)
}

function unsavedActions(response, button) {
    changeTooltipText(backButton, "Upload & Back");
    enableIconButton(uploadButton)
}
