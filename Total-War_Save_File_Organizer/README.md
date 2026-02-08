# 🎮 Total War Save Manager (토탈워 세이브 매니저)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

**Total War Save Manager**는 토탈워 시리즈의 중복된 세이브 파일을 지능적으로 분석하여 정리해주는 도구입니다. 같은 턴의 여러 세이브 중 최신 파일만 남기고 백업하여 디스크 용량을 획기적으로 절약합니다.

## ✨ 주요 기능

- **멀티 게임 자동 탐지**: Rome 2, Three Kingdoms, Warhammer 등 모든 토탈워 시리즈 지원.
- **지능형 정리 전략**: 숫자형, 계절형, 추수형 등 게임별 작명 규칙에 따른 최적화된 정리.
- **안전한 백업**: 파일을 삭제하지 않고 `backup` 폴더로 이동시켜 언제든 복구 가능.
- **편리한 GUI**: 마우스 클릭만으로 간편하게 조작.
- **자동 검토**: 정리 완료 후 백업 폴더를 자동으로 열어 결과를 즉시 확인 가능.

## 🚀 시작하기

### 유저용 (실행 파일)
1. [Releases](https://github.com/bunnybunny011/Total-War_Save_File_Organizer/releases) 페이지에서 `TotalWar_SaveManager.exe`를 다운로드합니다.
2. 실행 후 목록에서 게임을 선택하고 **정리 시작**을 누르세요.

### 개발자용 (소스 코드)
```bash
# 가상환경 구축
python -m venv venv
.\venv\Scripts\activate

# 의존성 설치
pip install pyinstaller

# 실행
python TotalWar_SaveManager.py
```

## 📸 ScreenShot

<p align="center">
  <img src="https://github.com/user-attachments/assets/c99c7b9e-2271-4da7-9f49-923390517fe2"width="600" alt="Total War Save Manager Screenshot" />
</p>

## 📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.
