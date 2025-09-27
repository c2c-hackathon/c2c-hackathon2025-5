import logging
import queue
import threading
import time
import typing
from dataclasses import dataclass
from random import *

import library
from matrix_button_led_controller import MatrixButtonLEDController

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
USE_LED_HAT = True

@dataclass
class ButtonInfo:
    color: str
    sound: str
    matched: bool


class Game:
    def __init__(self, button_pad: MatrixButtonLEDController):
        self.button_pad = button_pad
        self.button_pad.assign_button_events(self.when_pressed, self.when_held, self.when_released)
        self.buttons: typing.List[ButtonInfo] = []
        self.sounds: typing.List[str] = []
        self.pressed_before = False
        self.colors: typing.List[str] = []
        self.speaker = library.speaker.Speaker()
        self.initialize_button_pad()
        self.started = False
        self.play_game = True
        self.queue = queue.Queue()
        self.buttonpresses = 0
        self.previous = None
        self.matched_numbers = []

    @property
    def correct_sound(self):
        """The sound that is played when player gets a pair"""
        # OPTIONAL: change this to a different sound if you want
        return "correct_answer"

    @property
    def incorrect_sound(self):
        """The sound that is played when player makes an incorrect guess"""
        # OPTIONAL: change this to a different sound if you want
        return "incorrect"

    @property
    def end_of_game_sound(self):
        """The sound that is played when the game ends."""
        # OPTIONAL: change this to a different sound if you want
        return "end_of_game"

    def _background_logic_checker(self):
        while self.play_game:
            time.sleep(0.005)  # Prevents busy-waiting
            if self.queue.empty():
                continue
            button_number = self.queue.get()
            print(f"Handling button {button_number}")


            # TODO: check your game state, and update things


            
    def when_pressed(self, button):
        # TODO: this is called when a button is pressed. Add what you need to here
        _logger.info(f"Button {button.pin.info.number} pressed")
        self.queue.put(button.pin.info.number)

        button_number = button.pin.info.number
        
        self.speaker.play_preloaded_wav(self.buttons[button_number-1].sound, wait_until_done=False) 

        if button_number in self.matched_numbers :
            return

        if self.previous == button:
            print("same")
            return

        self.button_pad.set_button_led_color(button, self.buttons[button_number-1].color)
        self.buttonpresses += 1
        print(f"You have made {self.buttonpresses} guesses")


        if self.previous != None and self.buttonpresses % 2 == 0 and self.buttons[button_number-1].color == self.buttons[self.previous.pin.info.number-1].color:
            previous_num = self.previous.pin.info.number
            self.buttons[button_number-1].matched = True
            self.buttons[previous_num -1].matched = True
            self.matched_numbers.append(previous_num)
            self.matched_numbers.append(button_number)
            print("matched")
            print(self.matched_numbers)
        elif self.buttonpresses % 2 == 1:
            self.previous = button



    def when_held(self, button):
        button_number = button.pin.info.number
        if button_number == 1:
            self.initialize_button_pad()
        elif button_number == 2:
            for i in range(16):
                button = self.button_pad.get_button(i)
                self.button_pad.set_button_led_color(button, self.buttons[i-1].color)
                self.play_game = False
        # elif button_number == 16:
        #     self.play_game = False
        #     self.thread.join()
        #     self.button_pad.cleanup()
        else:
            pass


        
    def when_released(self, button):
        # TODO: this is called when a button is released. Add what you need to here
        # button_number = button.pin.info.number
        button_number = button.pin.info.number

        if self.buttonpresses != 0 and self.buttonpresses % 2 == 0 and button_number not in self.matched_numbers:
            print("Setting to black")
            self.button_pad.set_button_led_color(button, "black")
            self.button_pad.set_button_led_color(self.previous, "black")
    
        pass

    def initialize_button_pad(self):
        self.button_pad.clear_button_pad()
        # TODO: Set all buttons to a color, List of colors to choose from: https://github.com/waveform80/colorzero/blob/master/colorzero/tables.py#L315
        # sounds are available in the sounds directory
        self.colors = [
            "red",
            "blue",
            "white",
            "yellow",
            "purple",
            "green",
            "pink",
            "aquamarine",
        ]

        self.sounds = [
            "thunder2",
            "fart_z",
            "baby_x",
            "slide_whistle_x",
            "arrow2",
            "phone_pay",
            "bloop_x",
            "car_horn_x",
        ]
        # TODO: assign to buttons
        # self.color_and_sound = {}

        # Set color and sound together
        # PM

        self.color_and_sound=dict(zip(self.colors, self.sounds))

        self.buttons_available=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

        self.buttons = [None] * 16

        for i in range(8):
            for o in range(2):
                random_available_button = choice(self.buttons_available)
                self.buttons[random_available_button - 1] = ButtonInfo(color = self.colors[i], sound = self.color_and_sound[self.colors[i]], matched = False)
                self.buttons_available.remove(random_available_button)
                print(random_available_button, self.buttons[random_available_button - 1])
        



    def _start_game(self):
        self.thread = threading.Thread(target=self._background_logic_checker)
        self.thread.start()
        # TODO: play a sound to start the game
        self.speaker.play_preloaded_wav("drum_roll2", wait_until_done=True)
        self.started = True

    def play(self):
        self._start_game()
        try:
            input("Press Enter to exit the game...")
        except KeyboardInterrupt:
            print("Exiting game...")
            self.speaker.play_preloaded_wav(self.end_of_game_sound(), wait_until_done=True)
        finally:
            self.play_game = False
            self.thread.join()
            self.button_pad.cleanup()


def _main():
    button_pad = MatrixButtonLEDController(
        scan_delay=0.020, pwm_freq=10000, display_pause=0.001, use_led_hat=USE_LED_HAT
    )
    game = Game(button_pad)
    game.play()


if __name__ == "__main__":
    _main()
