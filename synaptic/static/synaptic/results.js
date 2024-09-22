function results(data) {
    leaderboardData = JSON.parse(data);
    leaderData = leaderboardData['leader_data'];
    leaderboardLength = leaderboardData['leaderboard_length'];
    var row_dict = {};
    var container_y = $("#leaderboard-container")[0].getBoundingClientRect()["y"];
    // populate rows with names in previous leaderboard order
    leaderData.forEach((leader, index) => {
        var old_position = leader['old_position'];
        document.querySelector(`#name-${old_position}`).innerHTML = leader['nickname'];
    });
    // keep yoffset position for each row on page in dictionary
    $('.leader-row').each((index, item) => {
        row_dict[index] = {};
        row_dict[index]['old_yOffset'] = item.getBoundingClientRect()["y"] - container_y
    });
    // rows with data for current leaderboard order
    leaderData.forEach((leader, index) => {
        var new_position = leader['new_position'];
        document.querySelector(`#name-${new_position}`).innerText = leader['nickname'];
        var score_field = document.querySelector(`#score-${new_position}`);
        score_field.innerText = numberWithCommas(leader['prior_score']);
        var jokerText = "";
        if (leader['joker'] == true) {
            jokerText = " J";
        }
        document.querySelector(`#added-${new_position}`).innerText =
            `+${numberWithCommas(leader['points_added'])}${jokerText}`;
        if (leader['points_added'] > 0) {
            gsap.fromTo(score_field,
                {innerText: leader['prior_score']},
                {innerText: leader['running_score'], duration: 2,
                    onUpdate: function() {
                    this.targets()[0].innerText = numberWithCommas(Math.ceil(this.targets()[0].textContent));
                    }
                });
        }
    });
    // keep new yoffset position for each row on page in dictionary
    $('.leader-row').each((index, item) => {
        row_dict[index]['new_yOffset'] = item.getBoundingClientRect()["y"] - container_y
    });
    // set animations for row moves
    leaderData.forEach((leader, index) => {
        var offset = row_dict[leader['old_position']]['old_yOffset'] -
            row_dict[leader['new_position']]['new_yOffset'];
        var row = document.querySelector(`#row-${leader['new_position']}`)
        gsap.set(row, {top:`${offset}`});
        gsap.to(row, {top: "0", duration: 2});
        if (leader["new_position"] > leaderboardLength - 1) {
            gsap.to(row, {opacity: 0, duration: 2});
        }
        if (leader["old_position"] > leaderboardLength - 1) {
            gsap.from(row, {opacity: 0, duration: 2});
        }
    });
}
