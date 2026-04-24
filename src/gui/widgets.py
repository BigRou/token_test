import tkinter as tk
from tkinter import ttk


class StatusLabel(ttk.Label):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    
    def set_success(self, text: str):
        self.config(text=text, foreground="green")
    
    def set_error(self, text: str):
        self.config(text=text, foreground="red")
    
    def set_warning(self, text: str):
        self.config(text=text, foreground="orange")
    
    def set_info(self, text: str):
        self.config(text=text, foreground="blue")


class ProgressFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.label = ttk.Label(self, text="")
        self.label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(self, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def start(self, maximum: int):
        self.progress_bar['maximum'] = maximum
        self.progress_bar['value'] = 0
    
    def update(self, value: int, text: str = None):
        self.progress_bar['value'] = value
        if text:
            self.label.config(text=text)
    
    def complete(self, text: str = "完成"):
        self.progress_bar['value'] = self.progress_bar['maximum']
        self.label.config(text=text)
    
    def reset(self):
        self.progress_bar['value'] = 0
        self.label.config(text="")


class ModelCheckboxFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.checkboxes = {}
    
    def add_model(self, model_name: str, checked: bool = True):
        var = tk.BooleanVar(value=checked)
        cb = ttk.Checkbutton(self, text=model_name, variable=var)
        cb.pack(side=tk.LEFT, padx=10)
        self.checkboxes[model_name] = var
    
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.checkboxes.clear()
    
    def get_selected(self) -> list:
        return [name for name, var in self.checkboxes.items() if var.get()]
    
    def select_all(self):
        for var in self.checkboxes.values():
            var.set(True)
    
    def deselect_all(self):
        for var in self.checkboxes.values():
            var.set(False)