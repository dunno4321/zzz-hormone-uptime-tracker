from PyQt5.QtWidgets import QApplication, QLabel
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import threading
import pyautogui
import time
import sys

READY_STATE = 0
UP_STATE = 1
COOLDOWN_STATE = 2
state = READY_STATE
prev_state = READY_STATE
hp_up = False
hp_ready = True
hp_starttime = datetime.now()
time.sleep(2)


class Timer:
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
        self.paused = False

    def start(self):
        """Start or resume the timer."""
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True
            self.paused = False
        elif self.paused:
            self.start_time = time.time() - self.elapsed_time
            self.paused = False

    def stop(self):
        """Stop the timer."""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.paused = False

    def pause(self):
        """Pause the timer."""
        if self.running and not self.paused:
            self.elapsed_time = time.time() - self.start_time
            self.paused = True

    def reset(self):
        """Reset the timer to zero."""
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
        self.paused = False

    def tick(self):
        """Return the current elapsed time in seconds."""
        if self.running and not self.paused:
            return round(time.time() - self.start_time)
        return round(self.elapsed_time)

def find_basicatk():
    try:
        pyautogui.locateOnScreen('basic_attack.png', confidence=0.5)
        return True
    except pyautogui.ImageNotFoundException:
        return False

def find_evelyn():
    try:
        pyautogui.locateOnScreen('evelyn.png', confidence=0.9)
        return True
    except pyautogui.ImageNotFoundException:
        return False


def overlay_png_on_screen(image_path, imgsize=(100, 100), location=(None,None), duration=30, callbackfunc=None):
    app = QApplication(sys.argv)

    # Create overlay window
    screen = app.primaryScreen()
    screen_geometry = screen.geometry()

    label = QLabel()
    label.setWindowFlags(
        Qt.FramelessWindowHint |
        Qt.WindowStaysOnTopHint |
        Qt.Tool |
        Qt.X11BypassWindowManagerHint
    )
    label.setAttribute(Qt.WA_TranslucentBackground)
    label.setAttribute(Qt.WA_NoSystemBackground, True)
    label.setAttribute(Qt.WA_TransparentForMouseEvents)

    pixmap = QPixmap(image_path)
    pixmap = pixmap.scaled(imgsize[0], imgsize[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
    label.setPixmap(pixmap)
    label.resize(pixmap.size())

    if location[0] is None and location[1] is None:
        x = (screen_geometry.width() - pixmap.width()) // 2
        y = (screen_geometry.height() - pixmap.height()) // 2
        label.move(x, y)
    else:
        label.move(location[0], location[1])

    label.show()

    # Timer for natural timeout
    QTimer.singleShot(duration * 1000, app.quit)

    # Thread to check for early close
    if callbackfunc is not None:
        threading.Thread(target=callbackfunc, args=(app,), daemon=True).start()

    sys.exit(app.exec_())


try:
    # set up variables
    # if eve was onfield last tick
    prev_eve = False
    # if we were in combat last tick
    prev_combat = True
    # timer object
    timer = Timer()

    def ready_callback(app):
        global state
        while state == READY_STATE:
            pass

    def up_callback(app):
        pass
    def cooldown_callback(app):
        pass
    while True:
        # are we in combat
        in_combat = find_basicatk()
        # if we are not in combat
        if not in_combat:
            # if we were in combat last tick
            if prev_combat:
                # start the timer to keep hormone uptime accurate
                timer.start()
            # debug
            print("PAUSED")
        elif in_combat and not prev_combat:
            # pause timer
            timer.pause()
        # check if evelyn is the active agent
        evelyn = find_evelyn()
        # calculate how long since hormone was up
        hp_since_up = (datetime.now() - hp_starttime - timedelta(seconds=timer.tick())).seconds
        # optional debug
        # print(hp_since_up)
        # if we are in combat, hormone punk is ready, and eve was just switched in
        if in_combat and evelyn and hp_ready and not prev_eve:
            # hormone is up
            hp_up = True
            # start time is now
            hp_starttime = datetime.now()
            # hormone is not ready to be up
            hp_ready = False
            # TODO: overlay here
        # if hormone is up, and it's been more than 10 seconds but less than 20 seconds
        elif hp_up and (10 <= hp_since_up < 20):
            # hormone punk not up, but on cooldown
            hp_up = False
            # TODO: overlay here
        # if it's been more than 20 seconds since hormone went up
        elif hp_since_up >= 20:
            # hormone punk is ready
            # TODO: overlay here
            hp_ready = True
        # helpful information, to be converted to an overlay
        # hopefully today
        if hp_ready:
            timer.reset()
            print("READY")
            state = READY_STATE
        elif hp_up:
            print("UP")
            state = UP_STATE
        elif not hp_up and not hp_ready:
            print("COOLDOWN")
            state = COOLDOWN_STATE
        # update variables so we can do fancy logic at the start
        prev_eve = evelyn
        prev_combat = in_combat
        # TODO: unused var?
        prev_state = state
except KeyboardInterrupt:
    pass
