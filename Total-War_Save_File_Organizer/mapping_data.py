# --- 다국어 데이터 ---
TRANSLATIONS = {
    "KOR": {
        "title": "토탈워 세이브 매니저 [FINAL Isolation]",
        "btn_add_folder": "게임 폴더 추가", "btn_change_base": "기본 경로 변경",
        "btn_start_clean": "중복 파일 정리 (1, 2, 3, 4)", "btn_campaign_clean": "중복 파일 정리 (3:1)",
        "label_detected": "탐지된 게임 세이브 폴더",
        "label_desc": "* (1, 2, 3, 4): 동일 시점 최신본 보존 / (3:1): 3개 삭제 1개 보존 (최신 필수 보존)",
        "msg_warning_no_selection": "정리할 게임을 목록에서 선택해주세요.",
        "msg_confirm_clean": "'{}'의 세이브 파일을 정리하시겠습니까?",
        "msg_confirm_campaign": "'{}'의 히스토리 정보를 정리하시겠습니까?",
        "msg_info_no_files": "정리할 세이브 파일이 없습니다.", "msg_done_title": "완료",
        "msg_done_body": "[{}] 정리 완료\n▶ 절약됨: {}개 파일 이동 ({})",
        "msg_error": "오류: {}", "dialog_folder_title": "폴더 선택",
        "dialog_add_title": "경로 추가", "msg_added": "추가됨: {}",
        "label_save_files": "파일 목록", "label_game": "게임",
        "label_faction": "세력", "label_leader": "리더",
        "label_version": "버전", "label_map": "지도",
        "label_details": "상세 정보", "lang_switch": "English"
    },
    "ENG": {
        "title": "Total War Save Manager",
        "btn_add_folder": "Add Folder", "btn_change_base": "Change Base",
        "btn_start_clean": "Clean (1:1)", "btn_campaign_clean": "Cleanup (3:1)",
        "label_detected": "Save Folders", "label_game": "Game", "label_faction": "Faction", 
        "label_leader": "Leader", "label_version": "Version", "label_map": "Map",
        "label_save_files": "Files", "label_details": "Details",
        "lang_switch": "한국어", "msg_done_title": "Done"
    }
}

# --- 종족별 군주 강제 결속 매핑 (Strict Binding) ---
# 이 맵은 특정 세력이 감지되었을 때, 해당 리더들만 검색 후보로 올리도록 강제합니다.
RACE_RELATIONS = {
    "케세이": ["묘영", "조명", "원보"],
    "키슬레프": ["카타린", "코스탈틴", "보리스 우르수스", "유리 바르코프"],
    "코른": ["스카브란드"],
    "슬라네쉬": ["느카리"],
    "너글": ["쿠가스"],
    "젠취": ["카이로스"],
    "오거 킹덤": ["그리수스", "스크라그"],
    "스케이븐": ["로드 스크롤크", "이킷 클로", "퀵 헤드테이커", "트롤치"],
    "제국": ["카를 프란츠", "벨타자르 겔트", "폴크마"],
    "드워프": ["토그림", "벨레가르", "웅그림"],
}

# --- 세력 매핑 (종족 단위) ---
FACTION_MAP = {
    "wh3_main_cth_": "케세이", "cth_the_northern_provinces": "케세이", "cth_the_western_provinces": "케세이",
    "북방 변경주": "케세이", "서방 변경주": "케세이", "northern_provinces": "케세이", "western_provinces": "케세이",
    "wh3_main_ksl_": "키슬레프", "ksl_the_ice_court": "키슬레프", "ksl_the_great_orthodoxy": "키슬레프", "ksl_expedition": "키슬레프",
    "아이스 코트": "키슬레프", "대정교회": "키슬레프", "키슬레프 원정대": "키슬레프",
    "wh3_main_dae_": "카오스의 악마", "wh3_main_kho_": "코른", "wh3_main_nur_": "너글", "wh3_main_tze_": "젠취", "wh3_main_sla_": "슬라네쉬", 
}

# --- 리더 매핑 (시스템 코드 포함) ---
LEADER_MAP = {
    "miao_ying": "묘영", "wh3_main_sc_cth_miao_ying": "묘영", "cth_miao_ying": "묘영", "묘영": "묘영",
    "zhao_ming": "조명", "wh3_main_sc_cth_zhao_ming": "조명", "cth_zhao_ming": "조명", "조명": "조명",
    "yuan_bo": "원보", "wh3_dlc24_sc_cth_yuan_bo": "원보", "cth_yuan_bo": "원보", "원보": "원보",
    "katarin": "카타린", "wh3_main_sc_ksl_katarin": "카타린", "tzarina": "카타린", "카타린": "카타린",
    "kostaltyn": "코스탈틴", "wh3_main_sc_ksl_kostaltyn": "코스탈틴", "코스탈틴": "코스탈틴",
    "boris": "보리스 우르수스", "wh3_main_sc_ksl_boris": "보리스 우르수스", "보리스": "보리스 우르수스",
    "yuri_barkov": "유리 바르코프", "wh3_main_sc_ksl_yuri": "유리 바르코프", "yuri": "유리 바르코프", "유리": "유리 바르코프",
    "skarbrand": "스카브란드", "wh3_main_sc_kho_skarbrand": "스카브란드", "스카브란드": "스카브란드",
    "nkari": "느카리", "wh3_main_sc_sla_nkari": "느카리", "느카리": "느카리",
    "lord_skrolk": "로드 스크롤크", "wh2_main_sc_skv_lord_skrolk": "로드 스크롤크", "skrolk": "로드 스크롤크",
    "karl_franz": "카를 프란츠", "wh_main_sc_emp_karl_franz": "카를 프란츠", "franz": "카를 프란츠"
}
