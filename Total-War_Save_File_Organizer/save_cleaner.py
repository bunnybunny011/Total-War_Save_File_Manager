import os
import shutil
import re
from save_reader import SaveMetadataReader

class SaveCleanerLogic:
    """세이브 파일 탐색 및 정리 로직을 담당합니다."""
    def __init__(self, base_path=None):
        if base_path:
            self.search_paths = [base_path]
        else:
            appdata = os.environ.get('APPDATA', '')
            prog_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
            self.search_paths = []
            if appdata:
                self.search_paths.append(os.path.join(appdata, 'The Creative Assembly'))
            steam_common = os.path.join(prog_x86, 'Steam', 'steamapps', 'common')
            if os.path.exists(steam_common):
                self.search_paths.append(steam_common)
        self.games = self.scan_games()

    def scan_games(self):
        games = []
        possible_save_dirs = ["save_games", "saves", "Save", "Saves"]
        valid_exts = (".save", ".sav")
        for base_path in self.search_paths:
            if not os.path.exists(base_path) or not os.path.isdir(base_path): continue
            for root, dirs, files in os.walk(base_path):
                if any(d.lower() in [sd.lower() for sd in possible_save_dirs] for d in dirs):
                    save_dir = next(os.path.join(root, d) for d in dirs if d.lower() in [sd.lower() for sd in possible_save_dirs])
                    save_files = [f for f in os.listdir(save_dir) if f.lower().endswith(valid_exts)]
                    if save_files:
                        game_name = os.path.basename(root)
                        games.append({"name": game_name, "path": save_dir, "count": len(save_files)})
        return games

    def get_save_files_details(self, game_path, progress_callback=None):
        details = []
        valid_exts = (".save", ".sav")
        all_files = [f for f in os.listdir(game_path) if f.lower().endswith(valid_exts)]
        total = len(all_files)
        
        for i, f in enumerate(all_files):
            if progress_callback: progress_callback(i + 1, total)
            full_path = os.path.join(game_path, f)
            try:
                mtime = os.path.getmtime(full_path)
                size = os.path.getsize(full_path)
                metadata = SaveMetadataReader.get_metadata(full_path) or {}
                details.append({
                    "name": f, "path": full_path, "time": mtime, "size": size,
                    "game": metadata.get("game", "Unknown"),
                    "faction": metadata.get("faction", "Unknown"),
                    "leader": metadata.get("leader", "Unknown"),
                    "version": metadata.get("version", "Unknown"),
                    "map": metadata.get("map", "Unknown")
                })
            except: pass
        return sorted(details, key=lambda x: x["time"], reverse=True)

    def clean_duplicates(self, game_path, progress_callback=None):
        files = self.get_save_files_details(game_path)
        if not files: return 0, 0, 0, 0, 0
        
        backup_dir = os.path.join(game_path, "backup")
        if not os.path.exists(backup_dir): os.makedirs(backup_dir)
        
        before_count = len(files)
        before_size = sum(f["size"] for f in files)
        
        seen_turns = {}
        moved_count = 0
        total = len(files)
        
        for i, f in enumerate(files):
            if progress_callback: progress_callback(i + 1, total)
            name = f["name"]
            # 턴/연도 추출 (숫자 조합)
            match = re.search(r'(\d{4}\s*BC|\d+\s*턴|\d+\s*turn|턴\s*\d+|Year\s*\d+)', name, re.I)
            turn_key = match.group(0).lower().replace(" ", "") if match else name
            
            if turn_key not in seen_turns:
                seen_turns[turn_key] = f
            else:
                shutil.move(f["path"], os.path.join(backup_dir, name))
                moved_count += 1
                
        after_files = self.get_save_files_details(game_path)
        after_count = len(after_files)
        after_size = sum(f["size"] for f in after_files)
        return before_count, before_size, after_count, after_size, moved_count

    def clean_campaign_history(self, game_path, progress_callback=None):
        files = self.get_save_files_details(game_path)
        if len(files) <= 5: return 0, 0, 0, 0, 0
        
        backup_dir = os.path.join(game_path, "backup")
        if not os.path.exists(backup_dir): os.makedirs(backup_dir)
        
        before_count = len(files)
        before_size = sum(f["size"] for f in files)
        
        # 최신 5개는 무조건 보존, 나머지에 대해 4개 중 3개 삭제(이동)
        protected = files[:5]
        to_process = files[5:]
        to_process.reverse() # 오래된 것부터
        
        moved_count = 0
        total = len(to_process)
        for i, f in enumerate(to_process):
            if progress_callback: progress_callback(i + 1, total)
            if i % 4 != 0: # 4개 중 1개(0번)만 남기고 이동
                shutil.move(f["path"], os.path.join(backup_dir, f["name"]))
                moved_count += 1
                
        after_files = self.get_save_files_details(game_path)
        return before_count, before_size, len(after_files), sum(f["size"] for f in after_files), moved_count
