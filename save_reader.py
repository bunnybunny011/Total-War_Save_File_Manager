import os
import re
import mmap
from mapping_data import GAME_SPECIFIC_MAPS, FACTION_TO_LEADER_FALLBACK

class SaveMetadataReader:
    @staticmethod
    def get_metadata(file_path):
        if not os.path.exists(file_path): return None
        try:
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    
                    game_title = SaveMetadataReader._detect_game_title(file_path)
                    
                    target_map = {}
                    # 게임별 맵 가져오기
                    if "Warhammer" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Warhammer", {})
                    elif "Three Kingdoms" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Three Kingdoms", {})
                    elif "Pharaoh" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Pharaoh", {})
                    elif "Shogun" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Shogun II", {})
                    elif "Rome" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Rome II", {})
                    elif "Britannia" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Thrones of Britannia", {})
                    elif "Napoleon" in game_title: target_map = GAME_SPECIFIC_MAPS.get("Napoleon", {})
                    
                    # [중요] 인코딩 전략 변경: 모든 게임에 대해 안전하게 둘 다 검색
                    # 속도가 충분히 빠르다고 하셨으므로, 누락 방지를 위해 안전하게 갑니다.
                    encodings = ["utf-16-le", "ascii", "utf-8"] 

                    faction_key = SaveMetadataReader._scan_full(mm, target_map, encodings)
                    
                    map_name = game_title + " Campaign"
                    if "Napoleon" in game_title: map_name = SaveMetadataReader._detect_nap_map(mm)
                    if "Warhammer" in game_title: map_name = SaveMetadataReader._detect_wh_map(mm)
                    
                    faction_name = "Unknown"
                    if faction_key:
                        base_name = target_map.get(faction_key, faction_key)
                        faction_name = SaveMetadataReader._resolve_faction_name(base_name, map_name)
                    
                    leader_name = FACTION_TO_LEADER_FALLBACK.get(faction_name, "Unknown")
                    version = SaveMetadataReader._extract_version(mm)

                    return {"game": game_title, "version": version, "faction": faction_name, "leader": leader_name, "map": map_name}
        except: return None

    @staticmethod
    def _scan_full(mm, mapping, encodings):
        if not mapping: return None
        
        # [중요] 키 길이 순으로 정렬 (가장 긴 것부터 검색해야 'troy' 같은 짧은 게 'phar_dyn_troy'보다 먼저 걸리는 걸 방지)
        sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
        
        for enc in encodings:
            for key in sorted_keys:
                try:
                    # 파라오/삼탈워는 utf-8 우선, 나머지는 utf-16le 우선이지만
                    # 여기서는 for enc 루프가 알아서 처리함
                    encoded_key = key.encode(enc)
                    
                    # 검색
                    if mm.find(encoded_key) != -1:
                        # [안전장치] 만약 키가 너무 짧은데(4글자 이하), 
                        # 더 확실한 접두사 붙은 키('phar_dyn_...')가 매핑에 있다면 이건 오탐지일 확률이 높음.
                        # 하지만 sorted_keys로 긴 걸 먼저 찾으므로, 여기까지 왔다는 건 긴 키가 없다는 뜻.
                        # 즉, 진짜 짧은 키일 확률이 높음. 따라서 리턴.
                        return key
                except: pass
        return None

    @staticmethod
    def _resolve_faction_name(base_name, map_name):
        if "Napoleon" in map_name:
            if "Egypt" in map_name:
                if "영국" in base_name or "대영" in base_name: return "대영 제국 (이집트)"
                if "프랑스" in base_name: return "프랑스 공화국 (이집트)"
            if "Peninsula" in map_name:
                if "영국" in base_name or "대영" in base_name: return "대영 제국 (반도)"
                if "프랑스" in base_name: return "프랑스 제국 (반도)"
            if "Europe" in map_name:
                if "영국" in base_name or "대영" in base_name: return "대영 제국 (유럽)"
        return base_name
        
    # ... (나머지 _detect_game_title 등은 기존과 동일) ...
    @staticmethod
    def _detect_game_title(path):
        p = path.lower()
        if "warhammer" in p: return "Warhammer III"
        if "three" in p: return "Three Kingdoms"
        if "pharaoh" in p: return "Pharaoh"
        if "rome" in p: return "Rome II"
        if "shogun" in p: return "Shogun II"
        if "napoleon" in p: return "Napoleon"
        if "thrones" in p or "britannia" in p: return "Thrones of Britannia"
        if "attila" in p: return "Attila" 
        return "Total War"

    @staticmethod
    def _detect_nap_map(mm):
        scan = mm[:1024*50].lower()
        if b"egypt" in scan: return "Napoleon: Egypt Campaign"
        if b"italy" in scan: return "Napoleon: Italy Campaign"
        if b"peninsula" in scan or b"spa_nap" in scan: return "Napoleon: Peninsular Campaign"
        return "Napoleon: Europe Campaign"
        
    @staticmethod
    def _detect_wh_map(mm):
        scan = mm[:1024*1024*2].lower()
        if b"main_warhammer" in scan: return "Immortal Empires"
        if b"chaos" in scan: return "The Realm of Chaos"
        if b"vortex" in scan: return "Eye of the Vortex"
        return "Campaign Map"

    @staticmethod
    def _extract_version(mm):
        match = re.search(rb"(v\d+\.\d+\.\d+|Build\s+[\d\.]+)", mm[:4096])
        return match.group().decode('utf-8', errors='ignore') if match else "Unknown"
