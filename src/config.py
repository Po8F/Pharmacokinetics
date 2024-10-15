import os
import sys

def get_base_path():
    """取得可執行檔的基礎路徑"""
    if getattr(sys, 'frozen', False):
        # 如果程式被 PyInstaller 打包，使用 sys.executable 指向可執行檔所在的路徑
        base_path = os.path.dirname(sys.executable)
    else:
        # 在開發環境中，使用當前文件的路徑
        base_path = os.path.abspath(os.path.dirname(__file__))
    return base_path

# 設定 TEMP_FOLDER_PATH 指向與可執行檔相同的目錄
TEMP_FOLDER_PATH = os.path.join(get_base_path(), "PharmacokineticAnalysis_temp")

# 檢查並創建資料夾
if not os.path.exists(TEMP_FOLDER_PATH):
    os.makedirs(TEMP_FOLDER_PATH)

print(f"TEMP_FOLDER_PATH: {TEMP_FOLDER_PATH}")
