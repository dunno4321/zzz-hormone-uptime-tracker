import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

# Global condition flag
should_close = False

def check_condition(app):
    """Run in background to check condition and close early."""
    for i in range(3):
        time.sleep(1)
    app.quit()  # safe to call from non-main thread

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

# Example usage
if __name__ == "__main__":
    # Start overlay
    threading.Thread(target=lambda: overlay_png_on_screen("assets/active.png", imgsize=(100,100), duration=20, callbackfunc=check_condition)).start()

