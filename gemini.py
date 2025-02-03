import tkinter as tk
from tkinter import ttk
import json

def save_tasks():
    tasks = []
    for task_var, task_text in task_entries.items():
        tasks.append({"text": task_text.get(), "completed": task_var.get()})
    try:
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)
    except Exception as e:
        print(f"Error saving tasks: {e}")


def load_tasks():
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)
            for task_data in tasks:
                add_task(task_data["text"], task_data["completed"])
    except FileNotFoundError:
        pass  # No saved tasks yet
    except json.JSONDecodeError:
        pass # File might be empty or corrupted



def add_task(initial_text="", initial_completed=False):

    task_var = tk.BooleanVar(value=initial_completed)
    task_frame = ttk.Frame(tasks_container, padding=5)
    task_frame.pack(fill=tk.X)

    checkbox = ttk.Checkbutton(task_frame, variable=task_var)
    checkbox.pack(side=tk.LEFT)

    task_text = tk.Entry(task_frame)
    task_text.insert(0, initial_text)
    task_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

    delete_button = ttk.Button(task_frame, text="Delete", command=lambda tf=task_frame: delete_task(tf))
    delete_button.pack(side=tk.LEFT)

    task_entries[task_var] = task_text  # Store for saving

def delete_task(task_frame):
    task_frame.pack_forget()  # Hide the task frame
    for var, entry in task_entries.items():
        if entry.master == task_frame:  #find the task entry to remove
            del task_entries[var]
            break


root = tk.Tk()
root.title("Checklist App")

tasks_container = ttk.Frame(root, padding=10)  # Frame to hold tasks
tasks_container.pack(fill=tk.BOTH, expand=True) # Make it expandable

task_entries = {}  # Dictionary to store task variables and entries

add_button = ttk.Button(root, text="Add Task", command=add_task)
add_button.pack(pady=10)


save_button = ttk.Button(root, text="Save Tasks", command=save_tasks)
save_button.pack()

load_button = ttk.Button(root, text="Load Tasks", command=load_tasks)
load_button.pack()


load_tasks() # Load saved tasks on startup

root.mainloop()