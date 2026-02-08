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
        
    def scan_games(self):
        games = []
        possible_save_dirs = ["save_games", "saves", "Save", "Saves"]
        valid_exts = (".save", ".sav")
        
        # 중복 스캔 방지를 위해 경로 집합(set) 사용
        unique_paths = set(self.search_paths)
        
        for base_path in unique_paths:
            if not os.path.exists(base_path) or not os.path.isdir(base_path): continue
            for root, dirs, files in os.walk(base_path):
                # 세이브 폴더 이름과 일치하는 폴더 찾기
                found_dir = None
                for d in dirs:
                    if d.lower() in [sd.lower() for sd in possible_save_dirs]:
                        found_dir = d
                        break
                
                if found_dir:
                    save_dir = os.path.join(root, found_dir)
                    save_files = [f for f in os.listdir(save_dir) if f.lower().endswith(valid_exts)]
                    if save_files:
                        game_name = os.path.basename(root)
                        games.append({"name": game_name, "path": save_dir, "count": len(save_files)})
        return games

    def get_save_files_details(self, game_path, progress_callback=None, stop_check=None):
        details = []
        valid_exts = (".save", ".sav")
        if not os.path.exists(game_path): return []
        
        all_files = [f for f in os.listdir(game_path) if f.lower().endswith(valid_exts)]
        total = len(all_files)
        
        for i, f in enumerate(all_files):
            # [중단 체크] UI에서 멈추라고 하면 즉시 중단
            if stop_check and stop_check(): return []
            
            if progress_callback: progress_callback(i + 1, total)
            
            full_path = os.path.join(game_path, f)
            try:
                mtime = os.path.getmtime(full_path)
                size = os.path.getsize(full_path)
                
                # 메타데이터 읽기
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
        files = self.get_save_files_details(game_path) # 여기선 메타데이터 없이 파일명만 봐도 되지만 재사용
        if not files: return 0, 0, 0, 0, 0
        
        # [수정] 백업 폴더 경로 절대경로화 및 생성
        backup_dir = os.path.abspath(os.path.join(game_path, "backup"))
        if not os.path.exists(backup_dir): 
            os.makedirs(backup_dir, exist_ok=True)
        
        before_count = len(files)
        before_size = sum(f["size"] for f in files)
        
        seen_turns = {}
        moved_count = 0
        total = len(files)
        
        for i, f in enumerate(files):
            if progress_callback: progress_callback(i + 1, total)
            name = f["name"]
            
            # 턴/연도 추출 패턴
            match = re.search(r'(\d{4}\s*BC|\d+\s*턴|\d+\s*turn|턴\s*\d+|Year\s*\d+)', name, re.I)
            # 패턴이 없으면 파일 이름 전체를 키로 사용 (동일 이름 파일 처리)
            turn_key = match.group(0).lower().replace(" ", "") if match else name
            
            if turn_key not in seen_turns:
                seen_turns[turn_key] = f
            else:
                try:
                    src = f["path"]
                    dst = os.path.join(backup_dir, name)
                    
                    # [안전 장치] 백업 폴더에 이미 파일이 있으면 삭제 후 덮어쓰기
                    if os.path.exists(dst): os.remove(dst)
                    
                    shutil.move(src, dst)
                    moved_count += 1
                except Exception as e:
                    print(f"Move Error: {e}")
                
        # 결과 계산 (다시 스캔하지 않고 계산)
        valid_files = [f for f in os.listdir(game_path) if f.lower().endswith((".save", ".sav"))]
        after_count = len(valid_files)
        after_size = 0
        for vf in valid_files:
            try: after_size += os.path.getsize(os.path.join(game_path, vf))
            except: pass
            
        return before_count, before_size, after_count, after_size, moved_count

    def clean_campaign_history(self, game_path, progress_callback=None):
        files = self.get_save_files_details(game_path)
        if len(files) <= 5: return 0, 0, len(files), sum(f["size"] for f in files), 0
        
        backup_dir = os.path.abspath(os.path.join(game_path, "backup"))
        if not os.path.exists(backup_dir): os.makedirs(backup_dir, exist_ok=True)
        
        before_count = len(files)
        before_size = sum(f["size"] for f in files)
        
        # 최신 5개 보존
        to_process = files[5:]
        
        moved_count = 0
        total = len(to_process)
        
        for i, f in enumerate(to_process):
            if progress_callback: progress_callback(i + 1, total)
            
            # 4개 주기 중 1개 남기기 (0,1,2 삭제, 3 보존... 식은 아니고)
            # 여기선 "3개 삭제 1개 보존" -> index 1,2,3 삭제, 0 보존 (반대)
            # 원본 로직 유지: i % 4 != 0 이면 이동 (즉 1,2,3번 이동, 0번 유지)
            if i % 4 != 0:
                try:
                    src = f["path"]
                    dst = os.path.join(backup_dir, f["name"])
                    if os.path.exists(dst): os.remove(dst)
                    shutil.move(src, dst)
                    moved_count += 1
                except Exception as e:
                    print(f"Move Error: {e}")
                    
        valid_files = [f for f in os.listdir(game_path) if f.lower().endswith((".save", ".sav"))]
        after_size = 0
        for vf in valid_files:
            try: after_size += os.path.getsize(os.path.join(game_path, vf))
            except: pass
            
        return before_count, before_size, len(valid_files), after_size, moved_count
