import sys
import tkinter as tk
import pyautogui
import threading
import random
import time
from tkinter import messagebox
from pyclick.humancurve import HumanCurve

class AreaSelector(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry(f"{master.winfo_screenwidth()}x{master.winfo_screenheight()}+0+0")
        self.overrideredirect(True)  # No window decorations
        self.attributes('-alpha', 0.5)  # Transparency
        
        self.canvas = tk.Canvas(self, bg='grey')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.begin = None
        self.end = None
        self.selection_rect = None
        self.area = None

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.mouse_press)
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_release)

    def mouse_press(self, event):
        """Start selection."""
        self.begin = (event.x, event.y)
        self.end = self.begin
        self.selection_rect = self.canvas.create_rectangle(
            self.begin[0], self.begin[1], self.end[0], self.end[1],
            outline="black", fill="white", stipple="gray50"
        )

    def mouse_move(self, event):
        """Update selection rectangle."""
        self.canvas.coords(self.selection_rect, self.begin[0], self.begin[1], event.x, event.y)

    def mouse_release(self, event):
        """Finalize selection."""
        x1 = min(self.begin[0], event.x)
        y1 = min(self.begin[1], event.y)
        x2 = max(self.begin[0], event.x)
        y2 = max(self.begin[1], event.y)
        self.area = (x1, y1, x2, y2)
        self.destroy()  # Close selector

class MouseMoverApp:
    def __init__(self, master):
        self.master = master
        master.title("Mouse Mover")

        # Area selection
        try:
            self.area_selector = AreaSelector(master)
            master.wait_window(self.area_selector)  # Wait until area is selected
            self.area = self.area_selector.area
        except Exception as e:
            messagebox.showerror("Error", f"Error while selecting area: {str(e)}")
            self.area = None

        # Control variables
        self.is_moving = False
        self.moving_thread = None
        self.click_var = tk.BooleanVar(value=True)

        # New: Store initial mouse position to detect small movements
        self.initial_mouse_position = pyautogui.position()
        self.movement_threshold = 10  # Set movement detection threshold to 10 pixels
        
        # UI Elements
        self.click_check = tk.Checkbutton(master, text="Enable Click", variable=self.click_var)
        self.click_check.pack(pady=5)

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start_moving, bg="green", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_moving, state=tk.DISABLED, bg="red", fg="white")
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Developer info
        self.dev_info = tk.Label(master, text="Developed by: Parikshit Shaktawat", fg="black")
        self.dev_info.pack(side=tk.BOTTOM, anchor='se', padx=5, pady=5)

        # Bind mouse movement to track physical mouse movement
        master.bind("<Motion>", self.user_mouse_move)

    def start_moving(self):
        try:
            if not self.area:
                messagebox.showerror("Input Error", "Please select an area first.")
                return

            self.is_moving = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start a new thread for mouse movement
            self.moving_thread = threading.Thread(target=self.move_mouse)
            self.moving_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Error while starting the movement: {str(e)}")

    def stop_moving(self):
        try:
            self.is_moving = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            # Soft stop, wait for thread to finish
            if self.moving_thread is not None:
                self.moving_thread.join()
        except Exception as e:
            messagebox.showerror("Error", f"Error while stopping the movement: {str(e)}")

    def user_mouse_move(self, event):
        """Handle user mouse movement."""
        try:
            current_position = pyautogui.position()

            # Check if the user moved the mouse by more than the threshold
            if abs(current_position[0] - self.initial_mouse_position[0]) > self.movement_threshold or \
               abs(current_position[1] - self.initial_mouse_position[1]) > self.movement_threshold:
                if self.is_moving:
                    self.stop_moving()

            # Update the last known mouse position
            self.initial_mouse_position = current_position
        except Exception as e:
            messagebox.showerror("Error", f"Error while tracking mouse movement: {str(e)}")

    def move_mouse(self):
        try:
            time.sleep(2)  # Delay to allow user to position the mouse
            prev_mouse_position = pyautogui.position()  # Track the initial mouse position

            while self.is_moving:
                # If the user has moved the mouse manually, stop the automatic movement
                current_mouse_position = pyautogui.position()
                if current_mouse_position != prev_mouse_position:
                    self.stop_moving()
                    break

                if hasattr(self, 'area'):
                    x1, y1, x2, y2 = self.area
                    target_x = random.randint(x1, x2)
                    target_y = random.randint(y1, y2)

                    # Smooth movement using HumanCurve
                    current_mouse_position = pyautogui.position()

                    human_curve = HumanCurve(current_mouse_position, (target_x, target_y))

                    # Move through the points on the curve faster
                    for point in human_curve.points:
                        if not self.is_moving:
                            break  # Stop if the movement is disabled

                        # Faster motion with minimal or no duration
                        pyautogui.moveTo(point[0], point[1], duration=0)

                    # If clicking is enabled, click at the new position
                    if self.click_var.get() and self.is_moving:
                        pyautogui.click()

                prev_mouse_position = pyautogui.position()  # Update the position after each movement

        except Exception as e:
            # messagebox.showerror("Error", f"Error during mouse movement: {str(e)}")
            messagebox.showinfo("Interruption", "Motion stopped")



if __name__ == "__main__":
    root = tk.Tk()
    app = MouseMoverApp(root)
    root.mainloop()
