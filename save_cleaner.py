import os
import re
import shutil
import subprocess
# [수정] from save_reader import SaveMetadataReader 삭제

class SaveCleanerLogic:
    """
    v15.0 Standalone Tokenizer Logic:
    - Removed dependency on SaveMetadataReader.
    - Pure filename-based tokenization strategy.
    """

    @staticmethod
    def get_backup_folder(base_folder):
        backup_dir = os.path.join(base_folder, "_Backup")
        if not os.path.exists(backup_dir): os.makedirs(backup_dir)
        return backup_dir

    @staticmethod
    def open_folder(path):
        if os.name == 'nt': os.startfile(path)
        elif os.name == 'posix': subprocess.Popen(['xdg-open', path])

    @staticmethod
    def move_to_backup(file_path, backup_folder):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(backup_folder, file_name)
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(file_name)
            cnt = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(backup_folder, f"{base}_{cnt}{ext}")
                cnt += 1
        try:
            shutil.move(file_path, dest_path)
            return True
        except: return False

    @staticmethod
    def tokenize_filename(filename):
        # 정규식으로 숫자와 비숫자 분리
        tokens = re.split(r'(\d+)', filename)
        parsed_tokens = []
        for t in tokens:
            if t.isdigit():
                parsed_tokens.append(int(t))
            elif t != "":
                parsed_tokens.append(t.lower())
        return parsed_tokens

    @staticmethod
    def parse_detailed_info(file_path):
        filename = os.path.basename(file_path)
        base, ext = os.path.splitext(filename)
        base_lower = base.lower()

        # [0] 절대 보호 (자동/빠른)
        protected_keywords = ["자동", "빠른", "auto", "quick"]
        if any(k in base_lower for k in protected_keywords):
            return ("PROTECTED", base), (0, 0)

        # [1] 토큰화 수행
        tokens = SaveCleanerLogic.tokenize_filename(base)
        
        # [2] 접미사(Suffix) 분리
        core_pattern = tuple(tokens)
        suffix = 0
        
        if len(tokens) > 0 and isinstance(tokens[-1], int):
            suffix = tokens[-1]
            core_pattern = tuple(tokens[:-1]) 
            
            # 공백/특수문자 트림 처리
            if len(core_pattern) > 0 and isinstance(core_pattern[-1], str):
                cleaned_str = core_pattern[-1].strip()
                if not cleaned_str:
                    core_pattern = core_pattern[:-1]
                else:
                    temp = list(core_pattern)
                    temp[-1] = cleaned_str
                    core_pattern = tuple(temp)

        mtime = os.path.getmtime(file_path)
        sort_key = (suffix, mtime)

        return core_pattern, sort_key

    @staticmethod
    def clean_duplicates_smart(folder_path, progress_callback=None):
        if not os.path.exists(folder_path): return 0, [], "", 0
        
        backup_dir = SaveCleanerLogic.get_backup_folder(folder_path)
        files = [f for f in os.listdir(folder_path) if f.endswith(".save")]
        
        groups = {}
        for idx, f in enumerate(files):
            full_path = os.path.join(folder_path, f)
            group_key, sort_key = SaveCleanerLogic.parse_detailed_info(full_path)
            
            if group_key[0] == "PROTECTED": continue

            if group_key not in groups: groups[group_key] = []
            groups[group_key].append((f, sort_key))
            if progress_callback: progress_callback(idx, len(files))

        moved_count = 0
        moved_files = []
        moved_size = 0

        for key in groups:
            file_list = groups[key]
            if len(file_list) < 2: continue
            
            file_list.sort(key=lambda x: x[1])
            to_move = file_list[:-1]
            
            for fname, _ in to_move:
                src = os.path.join(folder_path, fname)
                fsize = os.path.getsize(src)
                if SaveCleanerLogic.move_to_backup(src, backup_dir):
                    moved_files.append(fname)
                    moved_count += 1
                    moved_size += fsize
        
        return moved_count, moved_files, backup_dir, moved_size

    @staticmethod
    def clean_campaign_ratio(folder_path, progress_callback=None):
        if not os.path.exists(folder_path): return 0, [], "", 0
        
        backup_dir = SaveCleanerLogic.get_backup_folder(folder_path)
        files = [f for f in os.listdir(folder_path) if f.endswith(".save")]
        
        camp_groups = {}
        for f in files:
            full_path = os.path.join(folder_path, f)
            
            tokens = SaveCleanerLogic.tokenize_filename(f)
            faction_key = "Unknown"
            if tokens and isinstance(tokens[0], str):
                faction_key = tokens[0].strip()
            
            nums = [t for t in tokens if isinstance(t, int)]
            mtime = os.path.getmtime(full_path)
            sort_key = tuple(nums) + (mtime,)
            
            if faction_key not in camp_groups: camp_groups[faction_key] = []
            camp_groups[faction_key].append((f, sort_key))

        moved_files = []
        moved_size = 0

        for camp in camp_groups:
            file_list = camp_groups[camp]
            file_list.sort(key=lambda x: x[1])
            
            total = len(file_list)
            for i in range(total):
                if i == total - 1: continue
                if (i + 1) % 4 != 0:
                    fname = file_list[i][0]
                    src = os.path.join(folder_path, fname)
                    fsize = os.path.getsize(src)
                    if SaveCleanerLogic.move_to_backup(src, backup_dir):
                        moved_files.append(fname)
                        moved_size += fsize

        return len(moved_files), moved_files, backup_dir, moved_size
