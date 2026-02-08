import tkinter as tk
from gui_main import SaveManagerGUI

def main():
    """프로그램의 메인 엔트리 포인트입니다."""
    root = tk.Tk()
    # 고해상도 DPI 설정 (Windows)
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
        
    app = SaveManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
