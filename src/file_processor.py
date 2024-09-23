import os
import pandas as pd
import numpy as np
import models
import sys

def resource_path(relative_path):
    """取得資源的絕對路徑，適用於開發和打包後的環境"""
    try:
        # PyInstaller 在打包後會將臨時路徑存放在 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        # 在開發環境中，基於當前文件的路徑來定位資源
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)


PLACEHOLDER_IMAGE = resource_path("image/placeholder_image.png")

def get_sheet_names(file_path):
    """讀取 Excel 檔案中的工作表名稱"""
    excel_data = pd.ExcelFile(file_path)
    return_sheet_name = excel_data.sheet_names
    return return_sheet_name  # 回傳工作表名稱列表


def process_file(file_path, sheet_name, model_type, x_unit, y_unit, custom_title):
    prompt_msg = ""  # 初始化提示訊息
    result = ""
    file_paths = ""

    try:
        # 讀取 Excel 資料
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        prompt_msg += f"讀取{model_type}資料成功\n"  # 記錄資料讀取成功

        # 確認是否存在 'Time' 和 'Cp' 欄位
        if 'Time' not in data.columns or 'Cp' not in data.columns:
            return {"Error": "'Time' 或 'Cp' 欄位不存在，請檢查檔案格式。"}, [
                PLACEHOLDER_IMAGE], prompt_msg + '輸入資料格式錯誤\n請確認資料表為[Time][Cp][Dose]\n'

        prompt_msg += "確認欄位成功\n"  # 記錄確認欄位成功

        # 將資料轉換為 NumPy 陣列
        time = data['Time'].to_numpy()  # 確保 "時間" 是 1D 陣列
        c_p = data['Cp'].to_numpy()  # 確保 "藥物濃度 Cp" 是 1D 陣列
        dose = data['Dose'].to_numpy()  # 讀取整個劑量數據

        # 刪除 Dose 為零或空值的行
        valid_indices = ~np.isnan(dose) & (dose != 0)
        if valid_indices.any():
            dose = dose[valid_indices][0]  # 提取過濾後的第一個有效劑量值
        else:
            return {"Error": "無有效劑量數據。"}, [PLACEHOLDER_IMAGE], prompt_msg + '請確認[Dose]欄位下只有一個有效值\n'

        prompt_msg += "劑量處理成功\n"  # 記錄劑量處理成功

        # 確認過濾後有足夠的數據
        if len(time) < 2:
            return {"Error": "清理後數據不足以進行分析。"}, [PLACEHOLDER_IMAGE], prompt_msg + '數據不足以進行分析\n'

        prompt_msg += "數據清理成功\n"  # 記錄數據清理成功

        # 根據選擇的模型類型調用不同的模型函數
        if model_type == "一室模型":
            result, file_paths = models.one_compartment_model(time, c_p, dose, x_unit, y_unit, custom_title)
            prompt_msg += "一室模型運算成功\n"
        elif model_type == "二室模型":
            result, file_paths = models.two_compartment_model(time, c_p, dose, x_unit, y_unit, custom_title)
            prompt_msg += "二室模型運算成功\n"

        # 如果模型返回 None，處理為錯誤
        if result is None or file_paths is None:
            return {"Error": "模型未返回有效結果。"}, [PLACEHOLDER_IMAGE], prompt_msg + '模型未回傳有效結果\n'

        return result, file_paths, prompt_msg + '模型分析成功\n'  # 返回結果和對應的圖表文件路徑，記錄最終成功訊息

    except Exception as e:
        return {"Error": f"模型計算出現錯誤: {e}"}, [PLACEHOLDER_IMAGE], prompt_msg + f"模型計算出現錯誤: {e}\n"


def run_interface(file_path, sheet_name, x_unit, y_unit, custom_title):
    # 呼叫處理函數並將結果格式化為輸出
    results_one, image_paths_one, message_one = process_file(file_path, sheet_name, "一室模型", x_unit, y_unit,
                                                             custom_title)
    prompt_message = message_one
    results_two, image_paths_two, message_two = process_file(file_path, sheet_name, "二室模型", x_unit, y_unit,
                                                             custom_title)
    prompt_message += message_two

    # 一室模型 名稱
    one_model_names = f"""
    Slope:
    k_e:
    Half-life:
    Intercept:
    Initial Concentration:
    Clearance:
    Volume of Distribution (V_d):
    AUC(0-t):
    AUC(0-finity):
    """

    # 一室模型 數值
    one_model_values = f"""
    {results_one.get('slope', 'N/A')}
    {results_one.get('k_e', 'N/A')}
    {results_one.get('half_life', 'N/A')}
    {results_one.get('intercept', 'N/A')}
    {results_one.get('initial_concentration', 'N/A')}
    {results_one.get('clearance', 'N/A')}
    {results_one.get('VD', 'N/A')}
    {results_one.get('AUC(0-t)', 'N/A')}
    {results_one.get('AUC(0-finity)', 'N/A')}
    """

    # 二室模型 名稱
    two_model_names = f"""
    a:
    Alpha:
    b:
    Beta:
    k_21:
    k_10:
    k_12:
    Half-life Alpha:
    Half-life Beta:
    Half-life k21:
    Half-life k10:
    Half-life k12:
    VDss:
    Clearance:
    AUC(0-t):
    AUC(0-finity):
    """

    # 二室模型 數值
    two_model_values = f"""
    {results_two.get('a', 'N/A')}
    {results_two.get('alpha', 'N/A')}
    {results_two.get('b', 'N/A')}
    {results_two.get('beta', 'N/A')}
    {results_two.get('k_21', 'N/A')}
    {results_two.get('k_10', 'N/A')}
    {results_two.get('k_12', 'N/A')}
    {results_two.get('half_life_alpha', 'N/A')}
    {results_two.get('half_life_beta', 'N/A')}
    {results_two.get('half_life_k21', 'N/A')}
    {results_two.get('half_life_k10', 'N/A')}
    {results_two.get('half_life_k12', 'N/A')}
    {results_two.get('VDss', 'N/A')}
    {results_two.get('clearance', 'N/A')}
    {results_two.get('AUC(0-t)', 'N/A')}
    {results_two.get('AUC(0-finity)', 'N/A')}
    """

    # 根據模型結果的錯誤狀況來決定提示訊息
    if "Error" in results_one and "Error" in results_two:
        prompt_message += "一室模型和二室模型均出現錯誤。"
    elif "Error" in results_one:
        prompt_message += "一室模型出現錯誤，但二室模型成功。"
    elif "Error" in results_two:
        prompt_message += "二室模型出現錯誤，但一室模型成功。"
    else:
        prompt_message += "一室模型和二室模型均成功完成。"

    return one_model_names, one_model_values, image_paths_one[0], two_model_names, two_model_values, image_paths_two[
        0], prompt_message


def save_result():
    a = 1
