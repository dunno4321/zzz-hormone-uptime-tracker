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
    print("OVERLAY CALLED: " + image_path)
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
        print("set up callback")
        threading.Thread(target=callbackfunc, args=(app,), daemon=True).start()

    app.exec_()

try:
    # set up variables
    # if eve was onfield last tick
    prev_eve = False
    # if we were in combat last tick
    prev_combat = False
    in_combat = False
    evelyn = False
    # timer object
    timer = Timer()
    hp_since_up = 0

    # banger name ik
    def update_things():
        global hp_since_up, in_combat, prev_combat, prev_eve, evelyn, hp_up, hp_ready, hp_starttime, state
        # are we in combat
        in_combat = find_basicatk()
        evelyn = find_evelyn()
        # print(in_combat, evelyn)
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
            state = UP_STATE
            threading.Thread(overlay_png_on_screen("assets/active.png", imgsize=(100,100), location=(100,100), duration=20, callbackfunc=up_callback)).start()
            print("after overlay")
        # if hormone is up, and it's been more than 10 seconds but less than 20 seconds
        elif hp_up and (10 <= hp_since_up < 20):
            # hormone punk not up, but on cooldown
            hp_up = False
            # TODO: overlay here
            state = COOLDOWN_STATE
            threading.Thread(overlay_png_on_screen("assets/cooldown.png", imgsize=(100, 100), location=(100, 150), duration=20, callbackfunc=cooldown_callback)).start()
            print("after overlay2")
        # if it's been more than 20 seconds since hormone went up
        elif hp_since_up >= 20 and not hp_ready:
            # hormone punk is ready
            # TODO: overlay here
            hp_ready = True
            state = READY_STATE
            threading.Thread(overlay_png_on_screen("assets/neutral.png", imgsize=(100, 100), location=(100, 250), duration=20, callbackfunc=ready_callback)).start()
            print("after overlay3")
        prev_eve = evelyn
        prev_combat = in_combat

    def ready_callback(app):
        global hp_since_up, state
        print("callback READY")
        while state == READY_STATE:
            update_things()
            print("READY: " + str(state))
        print("END OF READY")
        app.quit()

    def up_callback(app):
        global hp_since_up, state
        print("callback UP")
        while state == UP_STATE:
            update_things()
            if hp_since_up >= 10:
                state = COOLDOWN_STATE
            print("UP: " + str(state))
        print("END OF UPTIME")
        app.quit()

    def cooldown_callback(app):
        global hp_since_up, state
        print("callback COOLDOWN")
        while state == COOLDOWN_STATE:
            update_things()
            print("COOLDOWN: " + str(state))
            if hp_since_up >= 20:
                state = READY_STATE
        print("END OF COOLDOWN")
        app.quit()

    while True:
        update_things()
        # helpful information, to be converted to an overlay
        # hopefully today
        if state == READY_STATE:
            timer.reset()
            print("READY")
        elif state == UP_STATE:
            print("UP")
            state = UP_STATE
        elif state == COOLDOWN_STATE:
            print("COOLDOWN")
            state = COOLDOWN_STATE
        # update variables so we can do fancy logic at the start
        prev_eve = evelyn
        prev_combat = in_combat
        # TODO: unused var?
        prev_state = state
except KeyboardInterrupt:
    pass
