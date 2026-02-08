import os
import re
import struct
import mmap
from mapping_data import FACTION_MAP, LEADER_MAP, RACE_RELATIONS

class SaveMetadataReader:
    """토탈워 세이브 파일의 데이터를 분석하여 메타데이터를 추출합니다. [Absolute v5 Strict]"""
    
    @staticmethod
    def get_metadata(file_path):
        if not os.path.exists(file_path): return None
        
        game_title = "Unknown Total War"
        p_lower = file_path.lower()
        if "warhammer3" in p_lower: game_title = "Warhammer III"
        elif "warhammer2" in p_lower: game_title = "Warhammer II"
        elif "warhammer" in p_lower: game_title = "Warhammer I"
        else:
            # 기타 타이틀 식별 (생략 가능하나 유지)
            for t in ["rome2", "shogun2", "attila", "threekingdoms", "pharaoh"]:
                if t in p_lower: game_title = t.capitalize(); break

        try:
            file_size = os.path.getsize(file_path)
            # v3.4.0: 타이틀별 최적화된 스캔 범위
            scan_limit = 10 * 1024 * 1024 if game_title == "Warhammer III" else 4 * 1024 * 1024
            read_size = min(file_size, scan_limit)
            
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    data = mm[:read_size]
                    
                    # 1. 버전 추출 (공통)
                    version = SaveMetadataReader._extract_version(data)
                    
                    # 2. 타이틀별 정밀 파싱 (Strict Pass)
                    if game_title == "Warhammer III":
                        return SaveMetadataReader._parse_strict(data, game_title, version)
                    elif game_title == "Warhammer II":
                        return SaveMetadataReader._parse_strict(data, game_title, version, is_wh2=True)
                    else:
                        return SaveMetadataReader._parse_common(data, game_title, version)
        except Exception as e:
            print(f"Metadata Error: {e}")
            return None

    @staticmethod
    def _find_strict_match(data, faction_name):
        """Absolute v5: 감지된 세력(Race)에 허용된 리더만 매칭 (오인식 원천 차단)"""
        if not data or not faction_name: return "Unknown", None
        
        # 해당 종족에 허용된 리더 목록 가져오기
        allowed_leaders = RACE_RELATIONS.get(faction_name, [])
        if not allowed_leaders: 
            # 매핑에 없는 신규 종족이면 전체 검색으로 폴백
            return SaveMetadataReader._find_match_v4(data, LEADER_MAP)

        # 허용된 리더들만 필터링한 전용 맵 생성
        strict_map = {k: v for k, v in LEADER_MAP.items() if v in allowed_leaders}
        return SaveMetadataReader._find_match_v4(data, strict_map, context_weight=True)

    @staticmethod
    def _find_match_v4(data, mapping, context_weight=False):
        """기존 v4 로직을 내부 유틸리티로 활용"""
        decoded_pool = []
        for encoding in ['ascii', 'utf-16-le']:
            try: decoded_pool.append(data.decode(encoding, errors='ignore').lower())
            except: pass
            if encoding == 'utf-16-le':
                try: decoded_pool.append(data[1:].decode(encoding, errors='ignore').lower())
                except: pass
        
        normalized_data = " ".join(decoded_pool)
        slim_data = re.sub(r'[^a-z0-9\uac00-\ud7a3]', '', normalized_data)
        
        matches = []
        for key, val in mapping.items():
            k_lower, v_lower = key.lower(), val.lower()
            k_slim = re.sub(r'[^a-z0-9]', '', k_lower)
            v_slim = re.sub(r'[^a-z0-9\uac00-\ud7a3]', '', v_lower)
            
            if k_lower in normalized_data or v_lower in normalized_data or k_slim in slim_data or v_slim in slim_data:
                score = len(key)
                if "wh" in k_lower or "sc" in k_lower: score += 100
                if context_weight: score += 1000 # 엄격 모드 가중치
                matches.append((key, score))
                    
        if not matches: return None, None
        best_key = max(matches, key=lambda x: x[1])[0]
        return best_key, mapping[best_key]

    @staticmethod
    def _extract_version(data):
        v_match = re.search(rb"(v\d+\.\d+\.\d+|Build\s+[\d\.]+)", data)
        return v_match.group().decode('utf-8', errors='ignore').strip() if v_match else "Unknown"

    @staticmethod
    def _parse_strict(data, title, version, is_wh2=False):
        info = {"game": title, "faction": "Unknown", "version": version, "map": "Unknown", "leader": "Unknown", "leader_key": None}
        
        # 1. 플레이어 구역 특정 (WH3/WH2 공통 marker)
        marker = data.find(b"local_faction")
        if marker == -1: marker = data.find(b"CAMPAIGN_SAVE_GAME")
        
        scan_data = data
        if marker != -1:
            start = max(0, marker - 50000)
            end = min(len(data), marker + 300000)
            scan_data = data[start:end]

        # STEP 1: 세력(Faction) 먼저 확정
        f_key, f_val = SaveMetadataReader._find_match_v4(scan_data, FACTION_MAP, context_weight=True)
        if f_val: info["faction"] = f_val
        
        # STEP 2: 감지된 세력에 맞는 리더만 검색 (Strict Binding)
        l_key, l_val = SaveMetadataReader._find_strict_match(scan_data, info["faction"])
        if l_val: info["leader_key"], info["leader"] = l_key, l_val
        
        # 맵 정보
        c_lower = data.lower()
        if is_wh2:
            info["map"] = "Eye of the Vortex" if b"vortex" in c_lower else "Mortal Empires"
        else:
            if b"combi" in c_lower or b"immortal" in c_lower: info["map"] = "Immortal Empires"
            elif b"chaos" in c_lower: info["map"] = "The Realm of Chaos"
            else: info["map"] = "Warhammer Campaign"
            
        return info

    @staticmethod
    def _parse_common(data, title, version):
        info = {"game": title, "faction": "Unknown", "version": version, "map": title + " Campaign", "leader": "Unknown", "leader_key": None}
        f_key, f_val = SaveMetadataReader._find_match_v4(data, FACTION_MAP)
        if f_val: info["faction"] = f_val
        l_key, l_val = SaveMetadataReader._find_match_v4(data, LEADER_MAP)
        if l_val: info["leader_key"], info["leader"] = l_key, l_val
        return info
