import logging

import pykka
from mopidy import core
import time
from mopidy_raspberry_gpio.sound import play_sound
logger = logging.getLogger(__name__)


class RaspberryGPIOFrontend(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super().__init__()
        import RPi.GPIO as GPIO

        self.core = core
        self.config = config["raspberry-gpio"]
        self.pin_settings = {}
        self.last_pin_action = {}

        GPIO.setwarnings(False)
        #GPIO.setmode(GPIO.BCM)
        GPIO.setmode(GPIO.BOARD)

        # Iterate through any bcmN pins in the config
        # and set them up as inputs with edge detection
        for key in self.config:
            if key.startswith("bcm"):
                pin = int(key.replace("bcm", ""))
                settings = self.config[key]
                if settings is None:
                    continue

                pull = GPIO.PUD_UP
                edge = GPIO.FALLING
                if settings.active == "active_high":
                    pull = GPIO.PUD_DOWN
                    edge = GPIO.RISING

                GPIO.setup(pin, GPIO.IN, pull_up_down=pull)

                GPIO.add_event_detect(
                    pin,
                    edge,
                    callback=self.gpio_event,
                    bouncetime=settings.bouncetime,
                )
                self.last_pin_action[pin] = round(time.time() * 1000)
                self.pin_settings[pin] = settings

    def gpio_event(self, pin):
        time_now = round(time.time() * 1000)
        logger.info('GPIO event pin: %s, time %s', pin, time_now)
        if time_now - self.last_pin_action[pin] > 1000:
           self.last_pin_action[pin] = time_now
           logger.info('triggering action for pin %s', pin)
           settings = self.pin_settings[pin]
           self.dispatch_input(settings.event)

    def dispatch_input(self, event):
        handler_name = f"handle_{event}"
        try:
            getattr(self, handler_name)()
        except AttributeError:
            raise RuntimeError(
                f"Could not find input handler for event: {event}"
            )

    def handle_play_pause(self):
        play_sound('success.mp3')
        if self.core.playback.get_state().get() == core.PlaybackState.PLAYING:
            self.core.playback.pause()
        else:
            self.core.playback.play()

    def handle_next(self):
        play_sound('success.mp3')
        self.core.playback.next()

    def handle_prev(self):
        play_sound('success.mp3')
        self.core.playback.previous()

    def handle_volume_up(self):
        play_sound('success.mp3')
        volume = self.core.mixer.get_volume().get()
        volume += 5
        volume = min(volume, 100)
        self.core.mixer.set_volume(volume)

    def handle_volume_down(self):
        play_sound('success.mp3')
        volume = self.core.mixer.get_volume().get()
        volume -= 5
        volume = max(volume, 0)
        self.core.mixer.set_volume(volume)
