import os
import shutil
import send2trash
from tkinter import *
from tkinter import ttk, messagebox, filedialog

class FileManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python File Manager")
        self.current_dir = os.getcwd()
        self.selected_item = None
        self.clipboard = None
        self.operation_mode = None
        
        # Styling
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TEntry', padding=5)
        
        # Main Frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        # Operation Buttons
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(fill=X, pady=5)
        
        ttk.Button(self.btn_frame, text="Open", command=self.show_quick_access).pack(side=LEFT, padx=2)
        ttk.Button(self.btn_frame, text="Rename", command=lambda: self.set_operation('rename')).pack(side=LEFT, padx=2)
        ttk.Button(self.btn_frame, text="Move", command=lambda: self.set_operation('move')).pack(side=LEFT, padx=2)
        ttk.Button(self.btn_frame, text="Copy", command=lambda: self.set_operation('copy')).pack(side=LEFT, padx=2)
        ttk.Button(self.btn_frame, text="Delete", command=self.show_delete_options).pack(side=LEFT, padx=2)
        
        # Directory List
        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.pack(fill=BOTH, expand=True)
        
        self.dir_list = Listbox(self.list_frame, width=80, height=20)
        self.dir_list.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
        
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient=VERTICAL, command=self.dir_list.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.dir_list.config(yscrollcommand=self.scrollbar.set)
        
        # Navigation Frame
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=X, pady=5)
        
        ttk.Button(self.nav_frame, text="⬅ Back", command=self.go_back).pack(side=LEFT, padx=2)
        ttk.Button(self.nav_frame, text="🔄 Refresh", command=self.update_list).pack(side=LEFT, padx=2)
        self.path_label = ttk.Label(self.nav_frame, text=self.current_dir)
        self.path_label.pack(side=LEFT, padx=10)
        
        # Action Frame
        self.action_frame = ttk.Frame(self.main_frame)
        
        # Status Bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # Event Bindings
        self.dir_list.bind('<<ListboxSelect>>', self.select_item)
        self.dir_list.bind('<Double-1>', self.navigate_directory)
        
        self.update_list()
    
    def set_operation(self, operation):
        self.operation_mode = operation
        self.show_action_controls()
    
    def show_action_controls(self):
        self.clear_action_frame()
        
        if self.operation_mode == 'rename':
            rename_frame = ttk.Frame(self.action_frame)
            rename_frame.pack(fill=X, pady=5)
            
            ttk.Label(rename_frame, text="New Name:").pack(side=LEFT, padx=5)
            
            self.rename_entry = ttk.Entry(rename_frame, width=30)
            self.rename_entry.pack(side=LEFT, padx=5)
            
            if self.selected_item:
                self.rename_entry.delete(0, END)
                self.rename_entry.insert(0, self.selected_item)
                self.rename_entry.focus_set()
            
            ttk.Button(rename_frame, 
                      text="Apply Rename", 
                      command=self.perform_rename).pack(side=LEFT, padx=5)
        
        elif self.operation_mode in ('move', 'copy'):
            if self.clipboard:
                ttk.Button(self.action_frame,
                         text=f"Paste Here ({'Move' if self.clipboard[1] == 'move' else 'Copy'})",
                         command=self.perform_transfer).pack(side=LEFT)
                ttk.Label(self.action_frame, 
                         text=f"Item: {os.path.basename(self.clipboard[0])}").pack(side=LEFT, padx=10)
            else:
                ttk.Button(self.action_frame,
                         text=f"{self.operation_mode.capitalize()} Selected",
                         command=self.set_clipboard).pack(side=LEFT)
        
        self.action_frame.pack(fill=X, pady=5)
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def clear_action_frame(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()
    
    def update_list(self):
        self.dir_list.delete(0, END)
        try:
            items = os.listdir(self.current_dir)
            for item in sorted(items, key=lambda x: os.path.isdir(os.path.join(self.current_dir, x)), reverse=True):
                self.dir_list.insert(END, item)
            self.path_label.config(text=self.current_dir)
        except PermissionError:
            messagebox.showerror("Error", "Access denied")
        self.selected_item = None
    
    def select_item(self, event):
        if self.dir_list.curselection():
            index = self.dir_list.curselection()[0]
            self.selected_item = self.dir_list.get(index)
            if self.operation_mode == 'rename':
                self.show_action_controls()
    
    def navigate_directory(self, event):
        if self.dir_list.curselection():
            index = self.dir_list.curselection()[0]
            selected = self.dir_list.get(index)
            new_path = os.path.join(self.current_dir, selected)
            
            if os.path.isdir(new_path):
                self.current_dir = new_path
                self.update_list()
                self.show_action_controls()
            else:
                os.startfile(new_path)
    
    def go_back(self):
        parent_dir = os.path.dirname(self.current_dir)
        if os.path.exists(parent_dir):
            self.current_dir = parent_dir
            self.update_list()
            self.show_action_controls()
    
    def perform_rename(self):
        if self.selected_item and self.rename_entry.get():
            old_path = os.path.join(self.current_dir, self.selected_item)
            new_name = self.rename_entry.get()
            new_path = os.path.join(self.current_dir, new_name)
            
            try:
                os.rename(old_path, new_path)
                self.update_list()
                self.rename_entry.delete(0, END)
                self.update_status("Renamed successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please select an item and enter a new name")
    
    def set_clipboard(self):
        if self.selected_item:
            self.clipboard = (
                os.path.join(self.current_dir, self.selected_item),
                self.operation_mode
            )
            self.update_status(f"Item {'copied' if self.operation_mode == 'copy' else 'cut'}: {os.path.basename(self.clipboard[0])}")
            self.show_action_controls()
    
    def perform_transfer(self):
        if self.clipboard:
            source, operation = self.clipboard
            destination = self.current_dir
            
            try:
                item_name = os.path.basename(source)
                dest_path = os.path.join(destination, item_name)
                
                if os.path.exists(dest_path):
                    response = messagebox.askyesnocancel("Conflict", "Item already exists. Overwrite?")
                    if not response:
                        return
                
                self.update_status(f"{'Moving' if operation == 'move' else 'Copying'} {item_name}...")
                
                if operation == 'move':
                    if os.path.isfile(source):
                        shutil.move(source, destination)
                    else:
                        shutil.move(source, dest_path)
                    message = "Moved successfully"
                elif operation == 'copy':
                    if os.path.isfile(source):
                        shutil.copy2(source, destination)
                    else:
                        shutil.copytree(source, dest_path)
                    message = "Copied successfully"
                
                self.clipboard = None
                self.update_list()
                self.update_status(message)
                self.show_action_controls()
            
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))
    
    def show_quick_access(self):
        quick_access = [
            ("📁 Documents", os.path.expandvars('%USERPROFILE%\\Documents')),
            ("🎥 Videos", os.path.expandvars('%USERPROFILE%\\Videos')),
            ("🖼 Pictures", os.path.expandvars('%USERPROFILE%\\Pictures')),
            ("📥 Downloads", os.path.expandvars('%USERPROFILE%\\Downloads'))
        ]
        
        top = Toplevel(self.root)
        top.title("Quick Access")
        
        ttk.Label(top, text="Quick Access Folders:", font='Arial 10 bold').grid(row=0, column=0, pady=5)
        
        for i, (name, path) in enumerate(quick_access):
            ttk.Button(top, text=name, 
                      command=lambda p=path: self.open_path(p, top)).grid(row=i+1, column=0, sticky=W, padx=10)
        
        ttk.Label(top, text="Drives:", font='Arial 10 bold').grid(row=0, column=1, pady=5)
        
        drives = [f"{chr(x)}: " for x in range(65, 91) if os.path.exists(f"{chr(x)}:")]
        for i, drive in enumerate(drives):
            ttk.Button(top, text=f"📀 {drive}", 
                      command=lambda d=drive: self.open_path(d, top)).grid(row=i+1, column=1, sticky=W, padx=10)
    
    def open_path(self, path, window):
        if os.path.exists(path):
            self.current_dir = path
            self.update_list()
            window.destroy()
        else:
            messagebox.showerror("Error", "Path does not exist")
    
    def show_delete_options(self):
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select an item first")
            return
        
        top = Toplevel(self.root)
        top.title("Delete Options")
        
        ttk.Button(top, text="🗑️ Permanent Delete", 
                  command=lambda: self.delete_item(permanent=True, window=top),
                  style='Danger.TButton').grid(row=0, column=0, padx=10, pady=5)
        
        ttk.Button(top, text="♻ Recycle Bin", 
                  command=lambda: self.delete_item(permanent=False, window=top),
                  style='Info.TButton').grid(row=0, column=1, padx=10, pady=5)
        
        self.style.configure('Danger.TButton', foreground='red')
        self.style.configure('Info.TButton', foreground='blue')
    
    def delete_item(self, permanent, window):
        path = os.path.join(self.current_dir, self.selected_item)
        
        try:
            if messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to {'permanently delete' if permanent else 'move to recycle bin'}?\n"
                                   f"{os.path.basename(path)}"):
                if permanent:
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)
                else:
                    send2trash.send2trash(path)
                
                self.update_list()
                window.destroy()
                self.update_status("Item deleted successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    root.geometry("800x600")
    FileManagerGUI(root)
    root.mainloop()