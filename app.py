import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
from datetime import datetime, timedelta
import calendar

class ModernChecklistManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist Manager")
        self.root.geometry("800x600")
        
        # Color scheme
        self.colors = {
            'bg': '#FFFFFF',
            'light_blue': '#E3F2FD',
            'medium_blue': '#90CAF9',
            'navy': '#1976D2',
            'text': '#2C3E50',
            'light_gray': '#F5F5F5'
        }
        
        # Configure root window background
        self.root.configure(bg=self.colors['bg'])
        
        # Configure fonts
        self.setup_fonts()
        
        # Configure styles
        self.setup_styles()
        
        # Data storage
        self.data_dir = "checklists"
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.current_checklist = None
        self.checklists = {}
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.checklists = json.load(f)
        
        self.setup_gui()
        self.refresh_library()
        
    def setup_fonts(self):
        # Use system fonts that look good on Mac
        self.fonts = {
            'header': font.Font(family='SF Pro Display', size=16, weight='bold'),
            'subheader': font.Font(family='SF Pro Display', size=14),
            'body': font.Font(family='SF Pro Text', size=12),
            'small': font.Font(family='SF Pro Text', size=10)
        }
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')  # Start with default theme
        
        # Configure common elements
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['light_blue'])
        
        # Buttons
        style.configure('Modern.TButton',
            background=self.colors['navy'],
            foreground='white',
            padding=(15, 5),
            font=self.fonts['body'])
            
        style.map('Modern.TButton',
            background=[('active', self.colors['medium_blue'])])
            
        # Secondary buttons
        style.configure('Secondary.TButton',
            background=self.colors['light_blue'],
            foreground=self.colors['navy'],
            padding=(10, 5),
            font=self.fonts['body'])
            
        # Treeview (Library)
        style.configure('Modern.Treeview',
            background=self.colors['bg'],
            fieldbackground=self.colors['bg'],
            font=self.fonts['body'])
            
        style.configure('Modern.Treeview.Heading',
            background=self.colors['light_blue'],
            font=self.fonts['subheader'])
            
        # Entry fields
        style.configure('Modern.TEntry',
            padding=(5, 5),
            fieldbackground=self.colors['light_gray'])
            
        # Checkbuttons
        style.configure('Modern.TCheckbutton',
            background=self.colors['bg'],
            font=self.fonts['body'])

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Main container with two panes
        self.paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Checklist Library
        self.setup_library_panel()
        
        # Right panel - Current Checklist
        self.setup_checklist_panel()
    def create_new_checklist(self):
        """Open dialog to create a new checklist"""
        dialog = ModernChecklistDialog(self.root, self)
        self.root.wait_window(dialog)

    def on_checklist_select(self, event):
        """Handle checklist selection from library"""
        selection = self.library_tree.selection()
        if selection:
            checklist_name = self.library_tree.item(selection[0])['text']
            self.load_checklist(checklist_name)

    def show_context_menu(self, event):
        """Show right-click menu"""
        selection = self.library_tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)
    
    def delete_checklist(self):
        """Delete the selected checklist"""
        selection = self.library_tree.selection()
        if selection:
            checklist_name = self.library_tree.item(selection[0])['text']
            if messagebox.askyesno("Delete Checklist", 
                                 f"Are you sure you want to delete '{checklist_name}'?"):
                del self.checklists[checklist_name]
                self.save_checklists()
                self.refresh_library()
                if self.current_checklist == checklist_name:
                    self.current_checklist = None
                    self.checklist_title.config(text="No Checklist Selected")
                    for widget in self.scrollable_frame.winfo_children():
                        widget.destroy()

    def load_checklist(self, name):
        """Load and display the selected checklist"""
        self.current_checklist = name
        checklist_data = self.checklists[name]
        
        self.checklist_title.config(text=name)
        
        # Clear existing tasks
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Add tasks with checkboxes
        for task in checklist_data['tasks']:
            self.create_task_row(task)

    def save_checklists(self):
        """Save all checklists to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.checklists, f)

    def refresh_library(self):
        """Refresh the library view"""
        self.library_tree.delete(*self.library_tree.get_children())
        for name, data in self.checklists.items():
            self.library_tree.insert('', 'end', text=name, 
                                   values=(data['type'], f"{len(data['tasks'])} tasks"))

    def add_task(self):
        """Add a new task to current checklist"""
        if not self.current_checklist:
            messagebox.showwarning("Warning", "Please select or create a checklist first!")
            return
            
        task_text = self.task_entry.get().strip()
        if task_text:
            self.checklists[self.current_checklist]['tasks'].append({
                'description': task_text,
                'completed': False
            })
            self.save_checklists()
            self.load_checklist(self.current_checklist)
            self.task_entry.delete(0, tk.END)
            self.refresh_library()

    def toggle_task(self, task, var):
        """Toggle task completion status"""
        task['completed'] = var.get()
        if task['completed']:
            task['completion_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        else:
            task.pop('completion_date', None)
        self.save_checklists()
        self.load_checklist(self.current_checklist)

    def complete_checklist(self):
        """Mark all tasks in checklist as complete"""
        if not self.current_checklist:
            return
            
        checklist = self.checklists[self.current_checklist]
        all_completed = True
        for task in checklist['tasks']:
            if not task['completed']:
                all_completed = False
                task['completed'] = True
                task['completion_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                
        if all_completed:
            if checklist['type'] != 'one-off':
                self.reset_recurring_checklist()
            else:
                messagebox.showinfo("Complete", "Checklist completed!")
                
        self.save_checklists()
        self.load_checklist(self.current_checklist)

    def reset_recurring_checklist(self):
        """Reset all tasks for recurring checklists"""
        checklist = self.checklists[self.current_checklist]
        for task in checklist['tasks']:
            task['completed'] = False
            task.pop('completion_date', None)

    def setup_library_panel(self):
        library_frame = ttk.Frame(self.paned, style='Modern.TFrame')
        self.paned.add(library_frame, weight=1)
        
        # Library header
        header_frame = ttk.Frame(library_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, 
                text="My Checklists",
                font=self.fonts['header'],
                fg=self.colors['navy'],
                bg=self.colors['bg']).pack(side=tk.LEFT)
                
        ttk.Button(header_frame,
                  text="+ New Checklist",
                  style='Modern.TButton',
                  command=self.create_new_checklist).pack(side=tk.RIGHT)
        
        # Checklist library
        self.library_tree = ttk.Treeview(library_frame,
                                       columns=('type', 'tasks'),
                                       show='tree headings',
                                       style='Modern.Treeview')
        self.library_tree.pack(fill=tk.BOTH, expand=True)
        
        self.library_tree.heading('type', text='Type')
        self.library_tree.heading('tasks', text='Tasks')
        
        # Style the columns
        self.library_tree.column('type', width=100)
        self.library_tree.column('tasks', width=80)
        
        self.library_tree.bind('<<TreeviewSelect>>', self.on_checklist_select)
        
        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        self.context_menu.add_command(label="Delete", command=self.delete_checklist)
        self.library_tree.bind("<Button-3>", self.show_context_menu)
        
    def setup_checklist_panel(self):
        checklist_frame = ttk.Frame(self.paned, style='Modern.TFrame')
        self.paned.add(checklist_frame, weight=2)
        
        # Checklist header
        self.header_frame = ttk.Frame(checklist_frame, style='Modern.TFrame')
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.checklist_title = tk.Label(self.header_frame,
                                      text="No Checklist Selected",
                                      font=self.fonts['header'],
                                      fg=self.colors['navy'],
                                      bg=self.colors['bg'])
        self.checklist_title.pack(side=tk.LEFT)
        
        self.complete_button = ttk.Button(self.header_frame,
                                        text="Complete All",
                                        style='Modern.TButton',
                                        command=self.complete_checklist)
        self.complete_button.pack(side=tk.RIGHT)
        
        # Task entry
        entry_frame = ttk.Frame(checklist_frame, style='Card.TFrame')
        entry_frame.pack(fill=tk.X, pady=(0, 20), ipady=10, ipadx=10)
        
        self.task_entry = ttk.Entry(entry_frame, style='Modern.TEntry', font=self.fonts['body'])
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        
        ttk.Button(entry_frame,
                  text="Add Task",
                  style='Modern.TButton',
                  command=self.add_task).pack(side=tk.RIGHT, padx=10)
        
        # Tasks list
        self.tasks_frame = ttk.Frame(checklist_frame, style='Modern.TFrame')
        self.tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tasks_canvas = tk.Canvas(self.tasks_frame,
                                    bg=self.colors['bg'],
                                    highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tasks_frame,
                                orient=tk.VERTICAL,
                                command=self.tasks_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.tasks_canvas, style='Modern.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.tasks_canvas.configure(scrollregion=self.tasks_canvas.bbox("all"))
        )
        
        self.tasks_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.tasks_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_task_row(self, task):
        frame = ttk.Frame(self.scrollable_frame, style='Modern.TFrame')
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        var = tk.BooleanVar(value=task['completed'])
        
        task_frame = ttk.Frame(frame, style='Card.TFrame')
        task_frame.pack(fill=tk.X, ipady=5, ipadx=5)
        
        cb = ttk.Checkbutton(task_frame,
                            variable=var,
                            style='Modern.TCheckbutton',
                            command=lambda: self.toggle_task(task, var))
        cb.pack(side=tk.LEFT, padx=10)
        
        task_label = tk.Label(task_frame,
                            text=task['description'],
                            font=self.fonts['body'],
                            fg=self.colors['text'],
                            bg=self.colors['light_blue'])
        task_label.pack(side=tk.LEFT, padx=5)
        
        if task['completed']:
            date = datetime.strptime(task['completion_date'], '%Y-%m-%d %H:%M')
            tk.Label(task_frame,
                    text=date.strftime('%Y-%m-%d %H:%M'),
                    font=self.fonts['small'],
                    fg='gray',
                    bg=self.colors['light_blue']).pack(side=tk.RIGHT, padx=10)

    # [All other methods remain the same]

class ModernChecklistDialog(tk.Toplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("Create New Checklist")
        self.geometry("400x300")
        
        # Apply the same styling
        self.configure(bg=manager.colors['bg'])
        
        self.setup_gui()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main_frame,
                text="Create New Checklist",
                font=self.manager.fonts['header'],
                fg=self.manager.colors['navy'],
                bg=self.manager.colors['bg']).pack(pady=(0, 20))
        
        # Name
        name_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        name_frame.pack(fill=tk.X, pady=10)
        tk.Label(name_frame,
                text="Checklist Name:",
                font=self.manager.fonts['body'],
                fg=self.manager.colors['text'],
                bg=self.manager.colors['bg']).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, style='Modern.TEntry', font=self.manager.fonts['body'])
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Type
        type_frame = ttk.Frame(main_frame, style='Card.TFrame')
        type_frame.pack(fill=tk.X, pady=10, ipady=10)
        tk.Label(type_frame,
                text="Type:",
                font=self.manager.fonts['body'],
                fg=self.manager.colors['text'],
                bg=self.manager.colors['light_blue']).pack(side=tk.LEFT, padx=10)
        
        self.type_var = tk.StringVar(value="one-off")
        for t in ["one-off", "daily", "weekly", "monthly"]:
            ttk.Radiobutton(type_frame,
                           text=t,
                           variable=self.type_var,
                           value=t,
                           style='Modern.TRadiobutton').pack(side=tk.LEFT, padx=5)
        
        # Time
        time_frame = ttk.Frame(main_frame, style='Card.TFrame')
        time_frame.pack(fill=tk.X, pady=10, ipady=10)
        tk.Label(time_frame,
                text="Time:",
                font=self.manager.fonts['body'],
                fg=self.manager.colors['text'],
                bg=self.manager.colors['light_blue']).pack(side=tk.LEFT, padx=10)
        
        self.hour_var = tk.StringVar(value="9")
        self.minute_var = tk.StringVar(value="00")
        ttk.Spinbox(time_frame,
                   from_=0,
                   to=23,
                   width=3,
                   textvariable=self.hour_var,
                   style='Modern.TSpinbox').pack(side=tk.LEFT)
        tk.Label(time_frame,
                text=":",
                font=self.manager.fonts['body'],
                bg=self.manager.colors['light_blue']).pack(side=tk.LEFT)
        ttk.Spinbox(time_frame,
                   from_=0,
                   to=59,
                   width=3,
                   textvariable=self.minute_var,
                   style='Modern.TSpinbox').pack(side=tk.LEFT)
        
        # Create button
        ttk.Button(main_frame,
                  text="Create Checklist",
                  style='Modern.TButton',
                  command=self.create_checklist).pack(pady=20)

    def create_checklist(self):
        """Create a new checklist and add it to the manager"""
        name = self.name_entry.get().strip()
        checklist_type = self.type_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()

        if not name:
            messagebox.showwarning("Warning", "Please enter a checklist name.")
            return

        if name in self.manager.checklists:
            messagebox.showwarning("Warning", "A checklist with this name already exists.")
            return

        # Create a new checklist entry
        self.manager.checklists[name] = {
            'type': checklist_type,
            'tasks': [],
            'time': f"{hour}:{minute}"
        }

        # Save the new checklist and refresh the library view
        self.manager.save_checklists()
        self.manager.refresh_library()

        # Close the dialog
        self.destroy()

def main():
    root = tk.Tk()
    app = ModernChecklistManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()