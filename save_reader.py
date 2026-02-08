# import os
# import struct
# import re

# class SaveMetadataReader:
#     """
#     v14.0 The Purifier logic:
#     - Reads strings from binary but applies STRICT regex filtering.
#     - If a string contains garbage symbols (, 뷁, etc.), it is rejected.
#     - Ensures clean output for the UI.
#     """

#     @staticmethod
#     def is_clean_string(s):
#         """
#         문자열이 '깨끗한지' 검사합니다.
#         한글, 영문, 숫자, 공백, 일부 특수문자(-_.)만 허용합니다.
#         제어 문자나 이상한 심볼이 있으면 False.
#         """
#         if not s: return False
#         # 한글 범위: 가-힣
#         # 영문/숫자/공백/기본문장부호
#         # 이 외의 문자가 많이 섞여있으면 쓰레기 데이터로 간주
#         clean_pattern = re.compile(r'^[가-힣a-zA-Z0-9\s\-\._\(\)\[\]]+$')
#         return bool(clean_pattern.match(s))

#     @staticmethod
#     def read_string(f):
#         try:
#             length_bytes = f.read(2)
#             if len(length_bytes) < 2: return None
#             length = struct.unpack('<H', length_bytes)[0]
            
#             # 길이 필터 (너무 길거나 짧으면 무시)
#             if length < 2 or length > 50: return None
            
#             string_bytes = f.read(length * 2)
#             if len(string_bytes) != length * 2: return None
            
#             # UTF-16 decoding
#             val = string_bytes.decode('utf-16-le', errors='ignore').strip()
            
#             # [핵심] 엄격한 필터링 적용
#             if SaveMetadataReader.is_clean_string(val):
#                 return val
#             return None
#         except:
#             return None

#     @staticmethod
#     def get_metadata(file_path):
#         metadata = {
#             "faction": "Unknown",
#             "leader": "Unknown"
#         }
        
#         if not os.path.exists(file_path): return metadata
        
#         try:
#             with open(file_path, 'rb') as f:
#                 f.seek(0)
#                 found_strings = []
                
#                 # 검색 범위 축소 (앞부분 1KB만)
#                 # 너무 뒤까지 가면 텍스트 데이터가 섞여 나옴
#                 search_limit = 1024 
#                 current_pos = 0
                
#                 ignore_list = ["System", "Campaign", "Default", "autosave", "quicksave", "mp_", "save_games"]
                
#                 while current_pos < search_limit and len(found_strings) < 5:
#                     f.seek(current_pos)
#                     try:
#                         s = SaveMetadataReader.read_string(f)
#                         if s and s not in ignore_list and not s.isdigit():
#                             found_strings.append(s)
#                             current_pos = f.tell()
#                         else:
#                             current_pos += 1
#                     except:
#                         current_pos += 1

#                 # [전략 변경] 
#                 # 내부 데이터가 불안정하므로(워해머3 등), 내부 데이터는 '보조'로만 사용
#                 # 여기서는 추출된 후보군만 반환하고, 최종 결정은 Core에서 함
#                 if len(found_strings) >= 1: metadata['candidate_1'] = found_strings[0]
#                 if len(found_strings) >= 2: metadata['candidate_2'] = found_strings[1]

#         except Exception:
#             pass
            
#         return metadata
