import time
import tkinter as tk
from PIL import Image, ImageTk
from multiprocessing import Process

counter = 0

def overlay_png_on_screen(image_path, screen_position=(100, 100), datafunc=None):
    # Load the image (must have alpha channel)
    img = Image.open(image_path).convert("RGBA").resize((100, 100))

    # Create transparent window
    root = tk.Tk()
    root.overrideredirect(True)  # Remove borders
    root.attributes('-topmost', True)  # Always on top
    root.wm_attributes('-transparentcolor', 'black')  # Make background transparent
    root.configure(bg='pink')  # Background must match transparent color

    # Position the window
    root.geometry(f'{img.width}x{img.height}+{screen_position[0]}+{screen_position[1]}')

    # Convert image to Tkinter-compatible format
    img_tk = ImageTk.PhotoImage(img)

    # Create canvas with transparent bg
    canvas = tk.Canvas(root, width=img.width, height=img.height, bg='black', highlightthickness=0)
    canvas.pack()

    # Draw the image
    canvas.create_image(0, 0, anchor='nw', image=img_tk)

    return root
    # def check_cond():
    #     if datafunc is not None:
    #         print("callback() condition: " + str(datafunc()))
    #         if datafunc() >= 5:
    #             root.destroy()
    #         else:
    #             root.after(1000, check_cond)
    #
    # root.after(1000, check_cond)
    # root.mainloop()

def thing():
    global counter
    for i in range(5):
        print("thing() condition: " + str(counter))
        counter += 1
        time.sleep(1)

def getcounter():
    global counter
    return counter


if __name__ == "__main__":
    # process = Process(target=thing)
    # process.start()
    root = overlay_png_on_screen("assets/active.png", screen_position=(100, 100), datafunc=getcounter)
    root.mainloop()