import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List


class ModelDialog:
    def __init__(self, parent, title: str, model_data: Dict = None, model_list: List[Dict] = None):
        self.result = None
        self.selected_model_name = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x520")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.model_data = model_data or {}
        self.model_list = model_list or []
        
        # 如果有模型列表，使用第一个模型的数据作为默认值
        if self.model_list and not self.model_data:
            self.model_data = self.model_list[0].copy()
        
        self._create_widgets()
        
        # 如果有模型列表，初始化下拉框
        if self.model_list:
            model_names = [m.get("name", "") for m in self.model_list]
            if model_names:
                self.model_combo.set(model_names[0])
                self._load_model_data(model_names[0])
        
        self.dialog.wait_window()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 如果是编辑模式且有模型列表，显示下拉选择
        if self.model_list:
            ttk.Label(main_frame, text="选择模型", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
            self.selected_model_var = tk.StringVar()
            model_names = [m.get("name", "") for m in self.model_list]
            self.model_combo = ttk.Combobox(main_frame, textvariable=self.selected_model_var, 
                                            values=model_names, state="readonly", width=50)
            self.model_combo.pack(fill=tk.X, pady=(5, 15))
            self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)
        
        # 模型名称
        ttk.Label(main_frame, text="模型名称", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        self.name_var = tk.StringVar(value=self.model_data.get("name", ""))
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        name_entry.pack(fill=tk.X, pady=(5, 12))
        
        # API接口地址
        ttk.Label(main_frame, text="API接口地址", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        self.api_url_var = tk.StringVar(value=self.model_data.get("api_url", "https://coding.dashscope.aliyuncs.com/v1"))
        api_url_entry = ttk.Entry(main_frame, textvariable=self.api_url_var, width=50)
        api_url_entry.pack(fill=tk.X, pady=(5, 12))
        
        # API密钥
        ttk.Label(main_frame, text="API密钥", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        self.api_key_var = tk.StringVar(value=self.model_data.get("api_key", ""))
        api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key_var, width=50, show="•")
        api_key_entry.pack(fill=tk.X, pady=(5, 12))
        
        # 接口协议
        ttk.Label(main_frame, text="接口协议", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        protocol_frame = ttk.Frame(main_frame)
        protocol_frame.pack(fill=tk.X, pady=(5, 12))
        
        self.protocol_var = tk.StringVar(value=self.model_data.get("protocol", "openai"))
        ttk.Radiobutton(protocol_frame, text="OpenAI兼容", variable=self.protocol_var, 
                        value="openai").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(protocol_frame, text="Anthropic兼容", variable=self.protocol_var, 
                        value="anthropic").pack(side=tk.LEFT)
        
        # Temperature 和 Max Tokens 并排
        params_frame = ttk.Frame(main_frame)
        params_frame.pack(fill=tk.X, pady=(5, 15))
        
        # Temperature
        temp_frame = ttk.Frame(params_frame)
        temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(temp_frame, text="Temperature", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        self.temperature_var = tk.StringVar(value=str(self.model_data.get("temperature", 0.7)))
        temp_entry = ttk.Entry(temp_frame, textvariable=self.temperature_var, width=20)
        temp_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Max Tokens
        max_tokens_frame = ttk.Frame(params_frame)
        max_tokens_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        ttk.Label(max_tokens_frame, text="Max Tokens", font=('Microsoft YaHei', 10)).pack(anchor=tk.W)
        self.max_tokens_var = tk.StringVar(value=str(self.model_data.get("max_tokens", 2048)))
        max_tokens_entry = ttk.Entry(max_tokens_frame, textvariable=self.max_tokens_var, width=20)
        max_tokens_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 15))
        
        # 底部按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 取消按钮（白色背景）
        cancel_btn = tk.Button(btn_frame, text="取消", command=self._cancel,
                               bg="white", fg="#333", relief="solid", 
                               bd=1, width=10, font=('Microsoft YaHei', 9))
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # 测试连接按钮（紫色背景）
        test_btn = tk.Button(btn_frame, text="测试连接", command=self._test_connection,
                             bg="#7B68EE", fg="white", relief="flat",
                             width=12, font=('Microsoft YaHei', 9))
        test_btn.pack(side=tk.RIGHT, padx=5)
        
        # 保存按钮（绿色背景）
        save_btn = tk.Button(btn_frame, text="保存", command=self._save,
                             bg="#4CAF50", fg="white", relief="flat",
                             width=10, font=('Microsoft YaHei', 9))
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def _on_model_selected(self, event=None):
        selected_name = self.selected_model_var.get()
        self._load_model_data(selected_name)
    
    def _load_model_data(self, model_name: str):
        for model in self.model_list:
            if model.get("name") == model_name:
                self.selected_model_name = model_name
                
                # 更新界面上的值
                self.name_var.set(model.get("name", ""))
                self.api_url_var.set(model.get("api_url", "https://coding.dashscope.aliyuncs.com/v1"))
                self.api_key_var.set(model.get("api_key", ""))
                self.protocol_var.set(model.get("protocol", "openai"))
                self.temperature_var.set(str(model.get("temperature", 0.7)))
                self.max_tokens_var.set(str(model.get("max_tokens", 2048)))
                break
    
    def _validate(self) -> bool:
        if not self.name_var.get().strip():
            messagebox.showwarning("提示", "请输入模型名称")
            return False
        
        if not self.api_url_var.get().strip():
            messagebox.showwarning("提示", "请输入API接口地址")
            return False
        
        if not self.api_key_var.get().strip():
            messagebox.showwarning("提示", "请输入API密钥")
            return False
        
        return True
    
    def _save(self):
        if not self._validate():
            return
        
        # 如果是编辑模式，记录原模型名称
        if self.model_list and hasattr(self, 'selected_model_var') and self.selected_model_var.get():
            self.selected_model_name = self.selected_model_var.get()
        
        self.result = {
            "name": self.name_var.get().strip(),
            "api_url": self.api_url_var.get().strip(),
            "api_key": self.api_key_var.get().strip(),
            "protocol": self.protocol_var.get(),
            "temperature": float(self.temperature_var.get()),
            "max_tokens": int(self.max_tokens_var.get())
        }
        
        self.dialog.destroy()
    
    def _cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def _test_connection(self):
        if not self._validate():
            return
        
        from ..api.openai import OpenAICompatibleAPI
        from ..api.anthropic import AnthropicCompatibleAPI
        
        protocol = self.protocol_var.get()
        
        try:
            if protocol == "openai":
                api = OpenAICompatibleAPI(
                    api_url=self.api_url_var.get().strip(),
                    api_key=self.api_key_var.get().strip(),
                    model_name=self.name_var.get().strip(),
                    temperature=float(self.temperature_var.get()),
                    max_tokens=int(self.max_tokens_var.get())
                )
            else:
                api = AnthropicCompatibleAPI(
                    api_url=self.api_url_var.get().strip(),
                    api_key=self.api_key_var.get().strip(),
                    model_name=self.name_var.get().strip(),
                    temperature=float(self.temperature_var.get()),
                    max_tokens=int(self.max_tokens_var.get())
                )
            
            success, message = api.test_connection()
            
            if success:
                messagebox.showinfo("连接测试", f"✓ {message}")
            else:
                messagebox.showerror("连接测试", f"✗ {message}")
        except Exception as e:
            messagebox.showerror("连接测试", f"✗ 测试失败: {str(e)}")