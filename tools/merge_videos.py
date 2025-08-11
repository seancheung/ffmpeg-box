import gradio as gr
import os
import subprocess


def run_merge_videos(input_path, output_path):
    output_path = output_path.strip('"')

    concat_list = os.path.join(
        os.path.dirname(output_path), f"{os.path.basename(output_path)}.txt"
    )
    with open(concat_list, "w", encoding="utf-8") as f:
        for input_file in input_path.split("\n"):
            file_path = input_file.strip('"')
            f.write(f"file '{file_path}'\n")
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-hwaccel",
            "cuda",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list,
            output_path,
        ]
    )
    os.remove(concat_list)


def draw_merge_videos():
    with gr.Group():
        gr.Markdown("## Merge Videos Tool", padding=True)
        input_path = gr.TextArea(
            label="Enter Video Files Path", lines=10, value="01.mp4\n02.mp4\n03.mp4"
        )
        output_path = gr.Textbox(label="Enter Output File Path")
        return input_path, output_path
