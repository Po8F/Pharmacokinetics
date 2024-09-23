import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from image_processor import plot_one_compartment, plot_two_compartment

# 設定 matplotlib 使用的中文字體（例如，PingFang HK 字體）
plt.rcParams['font.sans-serif'] = ['PingFang HK']  # 使用 PingFang HK 字體來顯示中文
plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號


# 定義線性回歸函數
def linear_regression(time, cp, time_total):
    x = sm.add_constant(time)  # 添加常數項 (截距項)
    y = cp  # 藥物濃度
    model = sm.OLS(y, x)  # 使用普通最小二乘法建立回歸模型
    results = model.fit()  # 擬合模型

    # print(results.summary())  # 打印回歸結果摘要

    intercept = results.params[0]  # 截距
    slope = results.params[1]  # 斜率

    # 創建一個新的時間範圍，從 t=0 到最大時間值
    new_time_range = np.linspace(0, time_total, num=100)  # 從 0 到最大時間值生成 100 個點
    new_x = sm.add_constant(new_time_range)  # 添加常數項

    predicted_cp = results.predict(new_x)  # 使用模型進行預測

    return predicted_cp, intercept, slope, new_time_range  # 返回預測值、截距和斜率


# 一室模型函數
def one_compartment_model(time, cp, dose, x_unit, y_unit, custom_title="", ):
    ln_cp = np.log(cp)  # 計算藥物濃度的自然對數
    time_total = max(time)  # 獲取最大時間
    predicted_cp, ln_cp_0, slope, new_time_range = linear_regression(time, ln_cp, time_total)  # 進行線性回歸，取得預測結果

    plot_one_compartment(time, cp, new_time_range, predicted_cp, x_unit, y_unit, custom_title=custom_title)

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
        'slope': slope,
        'k_e': k_e,
        'half_life': half_life,
        'intercept': ln_cp_0,
        'initial_concentration': cp_0,
        'clearance': c_l,
        'VD': v_d,
        'AUC(0-t)': auc_observed,
        'AUC(0-finity)': auc_total
    }

    return results, ['one_compartment_model_ln.png',
                     'one_compartment_model.png'],  # 'One-compartment model analysis successful.'  # 返回計算結果和圖像


# 二室模型函數
def two_compartment_model(time, cp, dose, x_unit, y_unit, custom_title=""):
    ln_cp = np.log(cp)  # 計算藥物濃度的自然對數
    ln_cp_b_dataset = ln_cp[-3:]  # 取最後三個數據點作為後段回歸
    time_b_dataset = time[-3:]  # 取最後三個時間點

    # 如果後段資料不足，則回傳錯誤
    if len(time_b_dataset) < 2 or len(ln_cp_b_dataset) < 2:
        print("Error: 此資料集不適用於model3")
        return

    time_total = time[-1]  # 最大時間值

    # 進行後段回歸
    predicted_cp_b, ln_b, b_slope, new_time_range_b = linear_regression(time_b_dataset, ln_cp_b_dataset, time_total)
    b = np.exp(ln_b)  # 計算後段回歸的 b 參數

    # 計算 cp_i 值，用於前段回歸
    cp_i = []
    for t in time:
        a = b * np.exp(b_slope * t)
        cp_i.append(a)
    cp_i = np.array(cp_i).flatten()

    ln_cp_a_dataset = []
    time_a_dataset = []
    # 進行前段回歸
    for i in range(len(cp)):
        if cp[i] > cp_i[i]:  # 當實際濃度大於 cp_i 時，進行回歸
            # print(cp[i], cp_i[i])
            x = np.log(cp[i] - cp_i[i])
            # print(f'x: {x}')
            if x >= 0:
                ln_cp_a_dataset.append(ln_cp[i])
                time_a_dataset.append(time[i])

    ln_cp_a_dataset = np.array(ln_cp_a_dataset).flatten()  # 將前段回歸資料展平
    time_a_dataset = np.array(time_a_dataset).flatten()

    # 如果前段資料不足，則回傳錯誤
    if len(time_a_dataset) < 2 or len(ln_cp_a_dataset) < 2:
        print("Error: 此資料集不適用於model3")
        return  # '', '', 'The two-compartment model analysis does not fit this dataset.'

    # 進行前段回歸
    predicted_cp_a, ln_a, a_slope, new_time_range_a = linear_regression(time_a_dataset, ln_cp_a_dataset, time_total)
    a = np.exp(ln_a)  # 計算前段回歸的 a 參數
    # print(f'a = {a}, alpha = {a_slope}, b = {b}, beta = {b_slope}')

    # 去掉不符合的數據點
    min_predicted_cp_b = np.min(np.exp(predicted_cp_b))
    valid_indices_a = np.exp(predicted_cp_a) >= min_predicted_cp_b
    new_time_range_a = new_time_range_a[valid_indices_a]
    predicted_cp_a = predicted_cp_a[valid_indices_a]

    plot_two_compartment(time, cp, new_time_range_a, predicted_cp_a, new_time_range_b, predicted_cp_b, a, b, x_unit,
                         y_unit, custom_title=custom_title)

    # 計算相關參數
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

    # 計算AUC
    auc_observed = np.trapz(cp, time)
    auc_extrapolated = cp[-1] / (-b_slope)
    auc_total = auc_observed + auc_extrapolated

    # 將結果打包成字典
    results = {
        'a': a,
        'alpha': alpha,
        'b': b,
        'beta': beta,
        'k_21': k_21,
        'k_10': k_10,
        'k_12': k_12,
        'half_life_alpha': half_life_alpha,
        'half_life_beta': half_life_beta,
        'half_life_k21': half_life_k21,
        'half_life_k10': half_life_k10,
        'half_life_k12': half_life_k12,
        'AUC(0-t)': auc_observed,
        'AUC(0-finity)': auc_total,
        'Volume': volume,
        'VDss': vd_ss,
        'clearance': c_l,
        'Cmax': max(cp)
    }

    return results, ['two_compartment_model.png'],  # 'Two-compartment model analysis successful.'  # 返回計算結果和圖像
