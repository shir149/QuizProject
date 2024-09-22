const room_number = document.getElementById("id_room_number");
const nickname = document.getElementById("id_nickname");

function selectSubmit(e, button) {
    e.preventDefault();
    var room_number_selected = button.dataset.room_number;
    var room_number_elem = document.getElementById(`id_room_number_${room_number_selected}`);
    var nickname_elem = document.getElementById(`id_nickname_${room_number_selected}`);
    room_number.value = room_number_elem.innerText;
    nickname.value = nickname_elem.innerText;
}
