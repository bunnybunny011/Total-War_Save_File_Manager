import os
import mmap
import re

def deep_analyze(folder_path):
    """폴더 내의 모든 세이브 파일을 전수 스캔하여 잠재적인 세력/리더 코드를 추출합니다."""
    print(f"--- 전수 조사 시작: {folder_path} ---")
    valid_exts = (".save", ".sav")
    save_files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
    
    unique_codes = set()
    # 토탈워 내부 시스템 코드 패턴 (wh_main_..., wh3_main_..., 등)
    pattern = re.compile(rb'([a-z0-9_]{5,30}_[sc|main|dlc][a-z0-9_]{3,30})')
    
    for f_name in save_files:
        path = os.path.join(folder_path, f_name)
        print(f"분석 중: {f_name}...", end="\r")
        try:
            with open(path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # 10MB 영역에서 시스템 코드 패턴 추출
                    matches = pattern.findall(mm[:10*1024*1024])
                    for m in matches:
                        unique_codes.add(m.decode('ascii', errors='ignore'))
        except: pass
    
    print("\n\n--- [추출된 잠재적 시스템 코드 목록] ---")
    for code in sorted(list(unique_codes)):
        print(code)
    print("\n--- 분석 완료 ---")

if __name__ == "__main__":
    # 임의의 토탈워 세이브 경로 (사용자 환경에 맞춰 자동 탐색)
    appdata = os.environ.get('APPDATA', '')
    base = os.path.join(appdata, 'The Creative Assembly')
    if os.path.exists(base):
        for root, dirs, files in os.walk(base):
            if "save_games" in dirs:
                deep_analyze(os.path.join(root, "save_games"))
                break
