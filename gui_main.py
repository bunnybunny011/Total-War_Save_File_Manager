import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from mapping_data import TRANSLATIONS
from save_cleaner import SaveCleanerLogic
import time
from datetime import datetime

def format_size(size_bytes):
    if size_bytes == 0: return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(units)-1:
        size_bytes /= 1024; i += 1
    return f"{size_bytes:.2f} {units[i]}"

class SaveManagerGUI:
    """토탈워 세이브 매니저 [v15.0 Performance Edition]"""
    def __init__(self, root):
        self.root = root
        self.lang = "KOR"
        
        try:
            from save_manager_core import SaveManagerLogic
            self.logic = SaveManagerLogic()
        except ImportError:
            # Fallback logic
            class MinimalLogic:
                def __init__(self): self.search_paths = []
                def scan_games(self): return [] 
                def get_save_files_details(self, path, progress_callback=None, stop_check=None): return []
            self.logic = MinimalLogic()

        self.is_working = False
        self.current_task_id = 0 
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        t = TRANSLATIONS[self.lang]
        self.root.title(t["title"])
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f0f0")
        
        # ... (상단/좌측 패널 코드는 기존과 동일, 생략 없이 전체를 원하시면 말씀해주세요) ...
        # 여기서는 핵심 변경점인 '우측 패널' 부분만 수정하여 전체 코드를 구성합니다.
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(header_frame, text=t["title"], font=("Helvetica", 16, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        self.lang_btn = ttk.Button(header_frame, text=t["lang_switch"], command=self.toggle_language)
        self.lang_btn.pack(side=tk.RIGHT)

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
        
        self.clean_btn = ttk.Button(btn_frame, text=t["btn_start_clean"], command=self.on_smart_clean_click)
        self.clean_btn.pack(side=tk.LEFT, padx=2)
        
        self.camp_btn = ttk.Button(btn_frame, text=t["btn_campaign_clean"], command=self.on_ratio_clean_click)
        self.camp_btn.pack(side=tk.LEFT, padx=2)
        
        # === [우측 패널 변경] ===
        right_panel = ttk.Frame(main_frame, width=450)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        details_frame = ttk.LabelFrame(right_panel, text=t["label_details"], padding="5")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_frame = ttk.Frame(details_frame)
        tree_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 컬럼 변경: Faction/Leader -> Date/Size
        self.file_list = ttk.Treeview(tree_scroll_frame, columns=("name", "date", "size"), 
                                      show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_list.yview)
        
        self.file_list.heading("name", text="File Name")
        self.file_list.heading("date", text="Date Modified")
        self.file_list.heading("size", text="Size")
        
        self.file_list.column("name", width=250)
        self.file_list.column("date", width=120, anchor=tk.CENTER)
        self.file_list.column("size", width=80, anchor=tk.E)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # ... (get_current_folder, get_total_size, run_cleaning_task, clean 버튼 핸들러들은 동일) ...
    # 편의를 위해 여기에 핵심 메서드만 다시 적습니다. 기존 코드 그대로 쓰셔도 무방합니다.
    
    def get_current_folder(self):
        sel = self.game_list.selection()
        if not sel:
            messagebox.showwarning("Warning", "게임을 먼저 선택해주세요.")
            return None
        return self.game_list.item(sel[0], "tags")[0]

    def get_total_size(self, folder):
        total = 0
        try:
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.path.isfile(fp): total += os.path.getsize(fp)
        except: pass
        return total

    def run_cleaning_task(self, folder, game_name, method_func, mode_name):
        initial_total_size = self.get_total_size(folder)
        initial_size_str = format_size(initial_total_size)
        
        self.set_status(f"Calculating files in {game_name}...", 0)
        self.is_working = True
        
        def task():
            def progress_cb(current, total):
                percent = (current / total) * 100
                self.root.after(0, lambda: self.set_status(f"Analyzing {current}/{total} files...", percent))
            try:
                count, moved_list, backup_path, saved_size = method_func(folder, progress_callback=progress_cb)
                def on_complete():
                    self.is_working = False
                    self.set_status("Ready", 0)
                    saved_str = format_size(saved_size)
                    percent_saved = (saved_size / initial_total_size * 100) if initial_total_size > 0 else 0
                    msg = (f"[{mode_name}] 완료!\n\n"
                           f"■ 백업된 파일: {count}개\n"
                           f"■ 전체 용량: {initial_size_str}\n"
                           f"■ 백업된 용량: {saved_str} ({percent_saved:.1f}%)\n\n"
                           f"백업 폴더를 여시겠습니까?")
                    if count > 0:
                        if messagebox.askyesno("완료", msg): SaveCleanerLogic.open_folder(backup_path)
                    else:
                        messagebox.showinfo("완료", "정리할 파일이 없습니다.")
                    self.refresh_file_list(folder)
                self.root.after(0, on_complete)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("오류", str(e)))
                self.is_working = False
        threading.Thread(target=task, daemon=True).start()

    def on_smart_clean_click(self):
        folder = self.get_current_folder()
        if not folder: return
        game_name = os.path.basename(os.path.dirname(folder))
        if not messagebox.askyesno("확인", f"[{game_name}] 정리 시작?\n(중복 턴 파일은 '_Backup' 폴더로 이동됩니다)"): return
        self.run_cleaning_task(folder, game_name, SaveCleanerLogic.clean_duplicates_smart, "중복 정리")

    def on_ratio_clean_click(self):
        folder = self.get_current_folder()
        if not folder: return
        game_name = os.path.basename(os.path.dirname(folder))
        if not messagebox.askyesno("확인", f"[{game_name}] 정리 시작?\n(3:1 비율로 '_Backup' 폴더로 이동됩니다)"): return
        self.run_cleaning_task(folder, game_name, SaveCleanerLogic.clean_campaign_ratio, "비율 정리(3:1)")

    def refresh_file_list(self, folder_path=None):
        self.on_game_select(None)

    def set_status(self, msg, progress=None):
        self.status_var.set(msg)
        if progress is not None: self.progress['value'] = progress
        self.root.update_idletasks()

    def refresh_list(self):
        if self.is_working: return
        self.game_list.delete(*self.game_list.get_children())
        if hasattr(self.logic, 'scan_games'):
            for g in self.logic.scan_games():
                self.game_list.insert("", tk.END, values=(g["name"], g["count"]), tags=(g["path"],))

    def on_game_select(self, event):
        self.is_working = False 
        sel = self.game_list.selection()
        if not sel: return
        
        path = self.game_list.item(sel[0], "tags")[0]
        game_display_name = os.path.basename(os.path.dirname(path))
        self.set_status(f"Loading files from {game_display_name}...", 0)
        
        current_task_id = time.time()
        self.current_task_id = current_task_id
        
        def task():
            self.is_working = True
            def check_stop(): return self.current_task_id != current_task_id
            def progress_cb(current, total):
                if check_stop(): return
                percent = (current / total) * 100
                self.root.after(0, lambda: self.set_status(f"Loading {game_display_name} ({current}/{total})...", percent))
            
            if hasattr(self.logic, 'get_save_files_details'):
                files = self.logic.get_save_files_details(path, progress_callback=progress_cb, stop_check=check_stop)
                if check_stop(): return 
                self.root.after(0, lambda: self.update_file_list(files))
            else:
                 self.root.after(0, lambda: self.set_status("Logic Error: get_save_files_details not found", 0))

        threading.Thread(target=task, daemon=True).start()

    def update_file_list(self, files):
        self.file_list.delete(*self.file_list.get_children())
        if not files:
            self.set_status("No files found or stopped.", 0)
            self.is_working = False
            return
        for f in files:
            # [변경] 컬럼 데이터 매핑 (name, date, size)
            self.file_list.insert("", tk.END, values=(f["name"], f["date"], f["size"]))
        self.is_working = False
        self.set_status("Ready", 0)

    def toggle_language(self):
        self.lang = "ENG" if self.lang == "KOR" else "KOR"
        self.update_texts()

    def update_texts(self):
        t = TRANSLATIONS[self.lang]
        self.root.title(t["title"])
        self.title_label.config(text=t["title"])
        self.add_btn.config(text=t["btn_add_folder"])
        self.clean_btn.config(text=t["btn_start_clean"])
        self.camp_btn.config(text=t["btn_campaign_clean"])
        self.lang_btn.config(text=t["lang_switch"])
        
        self.game_list.heading("path", text=t["label_game"])
        self.game_list.heading("count", text=t["label_save_files"])
        self.file_list.heading("faction", text=t["label_faction"]) # 내부 ID는 유지하되 텍스트만 변경 가능
        self.file_list.heading("leader", text=t["label_leader"])
        
        # 텍스트 변경 적용
        self.file_list.heading("date", text="Date Modified")
        self.file_list.heading("size", text="Size")

    def add_folder(self):
        t = TRANSLATIONS[self.lang]
        folder = filedialog.askdirectory(title=t["dialog_folder_title"])
        if folder:
            if hasattr(self.logic, 'search_paths'):
                self.logic.search_paths.append(folder)
            self.refresh_list()
            messagebox.showinfo(t["msg_done_title"], t["msg_added"].format(folder))
