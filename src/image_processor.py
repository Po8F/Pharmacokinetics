import matplotlib.pyplot as plt
import numpy as np
import platform
from config import TEMP_FOLDER_PATH

# 根據操作系統設置字體
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['PingFang HK']  # 使用 PingFang HK 字體來顯示中文
elif platform.system() == 'Windows':  # Windows
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微軟雅黑字體顯示中文
else:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # Linux 或其他系統的默認字體

plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號


def plot_one_compartment(time, cp, dose, new_time_range, predicted_cp, x_unit, y_unit, dose_unit, custom_title=""):
    title = f'One Compartment Model(dose : {dose} {dose_unit}) - {custom_title}' if custom_title else f'One Compartment Model(dose : {dose} {dose_unit})'
    filename = f'{TEMP_FOLDER_PATH}/one_compartment_model_ln.png'

    # 繪製實際藥物濃度(自然對數)與預測藥物濃度
    plt.figure(figsize=(10, 6))
    plt.plot(time, np.log(cp), 'o-', label='實際藥物濃度(Actual Drug Concentration)\n(自然對數)')
    plt.plot(new_time_range, predicted_cp, 'r--', label='預測藥物濃度')
    plt.xlabel(f'時間 ({x_unit})')
    plt.ylabel(f'藥物濃度 Cp ({y_unit})')
    plt.title(title)
    plt.legend()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_two_compartment(time, cp, dose, new_time_range_a, predicted_cp_a, new_time_range_b, predicted_cp_b, a, b,
                         x_unit, y_unit, dose_unit, custom_title=""):
    title = f'Two Compartment Model(dose : {dose} {dose_unit}) - {custom_title}' if custom_title else f'Two Compartment Model(dose : {dose} {dose_unit})'
    filename = f'{TEMP_FOLDER_PATH}/two_compartment_model.png'

    min_predicted_cp_b = np.min(np.exp(predicted_cp_b))
    # 設定 y 軸範圍
    min_ln_cp = max(np.min(cp[cp > 0]), min_predicted_cp_b) / 2
    max_ln_cp = max(cp) * 2

    # 繪製二室模型圖表
    plt.figure(figsize=(10, 6))
    plt.plot(time, cp, 'o-', label='實際藥物濃度(Actual Drug Concentration)')
    plt.plot(new_time_range_a, np.exp(predicted_cp_a), 'r--', label='前段預測藥物濃度')
    plt.plot(new_time_range_b, np.exp(predicted_cp_b), 'g--', label='後段預測藥物濃度')

    plt.scatter(0, b, color='green', s=50, zorder=5)  # 標記 b
    plt.scatter(0, a, color='red', s=50, zorder=5)  # 標記 a

    plt.text(0, b, f'b 線 t=0 濃度: {b:.2f}', color='green', verticalalignment='bottom', horizontalalignment='center')
    plt.text(0, a, f'a 線 t=0 濃度: {a:.2f}', color='red', verticalalignment='top', horizontalalignment='center')

    plt.yscale('log')  # 使用對數刻度

    plt.ylim(bottom=min_ln_cp, top=max_ln_cp)  # 設定 y 軸範圍

    ticks = [0.1, 0.5, 1, 5, 10, 50, 100]  # y 軸刻度
    ticks = [tick for tick in ticks if min_ln_cp <= tick <= max_ln_cp]
    plt.yticks(ticks, ['{:.2f}'.format(tick) for tick in ticks])

    plt.xlabel(f'時間({x_unit})')
    plt.ylabel(f'藥物濃度 Cp ({y_unit})')
    plt.title(title)
    plt.legend()
    plt.savefig(filename, dpi=300)  # 保存圖像
    plt.close()
