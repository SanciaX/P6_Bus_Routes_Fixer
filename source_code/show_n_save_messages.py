import tkinter as tk
from tkinter import ttk
def show_n_save_messages(all_messages):
    # Create the main window
    root = tk.Tk()
    root.title("Route Review Messages")

    # Create a frame to hold the Text widget and Scrollbar
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a Scrollbar
    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    # Create a Text widget with a scrollbar
    text_widget = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set)
    text_widget.pack(fill="both", expand=True)

    # Configure the scrollbar
    scrollbar.config(command=text_widget.yview)

    # Insert the accumulated messages into the text widget in one go
    text_widget.insert(tk.END, all_messages)

    # Disable the text widget to prevent editing
    text_widget.config(state=tk.DISABLED)

    # Start the Tkinter event loop
    root.mainloop()

