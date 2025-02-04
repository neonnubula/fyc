import tkinter as tk
from tkinter import ttk, messagebox, font
import json
from datetime import datetime, date
import os

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskMaster Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg="#ffffff")
        
        # Try to load custom font, fallback to system font if unavailable
        # self.root.option_add("*Font", "Segoe UI 10")
        
        # Data storage
        self.data_file = "checklists.json"
        self.checklists = self.load_data()
        
        # Color scheme
        self.colors = {
            'bg': '#ffffff',
            'secondary_bg': '#f8f9fa',
            'accent': '#007AFF',
            'text': '#2c3e50',
            'subtle_text': '#95a5a6',
            'border': '#e1e4e8'
        }
        
        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Custom.TFrame', background=self.colors['bg'])
        self.style.configure('Secondary.TFrame', background=self.colors['secondary_bg'])
        self.style.configure('Custom.TLabel', 
                           background=self.colors['bg'], 
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        self.style.configure('Header.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 14, 'bold'))
        self.style.configure('Title.TLabel',
                           background=self.colors['bg'],
                           foreground=self.colors['accent'],
                           font=('Arial', 18, 'bold'))
        
        # Custom button style
        self.style.configure('Accent.TButton',
                           background=self.colors['accent'],
                           foreground='white',
                           padding=(15, 8),
                           font=('Segoe UI', 10))
        
        # Entry style
        self.style.configure('Custom.TEntry',
                           fieldbackground=self.colors['secondary_bg'],
                           borderwidth=0,
                           padding=10)
        
        # Main layout
        self.setup_gui()
        
    def setup_gui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, style='Custom.TFrame', padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title = ttk.Label(main_container, text="TaskMaster Pro", style='Title.TLabel')
        title.config(font=('Arial', 18, 'bold'))
        title.pack(pady=(0, 20))
        
        # Left panel - Checklist management
        left_panel = ttk.Frame(main_container, style='Secondary.TFrame', padding="20")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=0)
        
        ttk.Label(left_panel, text="Create New Checklist", style='Header.TLabel').pack(pady=(0, 15))
        
        # Checklist name input with enter key binding
        self.name_entry = ttk.Entry(left_panel, width=30, style='Custom.TEntry')
        self.name_entry.pack(pady=(0, 10), fill=tk.X)
        self.name_entry.bind('<Return>', lambda e: self.create_checklist())
        
        # Daily refresh option
        self.refresh_var = tk.BooleanVar()
        refresh_check = ttk.Checkbutton(left_panel, text="Daily Refresh", 
                                      variable=self.refresh_var, 
                                      style='Custom.TLabel')
        refresh_check.pack(pady=(0, 10))
        
        # Create button
        create_btn = ttk.Button(left_panel, text="Create Checklist", 
                              command=self.create_checklist,
                              style='Accent.TButton')
        create_btn.pack(pady=(0, 20), fill=tk.X)
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=20)
        
        # Existing checklists
        ttk.Label(left_panel, text="Your Checklists", style='Header.TLabel').pack(pady=(0, 10))
        
        # Custom listbox style
        self.checklist_listbox = tk.Listbox(left_panel, 
                                          width=30, 
                                          height=15,
                                          bg=self.colors['secondary_bg'],
                                          fg=self.colors['text'],
                                          selectmode=tk.SINGLE,
                                          font=('Segoe UI', 10),
                                          relief=tk.FLAT,
                                          highlightthickness=0,
                                          selectbackground=self.colors['accent'])
        self.checklist_listbox.pack(pady=(0, 10), fill=tk.BOTH, expand=True)
        self.checklist_listbox.bind('<<ListboxSelect>>', self.on_select_checklist)
        
        # Delete button
        delete_btn = ttk.Button(left_panel, text="Delete Selected Checklist",
                              command=self.delete_checklist,
                              style='Accent.TButton')
        delete_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Right panel - Task management
        right_panel = ttk.Frame(main_container, style='Custom.TFrame', padding="20")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Task management header
        self.current_checklist_label = ttk.Label(right_panel, text="No Checklist Selected", 
                                               style='Header.TLabel')
        self.current_checklist_label.pack(pady=(0, 20))
        
        # Task input with enter key binding
        task_frame = ttk.Frame(right_panel, style='Custom.TFrame')
        task_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.task_entry = ttk.Entry(task_frame, style='Custom.TEntry')
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_task_btn = ttk.Button(task_frame, text="Add Task",
                                command=self.add_task,
                                style='Accent.TButton')
        add_task_btn.pack(side=tk.LEFT)
        
        # Tasks display
        self.tasks_frame = ttk.Frame(right_panel, style='Custom.TFrame')
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update display
        self.update_checklist_display()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                today = date.today().isoformat()
                for checklist in data.values():
                    if checklist.get('daily_refresh', False) and checklist.get('last_refresh', '') != today:
                        for task in checklist['tasks']:
                            task['done'] = False
                        checklist['last_refresh'] = today
                return data
        return {}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.checklists, f, indent=4)
            
    def create_checklist(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a checklist name")
            return
        if name in self.checklists:
            messagebox.showwarning("Warning", "A checklist with this name already exists")
            return
            
        self.checklists[name] = {
            'daily_refresh': self.refresh_var.get(),
            'tasks': [],
            'last_refresh': date.today().isoformat()
        }
        
        self.save_data()
        self.name_entry.delete(0, tk.END)
        self.refresh_var.set(False)
        self.update_checklist_display()
        
    def delete_checklist(self):
        selection = self.checklist_listbox.curselection()
        if not selection:
            return
            
        name = self.checklist_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            del self.checklists[name]
            self.save_data()
            self.update_checklist_display()
            self.clear_tasks_display()
            
    def update_checklist_display(self):
        self.checklist_listbox.delete(0, tk.END)
        for name in sorted(self.checklists.keys()):
            self.checklist_listbox.insert(tk.END, name)
            
    def on_select_checklist(self, event):
        selection = self.checklist_listbox.curselection()
        if not selection:
            return
            
        name = self.checklist_listbox.get(selection[0])
        self.current_checklist_label.config(text=f"Checklist: {name}")
        self.display_tasks(name)
        
    def add_task(self):
        selection = self.checklist_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a checklist first")
            return
            
        task_text = self.task_entry.get().strip()
        if not task_text:
            return
            
        checklist_name = self.checklist_listbox.get(selection[0])
        self.checklists[checklist_name]['tasks'].append({
            'text': task_text,
            'done': False
        })
        
        self.save_data()
        self.task_entry.delete(0, tk.END)
        self.display_tasks(checklist_name)
        
    def toggle_task(self, checklist_name, task_idx):
        self.checklists[checklist_name]['tasks'][task_idx]['done'] = not self.checklists[checklist_name]['tasks'][task_idx]['done']
        self.save_data()
        self.display_tasks(checklist_name)
        
    def display_tasks(self, checklist_name):
        # Clear existing tasks
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()
            
        # Create scrollable frame
        canvas = tk.Canvas(self.tasks_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Display tasks
        for i, task in enumerate(self.checklists[checklist_name]['tasks']):
            frame = ttk.Frame(scrollable_frame, style='Custom.TFrame')
            frame.pack(fill=tk.X, pady=5)
            
            var = tk.BooleanVar(value=task['done'])
            cb = ttk.Checkbutton(frame, variable=var,
                               command=lambda i=i: self.toggle_task(checklist_name, i),
                               style='Custom.TLabel')
            cb.pack(side=tk.LEFT)
            
            # Strike through text if task is done
            text_style = 'overstrike' if task['done'] else ''
            label = ttk.Label(frame, text=task['text'],
                            style='Custom.TLabel',
                            font=('Segoe UI', 10, text_style),
                            wraplength=400)
            label.pack(side=tk.LEFT, padx=5)
            
    def clear_tasks_display(self):
        self.current_checklist_label.config(text="No Checklist Selected")
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()