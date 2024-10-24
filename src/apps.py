import file_processor
import gradio as gr


def update_sheet_names(file_path):
    try:
        sheet_names = file_processor.get_sheet_names(file_path)
        return gr.Dropdown(choices=sheet_names, value=sheet_names[0])
    except Exception as e:
        print(f"Error reading file: {e}")
        return gr.Dropdown(choices=[], value="")


def update_inflection_point(file_path, sheet_name):
    try:
        unique_times = file_processor.get_time_columns(file_path, sheet_name)
        return gr.Dropdown(choices=unique_times, value=unique_times[-1])
    except Exception as e:
        print(f"Error reading file: {e}")
        return gr.Dropdown(choices=[], value="")


def reset_all():
    one_model_output = ("", "", None, "", "", None)
    two_model_output = ("", "", None, "", "", None)
    prompt_message = ("",)
    interface_output = (
        None,
        "",
        "",
        "Minute",
        "mg/L",
        "mg",
        None
    )

    return one_model_output + two_model_output + prompt_message + interface_output


# 使用 Blocks 和 Row/Column 佈局
with gr.Blocks() as demo:
    gr.Markdown("## 藥物濃度分析工具")

    # 設定檔案上傳元件和下拉選單
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="選擇 Excel 檔案", type="filepath", container=False)
        with gr.Column():
            sheet_name_input = gr.Dropdown(label="選擇工作表名稱", choices=[""], interactive=True,
                                           allow_custom_value=False)
            title_input = gr.Textbox(label="設定回歸圖標題", placeholder="請輸入資料實驗名稱(可留空)", interactive=True)
            with gr.Row():
                x_unit = gr.Dropdown(label="X", choices=["Second", "Minute", "Hour", "day"], value="Minute",
                                     interactive=True, allow_custom_value=False)
                y_unit = gr.Dropdown(label="Y", choices=["g/L", "mg/L", "µg/L", "ng/L"], value="mg/L", interactive=True,
                                     allow_custom_value=False)
                dose_unit = gr.Dropdown(label="dose", choices=["g", "mg", "µg", "ng"], value="mg",
                                        interactive=True, allow_custom_value=False)
            with gr.Row():
                inflection_point = gr.Dropdown(label="轉折點資料集拆分(時間點)", choices=[""], interactive=True,
                                               allow_custom_value=False)
        with gr.Column():
            information_output = gr.Textbox(label="Prompt message", interactive=False, container=False)

    run_button = gr.Button("Analyze")
    with gr.Row():
        reset_button = gr.Button("Reset")
        save_button = gr.Button("Save(image & .xlsx)")

    # 左右佈局：一室模型在左，二室模型在右
    with gr.Row():
        # 一室模型平均值佈局
        with gr.Column():
            gr.Markdown("### 一室模型結果 (平均值)")
            image_output_one_avg = gr.Image(label="一室模型圖表 (平均值)")
            with gr.Row():
                one_model_value_name_avg = gr.Textbox(label="一室模型參數 (平均值)", interactive=False, lines=10,
                                                      scale=4)
                one_model_value_output_avg = gr.Textbox(label="輸出數值 (平均值)", interactive=False, lines=10, scale=6)
        # 二室模型平均值佈局
        with gr.Column():
            gr.Markdown("### 二室模型結果 (平均值)")
            image_output_two_avg = gr.Image(label="二室模型圖表 (平均值)")
            with gr.Row():
                two_model_value_name_avg = gr.Textbox(label="二室模型參數 (平均值)", interactive=False, lines=10,
                                                      scale=4)
                two_model_value_output_avg = gr.Textbox(label="輸出數值 (平均值)", interactive=False, lines=10, scale=6)
    with gr.Row():
        # 一室模型原始數據佈局
        with gr.Column():
            gr.Markdown("### 一室模型結果 (原始數據)")
            image_output_one = gr.Image(label="一室模型圖表 (原始數據)")
            with gr.Row():
                one_model_value_name = gr.Textbox(label="一室模型參數 (原始數據)", interactive=False, lines=10, scale=4)
                one_model_value_output = gr.Textbox(label="輸出數值 (原始數據)", interactive=False, lines=10, scale=6)

        # 二室模型原始數據佈局
        with gr.Column():
            gr.Markdown("### 二室模型結果 (原始數據)")
            image_output_two = gr.Image(label="二室模型圖表 (原始數據)")
            with gr.Row():
                two_model_value_name = gr.Textbox(label="二室模型參數 (原始數據)", interactive=False, lines=10, scale=4)
                two_model_value_output = gr.Textbox(label="輸出數值 (原始數據)", interactive=False, lines=10, scale=6)

    # 將更新下拉選單的函數綁定到檔案上傳事件
    file_input.change(update_sheet_names, inputs=file_input, outputs=sheet_name_input)
    file_input.clear(update_sheet_names, inputs=file_input, outputs=sheet_name_input)

    sheet_name_input.change(update_inflection_point, inputs=[file_input, sheet_name_input], outputs=inflection_point)

    # 設定按鈕事件
    run_button.click(
        file_processor.run_interface,
        inputs=[file_input, sheet_name_input, x_unit, y_unit, dose_unit, inflection_point, title_input],
        outputs=[one_model_value_name_avg, one_model_value_output_avg, image_output_one_avg,
                 one_model_value_name, one_model_value_output, image_output_one,
                 two_model_value_name_avg, two_model_value_output_avg, image_output_two_avg,
                 two_model_value_name, two_model_value_output, image_output_two,
                 information_output]
    )
    reset_button.click(
        reset_all,
        inputs=[],
        outputs=[one_model_value_name_avg, one_model_value_output_avg, image_output_one_avg,
                 one_model_value_name, one_model_value_output, image_output_one,
                 two_model_value_name_avg, two_model_value_output_avg, image_output_two_avg,
                 two_model_value_name, two_model_value_output, image_output_two,
                 information_output, file_input, sheet_name_input, title_input, x_unit, y_unit, dose_unit,
                 inflection_point]
    )
    save_button.click(
        file_processor.save_file,
        inputs=[title_input,
                one_model_value_name, two_model_value_name,
                one_model_value_output, two_model_value_output,
                one_model_value_output_avg, two_model_value_output_avg],
        outputs=[]
    )

demo.launch(share=False, inbrowser=True)
