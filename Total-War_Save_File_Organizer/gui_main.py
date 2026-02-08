import os
import ctypes
import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from mapping_data import TRANSLATIONS
from save_reader import SaveMetadataReader
from save_cleaner import SaveCleanerLogic

def format_size(size_bytes):
    if size_bytes == 0: return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units)-1:
        size_bytes /= 1024; i += 1
    return f"{size_bytes:.2f} {units[i]}"

class SaveManagerGUI:
    """토탈워 세이브 매니저의 메인 UI 클래스입니다. [v3.3.7 Threaded]"""
    def __init__(self, root):
        self.root = root
        self.lang = "KOR"
        self.logic = SaveCleanerLogic()
        self.is_working = False
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        t = TRANSLATIONS[self.lang]
        self.root.title(t["title"] + " (v3.4.0 Final Isolation)")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f0f0")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 상단 헤더
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(header_frame, text=t["title"], font=("Helvetica", 16, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        self.lang_btn = ttk.Button(header_frame, text=t["lang_switch"], command=self.toggle_language)
        self.lang_btn.pack(side=tk.RIGHT)

        # 좌측: 게임 목록 및 버튼
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        list_frame = ttk.LabelFrame(left_panel, text=t["label_detected"], padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.game_list = ttk.Treeview(list_frame, columns=("path", "count"), show="headings")
        self.game_list.heading("path", text="Game / Path")
        self.game_list.heading("count", text="Saves")
        self.game_list.column("path", width=400)
        self.game_list.column("count", width=60, anchor=tk.CENTER)
        self.game_list.pack(fill=tk.BOTH, expand=True)
        self.game_list.bind("<<TreeviewSelect>>", self.on_game_select)
        
        btn_frame = ttk.Frame(left_panel, padding="5")
        btn_frame.pack(fill=tk.X)
        
        self.add_btn = ttk.Button(btn_frame, text=t["btn_add_folder"], command=self.add_folder)
        self.add_btn.pack(side=tk.LEFT, padx=2)
        
        self.clean_btn = ttk.Button(btn_frame, text=t["btn_start_clean"], command=self.start_cleaning)
        self.clean_btn.pack(side=tk.LEFT, padx=2)
        
        self.camp_btn = ttk.Button(btn_frame, text=t["btn_campaign_clean"], command=self.start_campaign_cleaning)
        self.camp_btn.pack(side=tk.LEFT, padx=2)
        
        # 우측: 상세 정보
        right_panel = ttk.Frame(main_frame, width=450)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        details_frame = ttk.LabelFrame(right_panel, text=t["label_details"], padding="5")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_list = ttk.Treeview(details_frame, columns=("name", "faction", "leader"), show="headings")
        self.file_list.heading("name", text="File Name")
        self.file_list.heading("faction", text="Faction")
        self.file_list.heading("leader", text="Leader")
        self.file_list.column("name", width=200)
        self.file_list.column("faction", width=100)
        self.file_list.column("leader", width=100)
        self.file_list.pack(fill=tk.BOTH, expand=True)
        
        # 하단 상태창 및 진행바
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def set_status(self, msg, progress=None):
        self.status_var.set(msg)
        if progress is not None:
            self.progress['value'] = progress
        self.root.update_idletasks()

    def refresh_list(self):
        if self.is_working: return
        self.game_list.delete(*self.game_list.get_children())
        for g in self.logic.scan_games():
            self.game_list.insert("", tk.END, values=(g["name"], g["count"]), tags=(g["path"],))

    def on_game_select(self, event):
        if self.is_working: return
        sel = self.game_list.selection()
        if not sel: return
        
        path = self.game_list.item(sel[0], "tags")[0]
        game_display_name = os.path.basename(os.path.dirname(path))
        self.set_status(f"Loading files from {game_display_name}...", 0)
        
        def task():
            self.is_working = True
            def progress_cb(current, total):
                percent = (current / total) * 100
                self.root.after(0, lambda: self.set_status(f"Loading {game_display_name} ({current}/{total})...", percent))
            
            files = self.logic.get_save_files_details(path, progress_callback=progress_cb)
            self.root.after(0, lambda: self.update_file_list(files))
            
        threading.Thread(target=task, daemon=True).start()

    def update_file_list(self, files):
        self.file_list.delete(*self.file_list.get_children())
        for f in files:
            self.file_list.insert("", tk.END, values=(f["name"], f["faction"], f["leader"]))
        self.is_working = False
        self.set_status("Ready", 0)

    def toggle_language(self):
        self.lang = "ENG" if self.lang == "KOR" else "KOR"
        self.update_texts()

    def update_texts(self):
        t = TRANSLATIONS[self.lang]
        self.root.title(t["title"] + " (v3.4.0 Final Isolation)")
        self.title_label.config(text=t["title"])
        self.add_btn.config(text=t["btn_add_folder"])
        self.clean_btn.config(text=t["btn_start_clean"])
        self.camp_btn.config(text=t["btn_campaign_clean"])
        self.lang_btn.config(text=t["lang_switch"])

    def add_folder(self):
        t = TRANSLATIONS[self.lang]
        folder = filedialog.askdirectory(title=t["dialog_add_title"])
        if folder:
            self.logic.search_paths.append(folder)
            self.refresh_list()
            messagebox.showinfo(t["msg_done_title"], t["msg_added"].format(folder))

    def start_cleaning(self):
        self._generic_clean_threaded(self.logic.clean_duplicates)

    def start_campaign_cleaning(self):
        self._generic_clean_threaded(self.logic.clean_campaign_history)

    def _generic_clean_threaded(self, method):
        t = TRANSLATIONS[self.lang]
        sel = self.game_list.selection()
        if not sel:
            messagebox.showwarning(t["msg_done_title"], t["msg_warning_no_selection"])
            return
            
        game_name = self.game_list.item(sel[0])["values"][0]
        game_path = self.game_list.item(sel[0], "tags")[0]
        
        if not messagebox.askyesno(t["msg_done_title"], t["msg_confirm_clean"].format(game_name)):
            return

        def task():
            self.is_working = True
            try:
                def progress_cb(current, total):
                    percent = (current / total) * 100
                    self.root.after(0, lambda: self.set_status(f"Processing ({current}/{total})...", percent))
                
                res = method(game_path, progress_callback=progress_cb)
                self.root.after(0, lambda: self.finish_cleaning(game_name, res))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(t["msg_done_title"], t["msg_error"].format(str(e))))
                self.is_working = False
                self.set_status("Error", 0)

        threading.Thread(target=task, daemon=True).start()

    def finish_cleaning(self, game_name, res):
        t = TRANSLATIONS[self.lang]
        messagebox.showinfo(t["msg_done_title"], t["msg_done_body"].format(
            game_name, res[0], format_size(res[1]), res[2], format_size(res[3]), res[4], format_size(res[1]-res[3])
        ))
        self.is_working = False
        self.refresh_list()
        self.set_status("Ready", 0)
