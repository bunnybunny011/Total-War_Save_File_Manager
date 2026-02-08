# 🎮 Total War Save Manager (토탈워 세이브 매니저)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**Total War Save Manager**는 토탈워 시리즈의 무분별하게 쌓이는 세이브 파일을 정리해주는 초경량 도구입니다. 
복잡한 게임별 규칙을 **'유니버셜 토크나이저(Universal Tokenizer)'** 기술로 통합하여, 구작(나폴레옹)부터 신작(파라오)까지 모든 토탈워 시리즈를 완벽하게 지원합니다.

> **v15.0 Update:** 바이너리 파싱을 제거하여 로딩 속도가 획기적으로 빨라졌으며(0.1초), 깨진 문자열(외계어) 문제가 완전히 해결되었습니다.

## ✨ 주요 기능

- **⚡ 초고속 스캔 (Instant Scan)**: 수천 개의 세이브 파일도 1초 이내에 로딩 완료.
- **🧠 유니버셜 토큰 분석**: 게임마다 다른 작명 규칙(년도, 계절, 월, 턴 등)을 스스로 패턴화하여 분석.
  - *예: Rome 2 (58 BC), Shogun 2 (Winter 1550), Warhammer (Turn 152) 모두 자동 대응.*
- **🛡️ 철통 같은 안전성**: 
  - `자동 저장(Auto Save)`, `빠른 저장(Quick Save)`은 절대 건드리지 않음.
  - 중복 파일은 삭제하지 않고 `_Backup` 폴더로 격리 (언제든 복구 가능).
- **📊 직관적인 정보**: 팩션/리더 이름 대신 **수정 날짜**와 **파일 크기**를 표시하여 정확한 식별 가능.
- **📂 캠페인 비율 정리**: 특정 캠페인 파일들을 3:1 비율(4개 중 1개만 유지)로 솎아내는 기능 지원.

## 🚀 시작하기

### 유저용 (실행 파일)
1. [Releases](https://github.com/bunnybunny011/Total-War_Save_File_Organizer/releases) 페이지에서 최신 `TotalWar_SaveManager.exe`를 다운로드합니다.
2. 실행 시 설치된 토탈워 게임을 자동으로 감지합니다.
3. 원하는 게임을 선택하고 **[중복 파일 정리]** 버튼을 누르세요.

### 개발자용 (소스 코드)
```bash
# 레포지토리 클론
git clone https://github.com/bunnybunny011/Total-War_Save_File_Organizer.git

# 가상환경 구축
python -m venv venv
.\venv\Scripts\activate

# 실행 (별도 라이브러리 설치 불필요 - 순수 Python 표준 라이브러리 사용)
python TotalWar_SaveManager.py
