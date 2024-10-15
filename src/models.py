import numpy as np
import statsmodels.api as sm
from image_processor import plot_one_compartment, plot_two_compartment
from config import TEMP_FOLDER_PATH

# 定義線性回歸函數
def linear_regression(time, cp, time_total):
    x = sm.add_constant(time)  # 添加常數項 (截距項)
    y = cp  # 藥物濃度
    model = sm.OLS(y, x)  # 使用普通最小平方法建立回歸模型
    results = model.fit()  # 擬合模型

    intercept = results.params[0]  # 截距
    slope = results.params[1]  # 斜率

    # 創建一個新的時間範圍，從 t=0 到最大時間值
    new_time_range = np.linspace(0, time_total, num=100)  # 從 0 到最大時間值生成 100 個點
    new_x = sm.add_constant(new_time_range)  # 添加常數項

    predicted_cp = results.predict(new_x)  # 使用模型進行預測

    return predicted_cp, round(intercept, 4), round(slope, 4), new_time_range  # 返回預測值、截距和斜率


# 一室模型函數
def one_compartment_model(time, cp, dose, x_unit, y_unit, dose_unit, custom_title="", average=False):
    ln_cp = np.log(cp)  # 計算藥物濃度的自然對數
    time_total = max(time)  # 獲取最大時間
    predicted_cp, ln_cp_0, slope, new_time_range = linear_regression(time, ln_cp, time_total)  # 進行線性回歸，取得預測結果

    plot_one_compartment(time, cp, dose, new_time_range, predicted_cp, x_unit, y_unit, dose_unit,
                         custom_title=custom_title, average=average)

    # 計算 AUC (區域下面積)
    auc_observed = np.trapz(cp, time)  # 使用梯形法則計算觀察到的 AUC
    auc_extrapolated = cp[-1] / (-slope)  # 計算外推的 AUC
    auc_total = auc_observed + auc_extrapolated  # 總 AUC = 觀察到的 AUC + 外推的 AUC

    cp_0 = np.exp(ln_cp_0)  # 初始濃度
    k_e = -slope  # 消除速率常數
    v_d = dose / cp_0  # 分布容積
    half_life = 0.693 / k_e  # 半衰期
    c_l = k_e * v_d  # 清除率

    # 將結果打包成字典
    results = {
        'slope': round(slope, 4),
        'k_e': round(k_e, 4),
        'half_life': round(half_life, 4),
        'intercept': round(ln_cp_0, 4),
        'initial_concentration': round(cp_0, 4),
        'clearance': round(c_l, 4),
        'VD': round(v_d, 4),
        'AUC(0-t)': round(auc_observed, 4),
        'AUC(0-finity)': round(auc_total, 4)
    }

    # 修改 return 部分，根據 average 參數選擇不同的圖像名稱
    filename = f'{TEMP_FOLDER_PATH}/one_compartment_model_ln_avg.png' if average else (
        f'{TEMP_FOLDER_PATH}/one_compartment_model_ln.png')

    return results, [filename]  # 返回計算結果和圖像


# 二室模型函數
def two_compartment_model(time, cp, dose, x_unit, y_unit, dose_unit, inflection_point, custom_title="", average=False):
    ln_cp = np.log(cp)

    # 找到 inflection_point 在 time 數組中的索引
    inflection_index = np.where(time == inflection_point)[0][0]
    ln_cp_b_dataset = ln_cp[inflection_index:]
    time_b_dataset = time[inflection_index:]

    # 如果後段資料不足，則回傳錯誤
    if len(time_b_dataset) < 2 or len(ln_cp_b_dataset) < 2:
        print("Error: 此資料集不適用於model3")
        return

    time_total = time[-1]

    predicted_cp_b, ln_b, b_slope, new_time_range_b = linear_regression(time_b_dataset, ln_cp_b_dataset, time_total)
    b = np.exp(ln_b)

    cp_i = [b * np.exp(b_slope * t) for t in time]
    cp_i = np.array(cp_i).flatten()

    ln_cp_a_dataset = []
    time_a_dataset = []

    for i in range(len(cp)):
        if cp[i] > cp_i[i]:
            x = np.log(cp[i] - cp_i[i])
            if x < 0:
                break
            ln_cp_a_dataset.append(ln_cp[i])
            time_a_dataset.append(time[i])

    ln_cp_a_dataset = np.array(ln_cp_a_dataset).flatten()
    time_a_dataset = np.array(time_a_dataset).flatten()

    if len(time_a_dataset) < 2 or len(ln_cp_a_dataset) < 2:
        print("Error: 此資料集不適用於model3")
        return

    predicted_cp_a, ln_a, a_slope, new_time_range_a = linear_regression(time_a_dataset, ln_cp_a_dataset, time_total)
    a = np.exp(ln_a)

    min_predicted_cp_b = np.min(np.exp(predicted_cp_b))
    valid_indices_a = np.exp(predicted_cp_a) >= min_predicted_cp_b
    new_time_range_a = new_time_range_a[valid_indices_a]
    predicted_cp_a = predicted_cp_a[valid_indices_a]

    plot_two_compartment(time, cp, dose, new_time_range_a, predicted_cp_a, new_time_range_b, predicted_cp_b, a, b,
                         x_unit, y_unit, dose_unit, custom_title=custom_title, average=average)

    alpha = -a_slope
    beta = -b_slope

    k_21 = (a * beta + b * alpha) / (a + b)
    k_10 = (alpha * beta) / k_21
    k_12 = alpha + beta - k_21 - k_10
    half_life_alpha = 0.693 / alpha
    half_life_beta = 0.693 / beta
    half_life_k21 = 0.693 / k_21
    half_life_k10 = 0.693 / k_10
    half_life_k12 = 0.693 / k_12
    volume = dose / (a + b)
    vd_ss = volume * (1 + (k_12 / k_21))
    c_l = k_10 * volume

    auc_observed = np.trapz(cp, time)
    auc_extrapolated = cp[-1] / (-b_slope)
    auc_total = auc_observed + auc_extrapolated

    results = {
        'a': round(a, 4),
        'alpha': round(alpha, 4),
        'b': round(b, 4),
        'beta': round(beta, 4),
        'k_21': round(k_21, 4),
        'k_10': round(k_10, 4),
        'k_12': round(k_12, 4),
        'half_life_alpha': round(half_life_alpha, 4),
        'half_life_beta': round(half_life_beta, 4),
        'half_life_k21': round(half_life_k21, 4),
        'half_life_k10': round(half_life_k10, 4),
        'half_life_k12': round(half_life_k12, 4),
        'AUC(0-t)': round(auc_observed, 4),
        'AUC(0-finity)': round(auc_total, 4),
        'Volume': round(volume, 4),
        'VDss': round(vd_ss, 4),
        'clearance': round(c_l, 4),
        'Cmax': round(max(cp), 4)
    }

    filename = f'{TEMP_FOLDER_PATH}/two_compartment_model_avg.png' if average else (
        f'{TEMP_FOLDER_PATH}/two_compartment_model.png')

    return results, [filename]
