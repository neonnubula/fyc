import tkinter as tk
from tkinter import ttk, messagebox, font, simpledialog
import json
from datetime import datetime, date
import os

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Call Centre Checklist")
        self.root.geometry("400x600")
        self.root.configure(bg="#ffffff")
        
        # Try to load custom font, fallback to system font if unavailable
        # self.root.option_add("*Font", "Segoe UI 10")
        
        # Color scheme and styles (most can be reused from previous design)
        self.colors = {
            'bg': '#ffffff',
            'secondary_bg': '#f8f9fa',
            'accent': '#007AFF',
            'text': '#2c3e50',
            'subtle_text': '#95a5a6',
            'border': '#e1e4e8'
        }
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Custom.TFrame', background=self.colors['bg'])
        self.style.configure('Header.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['text'],
                             font=('Segoe UI', 14, 'bold'))
        self.style.configure('Title.TLabel',
                             background=self.colors['bg'],
                             foreground=self.colors['accent'],
                             font=('Arial', 18, 'bold'))
        self.style.configure('Accent.TButton',
                             background=self.colors['accent'],
                             foreground='white',
                             padding=(10, 5),
                             borderwidth=2,
                             relief='raised',
                             font=('Segoe UI', 10))
        self.style.configure('Completed.TButton',
                             background='green',
                             foreground='white',
                             padding=(10, 5),
                             borderwidth=2,
                             relief='raised',
                             font=('Segoe UI', 10))
        self.style.configure('Custom.TEntry',
                             fieldbackground=self.colors['secondary_bg'],
                             borderwidth=0,
                             padding=10)
        
        # Define our call types and checklist modes
        self.call_types = ["sales", "reengagement", "followup", "at-risk", "support", "introduction"]
        self.checklist_options = ["voicemail", "start call"]
        
        # Data file and checklists structure: data is organized by call type then checklist option
        self.data_file = "checklists.json"
        self.checklists = self.load_data()
        
        # The container which we will use to switch between views
        self.container = ttk.Frame(self.root, style='Custom.TFrame', padding="10")
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # To store the currently selected call type & checklist mode for the checklist page
        self.current_call_type = None
        self.current_checklist_type = None
        
        # To reference the task entry and tasks frame in the checklist view
        self.task_entry = None
        self.tasks_frame = None
        
        # Instance variables for Objection mini sub-checklist (Sales, Start Call only)
        self.objection_subchecklist_data = None
        # (We recreate the mini checklist UI each time in display_tasks)
        
        self.show_home_page()
    
    def clear_container(self):
        # Remove all widgets from the container
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def load_data(self):
        data = {}
        today = date.today().isoformat()
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
        
        # Define preset tasks for each call type / checklist option.
        default_voicemail_tasks = [
            {'text': 'Purpose', 'done': False},
            {'text': 'Call to Action', 'done': False},
            {'text': 'Timeframe', 'done': False}
        ]
        preset_tasks = {
            ("sales", "voicemail"): default_voicemail_tasks,
            ("sales", "start call"): [
                {'text': 'Rapport Question', 'done': False},
                {'text': '2nd Open Question', 'done': False},
                {'text': 'Value Add Item', 'done': False},
                {'text': 'Great Ask for Sale', 'done': False},
                {'text': 'Objection', 'done': False},
                {'text': 'Implement Sale Now or "How & When"', 'done': False},
                {'text': 'Summarise Call', 'done': False},
                {'text': 'Book Followup or Next Steps', 'done': False}
            ],
            ("reengagement", "voicemail"): default_voicemail_tasks,
            ("reengagement", "start call"): [],
            ("followup", "voicemail"): default_voicemail_tasks,
            ("followup", "start call"): [],
            ("at-risk", "voicemail"): default_voicemail_tasks,
            ("at-risk", "start call"): [],
            ("support", "voicemail"): default_voicemail_tasks,
            ("support", "start call"): [],
            ("introduction", "voicemail"): default_voicemail_tasks,
            ("introduction", "start call"): [
                {'text': 'Repport Question', 'done': False},
                {'text': '2nd Open Question', 'done': False},
                {'text': 'Value Add Item', 'done': False},
                {'text': 'Learn their Current Situation', 'done': False},
                {'text': 'Learn their Desired Situation', 'done': False},
                {'text': 'Identify their Gap (& Problem Solve or Connect to Us)', 'done': False},
                {'text': 'Additional Support Required?', 'done': False},
                {'text': 'Summarise Call', 'done': False},
                {'text': 'Book Next Call or Followup Steps', 'done': False}
            ]
        }
        
        # Ensure every call type has two checklist modes
        for ct in self.call_types:
            if ct not in data:
                data[ct] = {}
            for option in self.checklist_options:
                if option not in data[ct]:
                    data[ct][option] = {
                        'daily_refresh': False,
                        'tasks': preset_tasks.get((ct, option), []),
                        'last_refresh': today
                    }
                else:
                    checklist = data[ct][option]
                    # If the tasks list is empty and we have a preset for this combination, fill it.
                    if not checklist.get("tasks"):
                        preset = preset_tasks.get((ct, option), [])
                        if preset:
                            checklist["tasks"] = preset
                    # If daily refresh is enabled and the last refresh date isn't today, reset.
                    if checklist.get('daily_refresh', False) and checklist.get('last_refresh', '') != today:
                        for task in checklist.get('tasks', []):
                            task['done'] = False
                        checklist['last_refresh'] = today
        return data
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.checklists, f, indent=4)
    
    def show_home_page(self):
        # Home page: a button for each call type.
        self.clear_container()
        title = ttk.Label(self.container, text="Call Centre Checklist", style='Title.TLabel')
        title.pack(pady=(0, 20))
        instruction = ttk.Label(self.container, text="Select Call Type:", style='Header.TLabel')
        instruction.pack(pady=(0, 10))
        
        for ct in self.call_types:
            btn = ttk.Button(self.container, text=ct.capitalize(),
                             command=lambda ct=ct: self.show_call_sub_menu(ct),
                             style='Accent.TButton')
            btn.pack(fill=tk.X, padx=10, pady=5)
    
    def show_call_sub_menu(self, call_type):
        # Second page: choose between Voicemail or Start Call for the selected call type
        self.clear_container()
        label = ttk.Label(self.container, text=f"Call Type: {call_type.capitalize()}", style='Header.TLabel')
        label.pack(pady=(0, 20))
        instruction = ttk.Label(self.container, text="Select an option:", style='Header.TLabel')
        instruction.pack(pady=(0, 10))
        
        voicemail_btn = ttk.Button(self.container, text="Voicemail",
                                   command=lambda: self.show_checklist_page(call_type, "voicemail"),
                                   style='Accent.TButton')
        voicemail_btn.pack(fill=tk.X, padx=10, pady=5)
        
        start_call_btn = ttk.Button(self.container, text="Start Call",
                                    command=lambda: self.show_checklist_page(call_type, "start call"),
                                    style='Accent.TButton')
        start_call_btn.pack(fill=tk.X, padx=10, pady=5)
    
    def show_checklist_page(self, call_type, checklist_type):
        # Checklist page: show tasks for the selected call type and checklist type.
        self.clear_container()
        self.current_call_type = call_type
        self.current_checklist_type = checklist_type
        
        header = ttk.Label(self.container, 
                           text=f"{call_type.capitalize()} - {checklist_type.capitalize()} Checklist",
                           style='Title.TLabel')
        header.pack(pady=(0, 10))
        
        # "New Call" button resets all tasks (marking every task as not done) then returns to home.
        new_call_btn = ttk.Button(self.container, text="New Call", command=self.new_call, style='Accent.TButton')
        new_call_btn.pack(pady=(0, 10))
        
        # Task input section with entry and add button
        task_frame = ttk.Frame(self.container, style='Custom.TFrame')
        task_frame.pack(fill=tk.X, pady=(0, 10))
        self.task_entry = ttk.Entry(task_frame, style='Custom.TEntry')
        self.task_entry.insert(0, "Add a new task")
        self.task_entry.bind("<FocusIn>", lambda e: self.task_entry.delete(0, tk.END))
        self.task_entry.bind('<Return>', self.add_task)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        add_task_btn = ttk.Button(task_frame, text="+", command=self.add_task, style='Accent.TButton')
        add_task_btn.pack(side=tk.LEFT)
        add_task_btn.config(width=2)
        
        # Tasks will be displayed in a separate frame, scrollable if needed.
        self.tasks_frame = ttk.Frame(self.container, style='Custom.TFrame')
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        self.display_tasks()
    
    def new_call(self):
        # Reset the current checklist by marking all tasks as not done and clearing the objection mini checklist.
        if self.current_call_type and self.current_checklist_type:
            for task in self.checklists[self.current_call_type][self.current_checklist_type]['tasks']:
                task['done'] = False
            self.save_data()
        # Reset the objection sub-checklist (if any)
        self.objection_subchecklist_data = None
        self.display_tasks()
        self.show_home_page()
    
    def add_task(self, event=None):
        task_text = self.task_entry.get().strip()
        if not task_text or task_text == "Add a new task":
            messagebox.showwarning("Warning", "Task cannot be empty")
            return
        
        ct = self.current_call_type
        cl = self.current_checklist_type
        self.checklists[ct][cl]['tasks'].append({'text': task_text, 'done': False})
        self.save_data()
        self.display_tasks()
        self.task_entry.delete(0, tk.END)
    
    def display_tasks(self):
        # Clear existing tasks in tasks_frame
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
            
        ct = self.current_call_type
        cl = self.current_checklist_type
        tasks = self.checklists[ct][cl]['tasks']
        
        # Create a canvas + scrollbar to allow scrolling if the list is long
        canvas = tk.Canvas(self.tasks_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
    
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
    
        # Display each task – including a button to toggle done, an edit and a delete button.
        for i, task in enumerate(tasks):
            frame = ttk.Frame(scrollable_frame, style='Custom.TFrame')
            frame.pack(fill=tk.X, pady=5)
    
            # For the Sales Start Call Objection task, we override the toggle behavior.
            if (ct == "sales" and cl == "start call" and task['text'] == "Objection"):
                # If the objection sub checklist exists and all its tasks are done, change to green.
                style_val = 'Accent.TButton'
                if self.objection_subchecklist_data is not None and all(item['done'] for item in self.objection_subchecklist_data):
                    style_val = 'Completed.TButton'
                task_btn = ttk.Button(frame, text=task['text'],
                                      command=lambda i=i: self.open_objection_subchecklist(),
                                      style=style_val)
            else:
                task_style = 'Completed.TButton' if task['done'] else 'Accent.TButton'
                task_btn = ttk.Button(frame, text=task['text'],
                                      command=lambda i=i: self.toggle_task(i),
                                      style=task_style)
            task_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
            edit_btn = ttk.Button(frame, text="✏️", command=lambda i=i: self.edit_task(i))
            edit_btn.pack(side=tk.LEFT, padx=5)
            edit_btn.config(width=2)
    
            delete_btn = ttk.Button(frame, text="🗑️", command=lambda i=i: self.delete_task(i))
            delete_btn.pack(side=tk.LEFT, padx=5)
            delete_btn.config(width=2)
    
            # If this is the Objection row and the objection mini checklist is active, render it.
            if (ct == "sales" and cl == "start call" and task['text'] == "Objection"
                and self.objection_subchecklist_data is not None):
                self.render_objection_subchecklist(scrollable_frame)
    
    def toggle_task(self, task_idx):
        ct = self.current_call_type
        cl = self.current_checklist_type
        # For Sales/Start Call Objection task, clicking it will open the mini sub-checklist
        if ct == "sales" and cl == "start call" and self.checklists[ct][cl]['tasks'][task_idx]['text'] == "Objection":
            self.open_objection_subchecklist()
            return
        else:
            self.checklists[ct][cl]['tasks'][task_idx]['done'] = not self.checklists[ct][cl]['tasks'][task_idx]['done']
            self.save_data()
            self.display_tasks()
    
    def edit_task(self, task_idx):
        ct = self.current_call_type
        cl = self.current_checklist_type
        task = self.checklists[ct][cl]['tasks'][task_idx]
        new_text = simpledialog.askstring("Edit Task", "Edit the task:", initialvalue=task['text'])
        if new_text is not None and new_text.strip() != "":
            task['text'] = new_text.strip()
            self.save_data()
            self.display_tasks()
    
    def delete_task(self, task_idx):
        ct = self.current_call_type
        cl = self.current_checklist_type
        del self.checklists[ct][cl]['tasks'][task_idx]
        self.save_data()
        self.display_tasks()
    
    def open_objection_subchecklist(self):
        # When Objection is clicked in Sales Start Call, initialize the mini sub-checklist if not already.
        if self.objection_subchecklist_data is None:
            self.objection_subchecklist_data = [
                {'text': 'Listen & Acknowledge', 'done': False},
                {'text': 'Clarify & Question', 'done': False},
                {'text': 'Address the Objection', 'done': False},
                {'text': 'Confirm & Close', 'done': False}
            ]
        # Refresh to show the objection sub-checklist
        self.display_tasks()
    
    def render_objection_subchecklist(self, parent):
        # Render the mini objection checklist vertically.
        sub_frame = ttk.Frame(parent, style='Custom.TFrame')
        sub_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        for idx, subtask in enumerate(self.objection_subchecklist_data):
            btn_style = 'Completed.TButton' if subtask['done'] else 'Accent.TButton'
            btn = ttk.Button(sub_frame, text=subtask['text'], style=btn_style,
                             command=lambda i=idx: self.toggle_objection_item(i))
            btn.pack(fill=tk.X, padx=5, pady=2)
    
    def toggle_objection_item(self, index):
        # Toggle the mini sub-checklist item.
        self.objection_subchecklist_data[index]['done'] = not self.objection_subchecklist_data[index]['done']
        self.display_tasks()

def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()