import random

# constant classes
class Constants:
    LEADERBOARD_SIZE_MAX    = 5
    PREVIEW_TIMEOUT         = 5
    MAX_JOKERS              = 3


# message type constants for websocket messages
class MessageType:
    AMEND_ANSWERS_SCRIPT    = "amend_answers_script"
    ANSWER_STATUS           = "answer_status"
    ANSWERS_SCRIPT          = "answers_script"
    SCORE_MULTI_SCRIPT      = "score_multiplier_script"
    BODY                    = "body"
    COUNTDOWN               = "countdown"                  # sends the countdown time updates
    DISCONNECT              = "disconnect"
    FOOTER                  = "footer"
    HEADER                  = "header"
    PREVIEW_COMPLETE        = "preview_complete"
    PREVIEW_STATE_SCRIPT    = "preview_script"
    RESULTS_SCRIPT          = "results_script"
    TIMER                   = "timer"                      # starts/stops the countdown

# message content constants for websocket messages
class MessageContent:
    QUESTION         = "question"
    START_TIMER      = "start timer"
    STOP_TIMER       = "stop timer"
    WAITING_ROOM     = "waiting"

# message group codes
class SendGroup:
    ALL    = "all"
    HOST   = "host"
    MEMBER = "member"
    ME     = "me"

# quiz status codes
class CheckStatus:
    READY        = "Ready"
    NOT_READY    = "Not Ready"

# room member status codes
class RoomMemberStatus:
    JOINED = "joined"
    LEFT   = "left"
    ALL   = "all"

# room status codes
class RoomStatus:
    ACTIVE           = "Active"
    AMEND_ANSWER     = "Amend Answer"
    ANSWER           = "Answer"
    QUESTION         = "Question"
    QUESTION_PREVIEW = "Question Preview"
    RESULTS          = "Results"
    SCORE_MULTIPLIER = "Score Multiplier"
    WAITING          = "Waiting"

# user type codes
class UserType:
    ALL    = "all"
    HOST   = "host"
    MEMBER = "member"

# user type codes
class AnimationType:
    EXPAND_FROM_CENTRE      = "expand_from_centre"
    FADE_IN                 = "fade_in"
    NONE                    = "none"
    HORIZONTAL_GROW         = "horizontal_grow"
    ROTATE_GROW_IN          = "rotate_grow_in"
    SCROLL                  = "scroll"
    SWIPE_FROM_BOTTOM       = "swipe_from_bottom"
    SWIPE_FROM_BOTTOM_LEFT  = "swipe_from_bottom_left"
    SWIPE_FROM_BOTTOM_RIGHT = "swipe_from_bottom_right"
    SWIPE_FROM_LEFT         = "swipe_from_left"
    SWIPE_FROM_RIGHT        = "swipe_from_right"
    SWIPE_FROM_TOP          = "swipe_from_top"
    SWIPE_FROM_TOP_LEFT     = "swipe_from_top_left"
    SWIPE_FROM_TOP_RIGHT    = "swipe_from_top_right"

# question method codes - determine whether the question screen is in add or edit mode
class FormFunction:
    CREATE = "create"
    UPDATE  = "update"
    DELETE = "delete"

# function return codes
class ReturnCodes:
    SUCCESS = 0
    FAILED  = 1

# message return codes
class MessageTypes:
    SUCCESS = "success"
    ERROR  = "error"

# question spreadsheet constants
class ExcelConstants:
    headers_row = 8
    headers_col = 1
    headers = [
        {"title": "question", "mandatory": True},
        {"title": "answer 1", "mandatory": True},
        {"title": "answer 2", "mandatory": True},
        {"title": "answer 3", "mandatory": True},
        {"title": "answer 4", "mandatory": True},
        {"title": "time limit", "mandatory": True},
        {"title": "correct answer", "mandatory": True},
        {"title": "media url", "mandatory": False},
        {"title": "score multiplier", "mandatory": False},
    ]
    question = 1
    answer1 = 2
    answer2 = 3
    answer3 = 4
    answer4 = 5
    time_limit = 6
    correct_answers = 7
    media_url = 8
    score_multiplier = 9

class DefaultImages:

    def __init__(self):
        self.default_images = [
            r'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Mus%C3%A9e_Rodin_1.jpg/800px-Mus%C3%A9e_Rodin_1.jpg',
            r'https://upload.wikimedia.org/wikipedia/commons/9/96/Thinking_%282808468566%29.jpg',
            r'https://live.staticflickr.com/3585/3444386664_7d73d90ccd_b.jpg',
            r'https://live.staticflickr.com/4027/4446734924_aeb9132c50.jpg',
            r'https://live.staticflickr.com/2360/2403249501_a57876dcb8_b.jpg',
            r'https://live.staticflickr.com/7157/6666891615_fd4e0b22a7_b.jpg',
            r'https://live.staticflickr.com/4061/4695658106_042a83f4f4_b.jpg',
            r'https://live.staticflickr.com/7323/9612772316_316c4642d7_b.jpg',
            r'https://live.staticflickr.com/149/394359583_b164643e76_b.jpg',
            r'https://live.staticflickr.com/3362/3205277810_8283a3e4b5_b.jpg',
            r'https://live.staticflickr.com/24/99535218_fdfab8c28b_b.jpg',
            r'https://live.staticflickr.com/2468/3623768629_d854236b17.jpg',
            r'https://live.staticflickr.com/78/181269963_cb8026af80_b.jpg',
            r'https://live.staticflickr.com/8058/8165692802_2dec851efa_b.jpg',
            r'https://live.staticflickr.com/8333/8127175006_1c056e2aaf_b.jpg',
            r'https://live.staticflickr.com/1180/1340980539_a3909d6c20_b.jpg',
            r'https://live.staticflickr.com/3091/2711755476_8975dd43ea.jpg',
            r'https://live.staticflickr.com/113/263551766_9bae56d04f_b.jpg',
            r'https://live.staticflickr.com/8012/7379137804_afc8e7cc61_b.jpg',
            r'https://live.staticflickr.com/4017/4587293562_2c66da3f4e.jpg'
        ]

    def get_random_default_image_number(self):
        return random.randint(0, len(self.default_images)-1)

    def get_default_image_url(self, image_number):
        if image_number > len(self.default_images) - 1:
            image_number = self.get_random_default_image_number()
        return self.default_images[image_number]



