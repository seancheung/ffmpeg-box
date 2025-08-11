import subprocess
import gradio as gr


def run_cut_video(input_path, output_path, timestampes):
    times = timestampes.split("\n")
    output_path = output_path.strip('"')
    for i, time in enumerate(times):
        start_time, end_time = time.split(",")
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-hwaccel",
            "cuda",
            "-i",
            input_path.strip('"'),
            "-ss",
            start_time,
            "-to",
            end_time,
            output_path.replace("?", str(i + 1)),
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cutting video: {e}")
            return f"Error cutting video: {e}"


def draw_cut_video():
    with gr.Group():
        gr.Markdown("## Cut Video Tool", padding=True)
        input_path = gr.Textbox(label="Enter Video File Path")
        output_path = gr.Textbox(label="Enter Output File Path", value="?.mp4")
        timestampes = gr.TextArea(
            label="Enter Timestampes",
            lines=10,
            value="00:00:00,00:00:00\n00:00:00,00:00:00",
        )
        return input_path, output_path, timestampes
