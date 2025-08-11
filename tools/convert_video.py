import gradio as gr
import subprocess


def run_convert_video(
    input_path,
    output_path,
    quality,
    crf,
    bitrate,
    subtitle,
    hevc,
    gpu,
    start_time,
    end_time,
    deinterlace,
    dedupe,
    mono,
):
    encoding = "libx264"
    if hevc:
        encoding = "hevc_nvenc" if gpu else "libx265"
    else:
        encoding = "h264_nvenc" if gpu else "libx264"

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-hwaccel",
        "cuda",
        "-i",
        input_path.strip('"'),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "0:a:0",
        "-c:a",
        "aac",
        "-c:v",
        encoding,
        "-preset",
        "slow",
    ]

    if subtitle:
        cmd.append("-map")
        cmd.append("0:s?")
        cmd.append("-c:s")
        cmd.append("copy")

    if quality == "CRF":
        cmd.append("-crf")
        cmd.append(str(crf))
    elif quality == "Bitrate":
        cmd.append("-b:v")
        cmd.append(str(bitrate))

    if start_time:
        cmd.insert(4, "-ss")
        cmd.insert(5, start_time)
    if end_time:
        cmd.insert(4, "-to")
        cmd.insert(5, end_time)

    if gpu:
        cmd.append("-profile:v")
        cmd.append("main")
        cmd.append("-rc")
        cmd.append("vbr")
        cmd.append("-qmin")
        cmd.append("18")

    filters = []

    if deinterlace:
        if gpu:
            filters.append("hwupload_cuda")
            filters.append("bwdif_cuda=0")
            filters.append("hwdownload")
            filters.append("format=nv12")
            filters.append("format=yuv420p")
        else:
            filters.append("bwdif=0")

    if dedupe:
        filters.append("mpdecimate")
        cmd.append("-vsync")
        cmd.append("vfr")

    if mono:
        filters.append("stereo3d=sbsl:ml")
        cmd.append("-metadata:s:v:0")
        cmd.append('stereo_mode="mono"')

    if filters:
        cmd.append("-vf")
        cmd.append(",".join(filters))

    cmd.append(output_path.strip('"'))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e}")
        return f"Error converting video: {e}"

def draw_convert_video():
    with gr.Group():
        gr.Markdown("## Convert Video Tool", padding=True)
        input_path = gr.Textbox(label="Enter Video File Path")
        output_path = gr.Textbox(label="Enter Output File Path")
        with gr.Row():
            quality = gr.Radio(
                label="Quality",
                choices=["Default", "CRF", "Bitrate"],
                value="Default",
            )
            crf = gr.Slider(
                label="CRF",
                minimum=0,
                maximum=51,
                value=23,
                step=1,
                visible=False,
            )
            bitrate = gr.Slider(
                label="Bitrate",
                minimum=100,
                maximum=8000,
                value=2000,
                step=100,
                visible=False,
            )

        quality.change(
            fn=lambda x: (
                gr.update(visible=x == "CRF"),
                gr.update(visible=x == "Bitrate"),
            ),
            inputs=[quality],
            outputs=[crf, bitrate],
        )

        with gr.Tab("Basic"):
            with gr.Row():
                subtitle = gr.Checkbox(label="Subtitle", value=False)
            with gr.Row():
                hevc = gr.Checkbox(label="HEVC", value=False)
                gpu = gr.Checkbox(label="GPU", value=False)
            with gr.Row():
                start_time = gr.Textbox(label="Start Time")
                end_time = gr.Textbox(label="End Time")
        with gr.Tab("Advanced"):
            with gr.Row():
                deinterlace = gr.Checkbox(label="Deinterlace", value=False)
                dedupe = gr.Checkbox(label="Dedupe", value=False)
                mono = gr.Checkbox(label="Mono", value=False)
        return (
            input_path,
            output_path,
            quality,
            crf,
            bitrate,
            subtitle,
            hevc,
            gpu,
            start_time,
            end_time,
            deinterlace,
            dedupe,
            mono,
        )
