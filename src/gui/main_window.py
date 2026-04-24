import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Callable
import threading

from .model_dialog import ModelDialog
from ..utils.config import ConfigManager
from ..tester.speed_test import SpeedTester


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI模型速度测试工具")
        self.root.geometry("900x850")
        self.root.minsize(900, 850)
        self.root.configure(bg='#f5f5f5')
        
        self.config_manager = ConfigManager()
        self.speed_tester = SpeedTester()
        
        self.models = self.config_manager.load_models()
        self.settings = self.config_manager.load_settings()
        
        self.selected_models = {}
        self.test_results = []
        self.is_testing = False
        
        self._create_widgets()
        self._load_initial_data()
    
    def _create_widgets(self):
        # 主容器
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 模型选择区域 - 卡片式
        model_card = tk.Frame(main_container, bg='white', bd=1, relief='solid')
        model_card.pack(fill=tk.X, pady=(0, 10))
        
        # 模型选择标题
        model_header = tk.Frame(model_card, bg='#f8f9fa', height=35)
        model_header.pack(fill=tk.X)
        model_header.pack_propagate(False)
        
        tk.Label(model_header, text="📦 模型选择", font=('Microsoft YaHei', 11, 'bold'),
                bg='#f8f9fa', fg='#333').pack(side=tk.LEFT, padx=12, pady=8)
        
        # 模型复选框区域
        model_content = tk.Frame(model_card, bg='white', padx=12, pady=10)
        model_content.pack(fill=tk.X)
        
        self.model_frame = tk.Frame(model_content, bg='white')
        self.model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 模型按钮区域
        btn_frame = tk.Frame(model_content, bg='white')
        btn_frame.pack(fill=tk.X)
        
        # 添加模型按钮（绿色）
        add_btn = tk.Button(btn_frame, text="➕ 添加模型", command=self._add_model,
                          bg='#4CAF50', fg='white', font=('Microsoft YaHei', 9),
                          relief='flat', padx=12, pady=5, cursor='hand2')
        add_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 编辑模型按钮（橙色）
        edit_btn = tk.Button(btn_frame, text="✏️ 编辑模型", command=self._edit_model,
                          bg='#FF9800', fg='white', font=('Microsoft YaHei', 9),
                          relief='flat', padx=12, pady=5, cursor='hand2')
        edit_btn.pack(side=tk.LEFT, padx=8)
        
        # 删除模型按钮（红色）
        delete_btn = tk.Button(btn_frame, text="🗑️ 删除模型", command=self._delete_model,
                              bg='#f44336', fg='white', font=('Microsoft YaHei', 9),
                              relief='flat', padx=12, pady=5, cursor='hand2')
        delete_btn.pack(side=tk.LEFT, padx=8)
        
        # 导入配置按钮
        import_btn = tk.Button(btn_frame, text="📥 导入配置", command=self._import_config,
                              bg='#2196F3', fg='white', font=('Microsoft YaHei', 9),
                              relief='flat', padx=12, pady=5, cursor='hand2')
        import_btn.pack(side=tk.LEFT, padx=8)
        
        # 导出配置按钮
        export_btn = tk.Button(btn_frame, text="📤 导出配置", command=self._export_config,
                              bg='#2196F3', fg='white', font=('Microsoft YaHei', 9),
                              relief='flat', padx=12, pady=5, cursor='hand2')
        export_btn.pack(side=tk.LEFT, padx=8)
        
        # 测试配置区域 - 卡片式
        config_card = tk.Frame(main_container, bg='white', bd=1, relief='solid')
        config_card.pack(fill=tk.X, pady=(0, 10))
        
        # 测试配置标题
        config_header = tk.Frame(config_card, bg='#f8f9fa', height=35)
        config_header.pack(fill=tk.X)
        config_header.pack_propagate(False)
        
        tk.Label(config_header, text="⚙️ 测试配置", font=('Microsoft YaHei', 11, 'bold'),
                bg='#f8f9fa', fg='#333').pack(side=tk.LEFT, padx=12, pady=8)
        
        # 配置内容
        config_content = tk.Frame(config_card, bg='white', padx=12, pady=10)
        config_content.pack(fill=tk.X)
        
        # 测试提示词
        tk.Label(config_content, text="测试提示词", font=('Microsoft YaHei', 10),
                bg='white', fg='#333').pack(anchor=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(config_content, height=4, wrap=tk.WORD, 
                                   font=('Microsoft YaHei', 10),
                                   bg='white', fg='#333',
                                   relief='solid', bd=1)
        self.prompt_text.pack(fill=tk.X, pady=(0, 15))
        
        # Temperature 和 Max Tokens 并排
        params_frame = tk.Frame(config_content, bg='white')
        params_frame.pack(fill=tk.X)
        
        # Temperature
        temp_frame = tk.Frame(params_frame, bg='white')
        temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(temp_frame, text="Temperature", font=('Microsoft YaHei', 10),
                bg='white', fg='#333').pack(anchor=tk.W, pady=(0, 5))
        
        self.temperature_var = tk.StringVar(value=str(self.settings.get("temperature", 0.7)))
        temp_entry = tk.Entry(temp_frame, textvariable=self.temperature_var,
                             font=('Microsoft YaHei', 10), width=15,
                             relief='solid', bd=1)
        temp_entry.pack(anchor=tk.W)
        
        # Max Tokens
        max_tokens_frame = tk.Frame(params_frame, bg='white')
        max_tokens_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(max_tokens_frame, text="Max Tokens", font=('Microsoft YaHei', 10),
                bg='white', fg='#333').pack(anchor=tk.W, pady=(0, 5))
        
        self.max_tokens_var = tk.StringVar(value=str(self.settings.get("max_tokens", 2048)))
        max_tokens_entry = tk.Entry(max_tokens_frame, textvariable=self.max_tokens_var,
                                     font=('Microsoft YaHei', 10), width=15,
                                     relief='solid', bd=1)
        max_tokens_entry.pack(anchor=tk.W)
        
        # 操作控制区域 - 卡片式
        control_card = tk.Frame(main_container, bg='white', bd=1, relief='solid')
        control_card.pack(fill=tk.X, pady=(0, 10))
        
        # 操作控制标题
        control_header = tk.Frame(control_card, bg='#f8f9fa', height=35)
        control_header.pack(fill=tk.X)
        control_header.pack_propagate(False)
        
        tk.Label(control_header, text="🎮 操作控制", font=('Microsoft YaHei', 11, 'bold'),
                bg='#f8f9fa', fg='#333').pack(side=tk.LEFT, padx=12, pady=8)
        
        # 操作按钮区域
        control_content = tk.Frame(control_card, bg='white', padx=12, pady=10)
        control_content.pack(fill=tk.X)
        
        btn_row = tk.Frame(control_content, bg='white')
        btn_row.pack(fill=tk.X)
        
        # 开始测试按钮（绿色）
        self.start_btn = tk.Button(btn_row, text="▶️ 开始测试", command=self._start_test,
                                  bg='#4CAF50', fg='white', font=('Microsoft YaHei', 10, 'bold'),
                                  relief='flat', padx=20, pady=8, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止测试按钮（红色）
        self.stop_btn = tk.Button(btn_row, text="⏹️ 停止测试", command=self._stop_test,
                                 bg='#f44336', fg='white', font=('Microsoft YaHei', 10, 'bold'),
                                 relief='flat', padx=20, pady=8, cursor='hand2',
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # 导出结果按钮（橙色）
        export_result_btn = tk.Button(btn_row, text="📊 导出结果", command=self._export_results,
                                     bg='#FF9800', fg='white', font=('Microsoft YaHei', 10, 'bold'),
                                     relief='flat', padx=20, pady=8, cursor='hand2')
        export_result_btn.pack(side=tk.LEFT, padx=10)
        
        # 进度条区域
        progress_frame = tk.Frame(control_content, bg='white')
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = tk.Label(progress_frame, text="", font=('Microsoft YaHei', 9),
                                     bg='white', fg='#666')
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 测试结果区域 - 卡片式
        result_card = tk.Frame(main_container, bg='white', bd=1, relief='solid')
        result_card.pack(fill=tk.BOTH, expand=True)
        
        # 测试结果标题
        result_header = tk.Frame(result_card, bg='#f8f9fa', height=35)
        result_header.pack(fill=tk.X)
        result_header.pack_propagate(False)
        
        tk.Label(result_header, text="📊 测试结果", font=('Microsoft YaHei', 11, 'bold'),
                bg='#f8f9fa', fg='#333').pack(side=tk.LEFT, padx=12, pady=8)
        
        # 测试完成标签（初始隐藏）
        self.complete_label = tk.Label(result_header, text="测试完成", font=('Microsoft YaHei', 9),
                                        bg='#4CAF50', fg='white', padx=8, pady=2)
        self.complete_label.pack(side=tk.RIGHT, padx=12, pady=8)
        self.complete_label.pack_forget()
        
        # 结果内容
        result_content = tk.Frame(result_card, bg='white', padx=12, pady=10)
        result_content.pack(fill=tk.BOTH, expand=True)
        
        # 结果表格 - 增加高度以显示至少4个模型
        columns = ("model_name", "status", "first_token", "total_time", "token_count", "speed")
        self.result_tree = ttk.Treeview(result_content, columns=columns, show='headings', height=8)
        
        self.result_tree.heading("model_name", text="模型名称")
        self.result_tree.heading("status", text="状态")
        self.result_tree.heading("first_token", text="首次Token(s)")
        self.result_tree.heading("total_time", text="总用时(s)")
        self.result_tree.heading("token_count", text="Token数")
        self.result_tree.heading("speed", text="速度(T/s)")
        
        self.result_tree.column("model_name", width=150, anchor='w')
        self.result_tree.column("status", width=80, anchor='center')
        self.result_tree.column("first_token", width=100, anchor='center')
        self.result_tree.column("total_time", width=90, anchor='center')
        self.result_tree.column("token_count", width=80, anchor='center')
        self.result_tree.column("speed", width=100, anchor='center')
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # 设置表格样式
        style = ttk.Style()
        style.configure('Treeview', font=('Microsoft YaHei', 9), rowheight=30)
        style.configure('Treeview.Heading', font=('Microsoft YaHei', 10, 'bold'))
        style.configure('Treeview', background='white', fieldbackground='white')
    
    def _load_initial_data(self):
        self._refresh_model_list()
        self.prompt_text.insert(tk.END, self.settings.get("default_prompt", ""))
    
    def _refresh_model_list(self):
        for widget in self.model_frame.winfo_children():
            widget.destroy()
        
        self.selected_models.clear()
        
        for i, model in enumerate(self.models):
            model_name = model.get("name", "")
            var = tk.BooleanVar(value=True)
            self.selected_models[model_name] = var
            
            # 极简模型选择 - 只显示复选框和名称
            cb = tk.Checkbutton(self.model_frame, text=model_name, variable=var,
                               bg='white', font=('Microsoft YaHei', 11),
                               activebackground='white', selectcolor='white')
            cb.pack(side=tk.LEFT, padx=(0, 20), pady=5)
    
    def _get_selected_models(self) -> List[Dict]:
        selected = []
        for model in self.models:
            model_name = model.get("name", "")
            if self.selected_models.get(model_name, tk.BooleanVar()).get():
                selected.append(model)
        return selected
    
    def _add_model(self):
        dialog = ModelDialog(self.root, "添加模型")
        if dialog.result:
            self.config_manager.add_model(dialog.result)
            self.models = self.config_manager.load_models()
            self._refresh_model_list()
            messagebox.showinfo("成功", "模型添加成功！")
    
    def _edit_model(self):
        if not self.models:
            messagebox.showwarning("提示", "没有可编辑的模型")
            return
        
        dialog = ModelDialog(self.root, "编辑模型", model_list=self.models)
        if dialog.result:
            old_name = dialog.selected_model_name
            self.config_manager.update_model(old_name, dialog.result)
            self.models = self.config_manager.load_models()
            self._refresh_model_list()
            messagebox.showinfo("成功", "模型更新成功！")
    
    def _delete_model(self):
        selected_models = self._get_selected_models()
        if not selected_models:
            messagebox.showwarning("提示", "请选择要删除的模型")
            return
        
        model_names = [m.get("name", "") for m in selected_models]
        if messagebox.askyesno("确认", f"确定要删除以下模型吗？\n{', '.join(model_names)}"):
            for name in model_names:
                self.config_manager.delete_model(name)
            self.models = self.config_manager.load_models()
            self._refresh_model_list()
            messagebox.showinfo("成功", "模型删除成功！")
    
    def _import_config(self):
        filepath = filedialog.askopenfilename(
            title="导入模型配置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                self.config_manager.import_models(filepath)
                self.models = self.config_manager.load_models()
                self._refresh_model_list()
                messagebox.showinfo("成功", "配置导入成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def _export_config(self):
        filepath = filedialog.asksaveasfilename(
            title="导出模型配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )
        if filepath:
            try:
                self.config_manager.export_models(filepath)
                messagebox.showinfo("成功", "配置导出成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def _start_test(self):
        selected_models = self._get_selected_models()
        if not selected_models:
            messagebox.showwarning("提示", "请选择要测试的模型")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("提示", "请输入测试提示词")
            return
        
        # 清空之前的结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.complete_label.pack_forget()
        
        self.test_results = []
        self.is_testing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.progress_bar['maximum'] = len(selected_models)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="正在测试...")
        
        def test_thread():
            results = self.speed_tester.test_models(
                selected_models,
                prompt,
                self._update_progress
            )
            self.test_results = results
            self._on_test_complete()
        
        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()
    
    def _update_progress(self, current: int, total: int, result: Dict):
        self.root.after(0, lambda: self._do_update_progress(current, total, result))
    
    def _do_update_progress(self, current: int, total: int, result: Dict):
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"已完成: {current}/{total}")
        
        # 添加结果到表格
        status_text = "✓ 成功" if result.get("success", False) else "✗ 失败"
        speed_value = result.get("speed", 0)
        speed_text = f"{speed_value:.2f}/s"
        
        # 根据速度设置颜色标签
        if speed_value >= 100:
            speed_color = "green"
        elif speed_value >= 50:
            speed_color = "orange"
        else:
            speed_color = "red"
        
        self.result_tree.insert("", tk.END, values=(
            result.get("model_name", ""),
            status_text,
            f"{result.get('first_token_time', 0):.2f}s",
            f"{result.get('total_time', 0):.2f}s",
            result.get("token_count", 0),
            speed_text
        ))
    
    def _stop_test(self):
        self.speed_tester.stop_test()
        self.progress_label.config(text="测试已停止")
    
    def _on_test_complete(self):
        self.root.after(0, self._do_on_test_complete)
    
    def _do_on_test_complete(self):
        self.is_testing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="测试完成")
        self.complete_label.pack(side=tk.RIGHT, padx=12, pady=8)
        
        success_count = sum(1 for r in self.test_results if r.get("success", False))
        messagebox.showinfo("完成", f"测试完成！\n成功: {success_count}/{len(self.test_results)}")
    
    def _export_results(self):
        if not self.test_results:
            messagebox.showwarning("提示", "没有测试结果可导出")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="导出测试结果",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("CSV文件", "*.csv")]
        )
        if filepath:
            try:
                if filepath.endswith('.csv'):
                    self.speed_tester.export_results_csv(self.test_results, filepath)
                else:
                    self.speed_tester.save_results(self.test_results, filepath)
                messagebox.showinfo("成功", f"结果已导出到: {filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")