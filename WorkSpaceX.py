import sys
import traceback 
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, font as tkfont
from tkinter import ttk
import os
import json
import webbrowser
import re 
from datetime import datetime

import win32api
import win32gui
import win32ui
import win32con
from PIL import Image, ImageTk

# 高分屏 (High DPI) 清晰度修复
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class WorkSpaceX(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 全局防崩溃黑匣子系统
        self.report_callback_exception = self.handle_tk_exception
        sys.excepthook = self.handle_global_exception
        
        self.title("WorkSpace X - 你的专属工作空间")
        
        # 调整为更大的 1280x720 (16:9) 默认尺寸
        window_width = 1280
        window_height = 720
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.items = [] 
        self.view_mode = "list"
        self.show_full_path = False 
        self.photo_images = []
        self.current_columns = 0 
        self.tk_custom_icon = None 
        
        self._resize_job = None
        self._scale_job = None
        self.grid_size = 160  

        self.data_dir = os.path.join(os.getcwd(), "data")
        self.profiles_dir = os.path.join(self.data_dir, "profiles")
        self.global_config_path = os.path.join(self.data_dir, "global_config.json")
        os.makedirs(self.profiles_dir, exist_ok=True)

        # 稍微加宽初始侧栏比例以适配更大的窗口
        self.left_panel_width = 260  
        self.right_panel_width = 280 
        
        if os.path.exists(self.global_config_path):
            try:
                with open(self.global_config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.left_panel_width = data.get("left_panel_width", 260)
                    self.right_panel_width = data.get("right_panel_width", 280)
                    self.grid_size = data.get("grid_size", 160)
            except Exception: pass

        self.load_custom_icon()
        self.initUI()
        self.load_global_config() 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def write_crash_log(self, error_msg):
        log_file = os.path.join(os.getcwd(), "crash_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] FATAL CRASH REPORT:\n{error_msg}\n{'-'*60}\n")
            return log_file
        except:
            return None

    def handle_tk_exception(self, exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_file = self.write_crash_log(error_msg)
        messagebox.showerror("软件发生异常", f"WorkSpace X 遇到了一个错误，但已被拦截。\n\n错误信息已保存至：\n{log_file}\n\n简述: {exc_value}")

    def handle_global_exception(self, exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.write_crash_log(error_msg)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def load_custom_icon(self):
        ico_path = os.path.join(self.data_dir, "icon.ico")
        png_path = os.path.join(self.data_dir, "icon.png")
        try:
            if os.path.exists(ico_path): self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                img = Image.open(png_path)
                self.tk_custom_icon = ImageTk.PhotoImage(img)
                self.iconphoto(False, self.tk_custom_icon)
        except Exception: pass

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)

    def initUI(self):
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("微软雅黑", 11), rowheight=28)
        
        bottom_bar = tk.Frame(self, pady=10)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=15)
        btn_launch = tk.Button(bottom_bar, text="🚀 一键启动 WorkSpace", bg="#0078D7", fg="white", 
                               font=("微软雅黑", 14, "bold"), command=self.launch_apps, height=2, cursor="hand2")
        btn_launch.pack(fill=tk.X)

        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.left_panel = tk.Frame(self.main_paned, width=self.left_panel_width)
        self.left_panel.pack_propagate(False) 
        self.main_paned.add(self.left_panel, weight=0)
        
        tk.Label(self.left_panel, text="📋 运行日志", font=("微软雅黑", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.log_text = tk.Text(self.left_panel, state=tk.DISABLED, bg="#F5F5F5", font=("Consolas", 10), wrap=tk.WORD)
        log_scroll = ttk.Scrollbar(self.left_panel, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text.tag_config("info", foreground="#333333")
        self.log_text.tag_config("success", foreground="#2E7D32", font=("Consolas", 10, "bold")) 
        self.log_text.tag_config("error", foreground="#D32F2F", font=("Consolas", 10, "bold"))   
        self.log_text.tag_config("warning", foreground="#F57C00") 
        self.log_text.tag_config("flash", foreground="#673AB7", font=("Consolas", 10, "bold")) 

        mid_panel = tk.Frame(self.main_paned)
        self.main_paned.add(mid_panel, weight=1)

        top_control_area = tk.Frame(mid_panel, bg="#f0f0f0")
        top_control_area.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))

        row1 = tk.Frame(top_control_area, bg="#f0f0f0")
        row1.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # 修改了按钮名称：添加文件
        self.btn_add_file = tk.Button(row1, text="➕ 添加文件", command=self.add_file, height=2, bg="#E1F5FE", relief=tk.GROOVE)
        self.btn_add_file.pack(side=tk.LEFT, padx=(5, 5))
        self.btn_add_path = tk.Button(row1, text="🔗 添加地址", command=self.show_add_address_dialog, height=2, bg="#E8F5E9", relief=tk.GROOVE)
        self.btn_add_path.pack(side=tk.LEFT, padx=5)
        self.var_select_all = tk.IntVar(value=0)
        self.chk_select_all = ttk.Checkbutton(row1, text="全选", variable=self.var_select_all, command=self.on_select_all_clicked)
        self.chk_select_all.pack(side=tk.LEFT, padx=(5, 5))
        self.btn_delete = tk.Button(row1, text="🗑️ 删除选中", command=self.delete_selected, fg="#D32F2F", bg="#f0f0f0", relief=tk.FLAT, cursor="hand2")
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.btn_toggle_view = tk.Button(row1, text="🔄 视图", command=self.toggle_view, height=2, bg="#FFF3E0", relief=tk.GROOVE)
        self.btn_toggle_view.pack(side=tk.RIGHT, padx=5)
        self.btn_toggle_path = tk.Button(row1, text="🔤 显示: 仅名称", command=self.toggle_path_display, height=2, bg="#F3E5F5", relief=tk.GROOVE)
        self.btn_toggle_path.pack(side=tk.RIGHT, padx=5)

        self.row2 = tk.Frame(top_control_area, bg="#f0f0f0")
        self.row2.pack(side=tk.TOP, fill=tk.X, pady=(5, 5))

        self.lbl_scale = tk.Label(self.row2, text="🔍 缩略图大小调节:", bg="#f0f0f0", font=("微软雅黑", 9))
        self.lbl_scale.pack(side=tk.LEFT, padx=(10, 5))

        self.scale_var = tk.DoubleVar(value=self.grid_size)
        self.scale_icon_size = ttk.Scale(self.row2, from_=60, to=240, orient=tk.HORIZONTAL, variable=self.scale_var, command=self.on_scale_drag)
        self.scale_icon_size.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        list_frame = tk.Frame(mid_panel, bd=1, relief=tk.SUNKEN, bg="white")
        list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(list_frame, borderwidth=0, highlightthickness=0, bg="white")
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)

        self.right_panel = tk.Frame(self.main_paned, width=self.right_panel_width)
        self.right_panel.pack_propagate(False)
        self.main_paned.add(self.right_panel, weight=0)
        
        tk.Label(self.right_panel, text="📂 模式预设", font=("微软雅黑", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        mode_op_frame = tk.Frame(self.right_panel)
        mode_op_frame.pack(fill=tk.X, pady=(0, 5))
        self.entry_mode_name = ttk.Entry(mode_op_frame)
        self.entry_mode_name.insert(0, "Unnamed")
        self.entry_mode_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        btn_save_mode = tk.Button(mode_op_frame, text="保存", command=self.save_current_as_profile, bg="#4CAF50", fg="white", relief=tk.FLAT)
        btn_save_mode.pack(side=tk.RIGHT)

        btn_delete_mode = tk.Button(self.right_panel, text="🗑️ 删除选中模式", command=self.delete_selected_profile, 
                                    bg="#D32F2F", fg="white", font=("微软雅黑", 10, "bold"), height=1, cursor="hand2")
        btn_delete_mode.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        tree_frame = tk.Frame(self.right_panel)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_yscroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_profiles = ttk.Treeview(tree_frame, show="tree", selectmode="browse", style="Custom.Treeview")
        self.tree_profiles.config(yscrollcommand=tree_yscroll.set, xscrollcommand=tree_xscroll.set)
        self.tree_profiles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_yscroll.config(command=self.tree_profiles.yview)
        tree_xscroll.config(command=self.tree_profiles.xview)
        
        self.tree_profiles.bind("<ButtonRelease-1>", self.on_tree_click)

    def on_tree_click(self, event):
        element = self.tree_profiles.identify_element(event.x, event.y)
        if element == "indicator": return
            
        item_id = self.tree_profiles.identify_row(event.y)
        if item_id:
            self.tree_profiles.selection_set(item_id)
            self.apply_selected_profile()

    def on_scale_drag(self, val):
        self.grid_size = float(val)
        if self._scale_job is not None:
            self.after_cancel(self._scale_job)
        self._scale_job = self.after(100, lambda: self.render_view(reset_scroll=False))

    def on_canvas_resize(self, event):
        if self.view_mode == "grid":
            item_width = int(self.grid_size) + 20
            columns = max(1, event.width // item_width)
            if columns != self.current_columns:
                self.current_columns = columns
                frames = self.scrollable_frame.winfo_children()
                for index, frame in enumerate(frames): 
                    frame.grid(row=index // columns, column=index % columns, padx=10, pady=10)

    def show_context_menu(self, event, item):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="📝 修改备注", command=lambda: self.after(50, lambda: self.rename_item(item)))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
            self.after(200, menu.destroy)

    def rename_item(self, item):
        new_name = simpledialog.askstring("修改备注", "请输入新的显示名称：", initialvalue=item["name"])
        if new_name and new_name.strip():
            old_name = item["name"]
            item["name"] = new_name.strip()
            self.render_view(reset_scroll=False)
            self.refresh_profile_list() 
            self.log(f"📝 备注修改: '{old_name}' -> '{item['name']}'")

    def log(self, message, force_tag=None):
        self.log_text.config(state=tk.NORMAL)
        time_str = datetime.now().strftime("%H:%M:%S")
        tag = force_tag if force_tag else "info"
        if not force_tag:
            if "❌" in message: tag = "error"
            elif "⚠️" in message: tag = "warning"
            elif any(icon in message for icon in ["✅", "💾", "🎉", "➕", "🚀", "📝"]): tag = "success"
        self.log_text.insert(tk.END, f"[{time_str}] {message}\n", tag)
        self.log_text.see(tk.END) 
        self.log_text.config(state=tk.DISABLED)

    def toggle_item_selection(self, item):
        current_state = item["var"].get()
        item["var"].set(0 if current_state == 1 else 1)
        self.check_select_all_state()

    def quick_launch(self, item):
        current_state = item["var"].get()
        item["var"].set(0 if current_state == 1 else 1)
        self.check_select_all_state()

        path = item["path"]
        try:
            if item["type"] == "url": webbrowser.open(path)
            else: os.startfile(path) 
            self.log(f"⚡ 闪电启动 -> {item['name']}", "flash")
        except Exception as e:
            self.log(f"❌ 启动失败 -> {item['name']}: {e}", "error")

    def show_add_address_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("添加地址")
        dialog.geometry("450x180")
        dialog.resizable(False, False)
        dialog.transient(self) 
        dialog.grab_set()      

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text="请输入网址、文件或文件夹绝对路径:", font=("微软雅黑", 11)).pack(pady=(20, 10))
        entry = ttk.Entry(dialog, font=("微软雅黑", 11))
        entry.pack(fill=tk.X, padx=30, ipady=4)
        entry.focus()

        def on_confirm(*args):
            path = entry.get().strip()
            dialog.destroy()
            if path:
                self.process_add_address(path)

        btn = tk.Button(dialog, text="确定", command=on_confirm, bg="#4CAF50", fg="white", font=("微软雅黑", 11), width=10, cursor="hand2")
        btn.pack(pady=15)
        dialog.bind("<Return>", on_confirm)

    def process_add_address(self, path):
        name = os.path.basename(path) if os.path.basename(path) else path
        url_pattern = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(/.*)?$|^(localhost|(\d{1,3}\.){3}\d{1,3})(:\d+)?(/.*)?$')
        
        is_url = False
        if path.startswith('http://') or path.startswith('https://'): is_url = True
        elif path.startswith('www.') or url_pattern.match(path):
            path = 'http://' + path 
            is_url = True

        if is_url:
            clean_name = re.sub(r'^https?://(www\.)?', '', path).split('/')[0]
            self.add_to_data(clean_name, path, "url", None)
        elif os.path.exists(path):
            if os.path.isdir(path): self.add_to_data(name, path, "folder", None)
            else:
                icon = self.get_exe_icon(path) if path.lower().endswith('.exe') else None
                self.add_to_data(name, path, "exe" if path.lower().endswith('.exe') else "file", icon)
        else: self.log(f"❌ 添加失败：无法识别路径 {path}")

    def add_to_data(self, name, path, item_type, icon):
        if any(item["path"] == path for item in self.items):
            self.log(f"⚠️ {name} 已在列表中，切勿重复添加。")
            return
        self.items.append({"name": name, "path": path, "type": item_type, "var": tk.IntVar(value=1), "icon": icon})
        self.render_view(reset_scroll=False)
        self.check_select_all_state()
        self.log(f"➕ 成功添加: {name}")

    def draw_list_item(self, item):
        frame = tk.Frame(self.scrollable_frame, bg="white")
        frame.pack(fill=tk.X, expand=True, pady=5, padx=10)
        
        chk = tk.Checkbutton(frame, text="", variable=item["var"], bg="white", command=self.check_select_all_state)
        chk.pack(side=tk.LEFT, padx=(10, 5))

        if item["icon"]:
            tk_img = ImageTk.PhotoImage(item["icon"])
            self.photo_images.append(tk_img)
            lbl_icon = tk.Label(frame, image=tk_img, bg="white")
        else: lbl_icon = self.create_fallback_icon(frame, item["type"], "small")
        lbl_icon.pack(side=tk.LEFT, padx=(0, 10))

        display_text = item["path"] if self.show_full_path else item["name"]
        lbl_text = tk.Label(frame, text=display_text, font=("微软雅黑", 10), bg="white", anchor="w")
        lbl_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        for widget in (frame, lbl_icon, lbl_text):
            widget.bind("<Button-1>", lambda e, i=item: self.toggle_item_selection(i))
            widget.bind("<Double-Button-1>", lambda e, i=item: self.quick_launch(i))
            widget.bind("<Button-3>", lambda e, i=item: self.show_context_menu(e, i))
            widget.config(cursor="hand2")
            self._bind_mousewheel(widget) 
        
        self._bind_mousewheel(chk)

    def draw_grid_item(self, item, row, col):
        size = int(self.grid_size)
        frame = tk.Frame(self.scrollable_frame, width=size, height=size, bg="white", bd=1, relief=tk.RIDGE)
        frame.grid(row=row, column=col, padx=10, pady=10)
        frame.pack_propagate(False) 

        max_chars = max(6, int((size - 10) / 7.5))
        display_text = item["path"] if self.show_full_path else item["name"]
        
        if self.show_full_path and len(display_text) > max_chars:
            display_text = "..." + display_text[-(max_chars-3):] 
        elif not self.show_full_path and len(display_text) > max_chars: 
            display_text = display_text[:(max_chars-3)] + "..."   

        lbl_text = tk.Label(frame, text=display_text, font=("微软雅黑", 9), bg="white", justify="center")
        lbl_text.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))

        if item["icon"]:
            icon_size = max(16, int(size * 0.55))  
            resized_img = item["icon"].resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(resized_img)
            self.photo_images.append(tk_img)
            lbl_icon = tk.Label(frame, image=tk_img, bg="white")
        else: lbl_icon = self.create_fallback_icon(frame, item["type"], "large", size)
            
        lbl_icon.pack(side=tk.TOP, expand=True) 
        
        chk = tk.Checkbutton(frame, text="", variable=item["var"], bg="white", command=self.check_select_all_state)
        chk.place(relx=1.0, rely=1.0, anchor="se")

        for widget in (frame, lbl_text, lbl_icon):
            widget.bind("<Button-1>", lambda e, i=item: self.toggle_item_selection(i))
            widget.bind("<Double-Button-1>", lambda e, i=item: self.quick_launch(i))
            widget.bind("<Button-3>", lambda e, i=item: self.show_context_menu(e, i))
            widget.config(cursor="hand2")
            self._bind_mousewheel(widget)

    def save_current_as_profile(self):
        raw_name = self.entry_mode_name.get().strip()
        name = re.sub(r'[\\/*?:"<>|]', "", raw_name)
        if not name: name = "Unnamed"
        if name != raw_name:
            self.log("⚠️ 自动移除了模式名称中的非法字符。")
            self.entry_mode_name.delete(0, tk.END)
            self.entry_mode_name.insert(0, name)

        selected_paths = [item["path"] for item in self.items if item["var"].get() == 1]
        if not selected_paths:
            self.log("⚠️ 无法保存：请至少勾选一个应用！")
            return
            
        file_path = os.path.join(self.profiles_dir, f"{name}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(selected_paths, f, ensure_ascii=False, indent=4)
            self.log(f"💾 模式 '{name}' 已保存！")
            self.refresh_profile_list()
        except Exception as e: self.log(f"❌ 保存模式失败: {e}")

    def refresh_profile_list(self):
        for item in self.tree_profiles.get_children(): self.tree_profiles.delete(item)
        
        font_measure = tkfont.Font(family="微软雅黑", size=11)
        max_width = 250 
        path_to_name = {itm["path"]: itm["name"] for itm in self.items}

        for file in os.listdir(self.profiles_dir):
            if file.endswith(".json"):
                profile_name = file.replace(".json", "")
                file_path = os.path.join(self.profiles_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: paths = json.load(f)
                    parent = self.tree_profiles.insert("", tk.END, text=f"📁 {profile_name}", values=(file_path,))
                    
                    parent_w = font_measure.measure(f"📁 {profile_name}") + 60
                    max_width = max(max_width, parent_w)

                    for p in paths:
                        display_text = p if self.show_full_path else path_to_name.get(p, os.path.basename(p))
                        node_text = f"  - {display_text}"
                        
                        item_w = font_measure.measure(node_text) + 80
                        max_width = max(max_width, item_w)
                        
                        self.tree_profiles.insert(parent, tk.END, text=node_text)
                except: pass
        
        self.tree_profiles.column("#0", minwidth=max_width, width=max_width)

    def apply_selected_profile(self):
        selection = self.tree_profiles.selection()
        if not selection: return
        item_id = selection[0]
        parent_id = self.tree_profiles.parent(item_id)
        if parent_id: item_id = parent_id 
        values = self.tree_profiles.item(item_id, "values")
        if not values: return 
        
        file_path = values[0]
        profile_name = os.path.basename(file_path).replace(".json", "")
        self.entry_mode_name.delete(0, tk.END)
        self.entry_mode_name.insert(0, profile_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f: profile_paths = json.load(f)
            current_paths = []
            for item in self.items:
                current_paths.append(item["path"])
                item["var"].set(1 if item["path"] in profile_paths else 0)
            for p in profile_paths:
                if p not in current_paths: self.log(f"⚠️ {os.path.basename(p)} 不在列表中，已跳过。")
            self.check_select_all_state()
            self.log(f"✅ 已应用模式: {profile_name}")
        except Exception as e: self.log(f"❌ 加载模式失败: {e}")

    def delete_selected_profile(self):
        selection = self.tree_profiles.selection()
        if not selection: return
        item_id = selection[0]
        parent_id = self.tree_profiles.parent(item_id)
        if parent_id: item_id = parent_id
        values = self.tree_profiles.item(item_id, "values")
        if not values: return
            
        file_path = values[0]
        profile_name = os.path.basename(file_path).replace(".json", "")
        try:
            os.remove(file_path)
            self.log(f"🗑️ 模式 '{profile_name}' 已删除。")
            if self.entry_mode_name.get() == profile_name:
                self.entry_mode_name.delete(0, tk.END)
                self.entry_mode_name.insert(0, "Unnamed")
            self.refresh_profile_list()
        except Exception as e: self.log(f"❌ 删除失败: {e}")

    def save_global_config(self):
        left_w = self.left_panel.winfo_width()
        right_w = self.right_panel.winfo_width()
        
        data = {
            "view_mode": self.view_mode, 
            "show_full_path": self.show_full_path, 
            "left_panel_width": left_w if left_w > 50 else self.left_panel_width,
            "right_panel_width": right_w if right_w > 50 else self.right_panel_width,
            "grid_size": self.grid_size,  
            "items": []
        }
        for item in self.items:
            data["items"].append({"name": item["name"], "path": item["path"], "type": item["type"], "checked": item["var"].get()})
        try:
            with open(self.global_config_path, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception: pass

    def load_global_config(self):
        self.log("🚀 WorkSpace X 系统初始化...")
        if os.path.exists(self.global_config_path):
            try:
                with open(self.global_config_path, 'r', encoding='utf-8') as f: data = json.load(f)
                self.view_mode = data.get("view_mode", "list")
                self.show_full_path = data.get("show_full_path", False)
                self.btn_toggle_view.config(text=f"🔄 视图: {'缩略图' if self.view_mode == 'grid' else '列表'}")
                self.btn_toggle_path.config(text=f"🔤 显示: {'绝对路径' if self.show_full_path else '仅名称'}")
                
                if self.view_mode == "list": 
                    self.scale_icon_size.config(state=tk.DISABLED)
                    self.lbl_scale.config(fg="gray")
                
                loaded_items = data.get("items", [])
                for i_data in loaded_items:
                    path = i_data["path"]
                    icon = self.get_exe_icon(path) if i_data["type"] == "exe" and os.path.exists(path) else None
                    self.items.append({"name": i_data["name"], "path": path, "type": i_data["type"], "var": tk.IntVar(value=i_data.get("checked", 1)), "icon": icon})
                self.log(f"✅ 成功加载 {len(self.items)} 个历史应用。")
            except Exception as e: self.log(f"❌ 加载配置文件受损: {e}")
        
        self.render_view(reset_scroll=True)
        self.check_select_all_state()
        self.refresh_profile_list() 

    def on_closing(self):
        self.save_global_config()
        self.destroy()

    def get_exe_icon(self, exe_path):
        try:
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if not large: return None
            hicon = large[0]
            
            screen_dc = win32gui.GetDC(0)
            hdc = win32ui.CreateDCFromHandle(screen_dc)
            
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, 32, 32)
            memdc = hdc.CreateCompatibleDC()
            memdc.SelectObject(hbmp)
            
            brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255)) 
            win32gui.FillRect(memdc.GetSafeHdc(), (0, 0, 32, 32), brush)
            win32gui.DrawIconEx(memdc.GetSafeHdc(), 0, 0, hicon, 32, 32, 0, 0, win32con.DI_NORMAL)
            
            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            
            for icon in large: win32gui.DestroyIcon(icon)
            for icon in small: win32gui.DestroyIcon(icon)
            win32gui.DeleteObject(brush)
            memdc.DeleteDC()
            hdc.DeleteDC()
            win32gui.ReleaseDC(0, screen_dc) 
            win32gui.DeleteObject(hbmp.GetHandle())
            
            return img 
        except Exception: return None

    def on_select_all_clicked(self):
        state = self.var_select_all.get()
        for item in self.items: item["var"].set(state)

    def check_select_all_state(self):
        if not self.items:
            self.var_select_all.set(0)
            return
        self.var_select_all.set(1 if all(item["var"].get() == 1 for item in self.items) else 0)

    def delete_selected(self):
        to_keep = [item for item in self.items if item["var"].get() == 0]
        if len(to_keep) == len(self.items):
            self.log("⚠️ 没有选中任何应用，无法删除。")
            return
        deleted_count = len(self.items) - len(to_keep)
        self.items = to_keep
        self.render_view(reset_scroll=False)
        self.check_select_all_state()
        self.log(f"🗑️ 已移出 {deleted_count} 个应用。")

    def add_file(self):
        file_path = filedialog.askopenfilename(title="选择任意文件", filetypes=[("所有文件", "*.*"), ("可执行文件", "*.exe")])
        if file_path:
            name = os.path.basename(file_path)
            icon = self.get_exe_icon(file_path) if file_path.lower().endswith('.exe') else None
            self.add_to_data(name, file_path, "exe" if file_path.lower().endswith('.exe') else "file", icon)

    def toggle_view(self):
        self.view_mode = "grid" if self.view_mode == "list" else "list"
        self.btn_toggle_view.config(text=f"🔄 视图: {'缩略图' if self.view_mode == 'grid' else '列表'}")
        
        if self.view_mode == "grid": 
            self.scale_icon_size.config(state=tk.NORMAL)
            self.lbl_scale.config(fg="black")
        else: 
            self.scale_icon_size.config(state=tk.DISABLED)
            self.lbl_scale.config(fg="gray")
            
        self.render_view(reset_scroll=True)

    def toggle_path_display(self):
        self.show_full_path = not self.show_full_path
        self.btn_toggle_path.config(text=f"🔤 显示: {'绝对路径' if self.show_full_path else '仅名称'}")
        self.render_view(reset_scroll=False)
        self.refresh_profile_list() 

    def render_view(self, reset_scroll=False):
        current_y = self.canvas.yview() 
        
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.photo_images.clear() 

        if reset_scroll:
            self.canvas.yview_moveto(0)

        if self.view_mode == "list":
            for item in self.items: self.draw_list_item(item)
        else:
            self.canvas.update_idletasks()
            item_width = int(self.grid_size) + 20
            self.current_columns = max(1, self.canvas.winfo_width() // item_width)
            for index, item in enumerate(self.items): 
                self.draw_grid_item(item, index // self.current_columns, index % self.current_columns)
                
        self.canvas.update_idletasks()
        if not reset_scroll:
            self.canvas.yview_moveto(current_y[0]) 

    def create_fallback_icon(self, parent, item_type, size="large", frame_size=160):
        icons = {"url": "🌐", "folder": "📁", "file": "📄", "exe": "💻"}
        font_size = int(frame_size * 0.4) if size == "large" else 18
        return tk.Label(parent, text=icons.get(item_type, "❓"), font=("", font_size), bg="white")

    def launch_apps(self):
        self.log("-" * 30)
        self.log("🚀 开始一键构建环境...")
        launched_count = 0
        for item in self.items:
            if item["var"].get() == 1:
                path = item["path"]
                try:
                    if item["type"] == "url": webbrowser.open(path)
                    else: os.startfile(path) 
                    self.log(f"✅ 启动成功 -> {item['name']}")
                    launched_count += 1
                except Exception as e:
                    self.log(f"❌ 启动失败 -> {item['name']}: {e}")
        
        if launched_count > 0: self.log(f"🎉 汇报：已成功发送 {launched_count} 个启动请求！")
        else: self.log("⚠️ 汇报：当前未勾选任何应用。")

if __name__ == "__main__":
    app = WorkSpaceX()
    app.mainloop()