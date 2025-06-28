from PyQt5.QtWidgets import QApplication, QLabel
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import pyautogui
import time
import sys

"""
Fair warning, this code is very messy but it works.
Cleanup will happen, I just want it to work for now lmao
"""

# fancy variables that are no longer used
READY_STATE = 0
UP_STATE = 1
COOLDOWN_STATE = 2
state = READY_STATE
prev_state = READY_STATE
# fancy variables that are used
hp_up = False
hp_ready = True
hp_starttime = datetime.now()
# allow the user to swap to zzz before starting
time.sleep(2)


class Timer:
    """Timer class for handling pauses/ult animations"""
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
    """Finds the basic attack button, used for determining if combat or not"""
    try:
        pyautogui.locateOnScreen('./basic_attack.png', confidence=0.55)
        return True
    except pyautogui.ImageNotFoundException:
        return False

def find_evelyn():
    """Finds evelyn/the agent in evelyn.png, used for determining if eve is the active agent"""
    try:
        pyautogui.locateOnScreen('./evelyn.png', confidence=0.9)
        return True
    except pyautogui.ImageNotFoundException:
        return False

def setup_pyqt():
    """Sets up PyQt5. Did not know what I was doing when i made this but it works so idc"""
    app = QApplication(sys.argv)

    # Create overlay window
    screen = app.primaryScreen()
    return app, screen

# chatgpt bc i dont know pyqt5
class DraggableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(DraggableLabel, self).__init__(*args, **kwargs)
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            print(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

def create_image_overlay(image_path, imgsize=(100,100), location=(100,100)):
    """Overlays an image on the user's screen"""
    # pyqt stuff chatgpt made lmao
    label = DraggableLabel()
    label.setWindowFlags(
        Qt.FramelessWindowHint |
        Qt.WindowStaysOnTopHint |
        Qt.Tool |
        Qt.X11BypassWindowManagerHint
    )
    label.setAttribute(Qt.WA_TranslucentBackground)
    label.setAttribute(Qt.WA_NoSystemBackground, True)
    # Removed WA_TransparentForMouseEvents so it can receive mouse events
    # label.setAttribute(Qt.WA_TransparentForMouseEvents)

    pixmap = QPixmap(image_path)
    pixmap = pixmap.scaled(imgsize[0], imgsize[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
    label.setPixmap(pixmap)
    label.resize(pixmap.size())


    if location[0] is None or location[1] is None:
        # default loc
        label.move(100, 100)
    else:
        label.move(location[0], location[1])

    return label

try:
    # set up variables
    # if eve was onfield last tick
    prev_eve = False
    # if we were in combat last tick
    prev_combat = False
    # are we in combat rn
    in_combat = False
    # is eve onfield
    evelyn = False
    # timer object
    timer = Timer()
    # hormone punk tracking timer
    hp_since_up = 0
    # pyqt setup
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    w, h = screen.geometry().width(), screen.geometry().height()
    mults = 335 / 1920, 74 / 1080
    overlay_loc =  round(w * mults[0]), round(h * mults[1])
    # overlay setup
    # TODO: allow changing of these images/positions/sizes etc (e.g. set draggable maybe)
    active_icon = create_image_overlay("./assets/active.png", imgsize=(100,100), location=overlay_loc)
    active_icon.hide()
    ready_icon = create_image_overlay("./assets/neutral.png", imgsize=(100,100), location=overlay_loc)
    ready_icon.show()
    cooldown_icon = create_image_overlay("./assets/cooldown.png", imgsize=(100,100), location=overlay_loc)
    cooldown_icon.hide()

    # banger name ik
    def update_things():
        # scuffed code lmao
        global hp_since_up, in_combat, prev_combat, prev_eve, evelyn, hp_up, hp_ready, hp_starttime, state, ready_icon, cooldown_icon, active_icon
        # are we in combat
        in_combat = find_basicatk()
        # is eve the active agent
        evelyn = find_evelyn()
        # print(in_combat, evelyn)
        if not in_combat:
            # if we were in combat last tick
            if prev_combat:
                # start the timer to keep hormone uptime accurate
                timer.start()
        elif in_combat and not prev_combat:
            # pause timer
            timer.pause()
        # calculate how long since hormone was up
        hp_since_up = (datetime.now() - hp_starttime - timedelta(seconds=timer.tick())).seconds
        # if we are in combat, were in combat last tick (to prevent ults/pauses from triggering the uptime), hormone punk is ready, and eve was just switched in
        if in_combat and prev_combat and evelyn and hp_ready and not prev_eve:
            # update overlay
            ready_icon.hide()
            active_icon.show()
            cooldown_icon.hide()
            # reset timer
            timer.reset()
            # hormone is up
            hp_up = True
            # start time is now
            hp_starttime = datetime.now()
            # hormone is not ready to go up
            hp_ready = False
        # if hormone is up, and it's been more than 10 seconds but less than 20 seconds (cooldown)
        elif hp_up and (10 <= hp_since_up < 20):
            # update overlay
            ready_icon.hide()
            active_icon.hide()
            cooldown_icon.show()
            # hormone punk not up, but on cooldown
            hp_up = False
        # if it's been more than 20 seconds since hormone went up
        elif hp_since_up >= 20 and not hp_ready:
            # update overlay
            ready_icon.show()
            active_icon.hide()
            cooldown_icon.hide()
            # hormone punk cooldown over, is ready to go
            hp_ready = True
        prev_eve = evelyn
        prev_combat = in_combat

    while True:
        # banger names ik
        update_things()
        app.processEvents()
except KeyboardInterrupt:
    # exit gracefully
    # or smth
    sys.exit(0)
