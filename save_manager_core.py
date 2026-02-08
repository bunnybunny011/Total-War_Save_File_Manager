import os
from datetime import datetime
# [수정] save_reader import 제거

class SaveManagerLogic:
    def __init__(self):
        self.search_paths = []

    def scan_games(self):
        games = []
        appdata = os.getenv('APPDATA')
        if not appdata: return []

        base_path = os.path.join(appdata, "The Creative Assembly")
        
        if os.path.exists(base_path):
            for entry in os.listdir(base_path):
                full_path = os.path.join(base_path, entry, "save_games")
                if os.path.exists(full_path):
                    count = len([f for f in os.listdir(full_path) if f.lower().endswith(".save")])
                    games.append({
                        "name": entry,
                        "path": full_path,
                        "count": count
                    })
        
        for path in self.search_paths:
            if os.path.exists(path):
                name = os.path.basename(os.path.dirname(path))
                count = len([f for f in os.listdir(path) if f.lower().endswith(".save")])
                games.append({
                    "name": f"[User] {name}",
                    "path": path,
                    "count": count
                })

        return games
    
    def format_size(self, size_bytes):
        if size_bytes == 0: return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024 and i < len(units)-1:
            size_bytes /= 1024; i += 1
        return f"{size_bytes:.2f} {units[i]}"

    def get_save_files_details(self, folder_path, progress_callback=None, stop_check=None):
        if not os.path.exists(folder_path): return []
        
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(".save")]
        details = []
        
        total = len(files)
        for idx, f in enumerate(files):
            if stop_check and stop_check(): break
            if progress_callback: progress_callback(idx, total)
            
            full_path = os.path.join(folder_path, f)
            
            mtime = os.path.getmtime(full_path)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            
            size = os.path.getsize(full_path)
            size_str = self.format_size(size)
            
            details.append({
                "name": f,
                "date": date_str,
                "size": size_str
            })
            
        return details
