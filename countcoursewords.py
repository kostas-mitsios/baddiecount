import time
import threading
import sys #drop?
import keyboard
from infi.systray import SysTrayIcon
import os
import pygame
import tkinter as tk

#inits
pygame.mixer.init()
start_time = time.time()
typed_text = ""
exit_event = threading.Event()  # Event to signal threads to exit
current_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(current_dir, "icon.ico").replace("\\", "/")
error_soundfile = os.path.join(current_dir, "error.mp3").replace("\\", "/")

#load error soundfile
pygame.mixer.music.load(error_soundfile)

#bad words
cursed_words = ["damn", "kebap", "oof"] #bad words
cursed_counter = 0

#todo
#appreciating words
appreciating_words = ["damn", "kebap", "oof"] #bad words
appreciating_counter = 0

#todo
#whining words
whining_words = ["damn", "kebap", "oof"] #bad words
whining_counter = 0

#generic popup window
def show_popup(message):
    popup = tk.Tk()
    popup.wm_title("Time running")
    label = tk.Label(popup, text=message)
    label.pack(padx=20, pady=20)
    button = tk.Button(popup, text="OK", command=popup.destroy)
    button.pack(pady=10)
    popup.mainloop()

#time running trigger
def show_time_running(systray):
    running_time = int(time.time() - start_time)
    message = f"Time running: {running_time} seconds"
    show_popup(message)  # Show popup with running time

#exit trigger
def exit_app(systray):
    show_popup("Exiting the application.")  # Show popup when exiting
    exit_event.set()  # Signal to exit the thread
    systray.shutdown()  # Shutdown the systray icon

#reset counter trigger
def reset_counter(systray):
    global cursed_counter
    cursed_counter = 0
    update_tray_text(systray)  # Update the tray text to reflect the reset

#tray update
def update_tray_text(systray):
    """Update tray text to display the counter in the tooltip."""
    tooltip_text = f"Cursed: {cursed_counter} times today!"
    print(f"Updating tray text: {tooltip_text}")  # Debugging statement
    systray.update(icon_path, tooltip_text)  # Update tooltip text

#tray optionset
#todo add pause/continue buttons
menu_options = (
    ("Time running", None, show_time_running),
    ("Reset Cursed Counter", None, reset_counter),  # New option to reset the counter
    ("Exit", None, exit_app),  # Exit option
)

#tray generic
#todo show username in the text as well
systray = SysTrayIcon(icon_path, f"Cursed: {cursed_counter} times today!", menu_options)

#allowed keys (letters, numbers, symbols, space)
allowed_keys = set("abcdefghijklmnopqrstuvwxyz0123456789"  # letters & numbers
                   "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"      # symbols
                   " ")  # space

#captures allowed keystrokes
def capture_key_event(event):
    global typed_text
    key = event.name
    if len(key) == 1 and key in allowed_keys:  #only capture allowed keystrokes
        typed_text += key
    elif key == "space":  #space keystroke registered as ' ' char
        typed_text += " "

#checks for cursed/bad words - plays error sound - increases counter
#todo register indefinitely until enter keystroke or exit/quit buttons on tray
def check_for_cursed_words(text):
    global cursed_counter
    for word in cursed_words:
        if word in text:
            cursed_counter += 1
            pygame.mixer.music.play()
            return True
    return False

#loops every 5" - this is default interval
#todo add choice for user to change the sleep time
def log_typed_text():
    global typed_text
    while not exit_event.is_set():
        time.sleep(5)
        if typed_text:
            print(f"Typed in the last 5 seconds: {typed_text}")
            if check_for_cursed_words(typed_text):
                # Update the tray icon with the new counter
                update_tray_text(systray)
            typed_text = ""  # Reset after logging

#keystrokes listener
keyboard.on_press(capture_key_event)

#start thread for 5" checking of words
log_thread = threading.Thread(target=log_typed_text, daemon=True)
log_thread.start()

#init tray
systray.start()

#wait for the log thread to exit before shutting down
log_thread.join()
