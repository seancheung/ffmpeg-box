import gradio as gr
from tools.convert_video import draw_convert_video, run_convert_video
from tools.embed_subtitles import draw_embed_subtitles, run_embed_subtitles
from tools.cut_video import draw_cut_video, run_cut_video
from tools.merge_videos import draw_merge_videos, run_merge_videos
from tools.split_subtitle import draw_split_subtitle, run_split_subtitle

tools = [
    "Select a tool...",
    "Convert Video",
    "Merge Videos",
    "Cut Video",
    "Embed Subtitles",
    "Split Subtitle",
]

with gr.Blocks(title="FFmpeg Box - Video Processing Tools") as app:
    gr.Markdown("# 🎬 FFmpeg Box")
    gr.Markdown("A comprehensive video processing toolkit powered by FFmpeg")

    tool_selector = gr.Dropdown(
        choices=tools,
        label="Select Tool",
        value="Select a tool...",
        interactive=True,
    )

    @gr.render(inputs=tool_selector)
    def show_tool_interface(tool_name):
        match tool_name:
            case "Convert Video":
                tool_inputs = draw_convert_video()
                run_button.click(fn=run_convert_video, inputs=tool_inputs)
            case "Cut Video":
                tool_inputs = draw_cut_video()
                run_button.click(fn=run_cut_video, inputs=tool_inputs)
            case "Embed Subtitles":
                tool_inputs = draw_embed_subtitles()
                run_button.click(fn=run_embed_subtitles, inputs=tool_inputs)
            case "Merge Videos":
                tool_inputs = draw_merge_videos()
                run_button.click(fn=run_merge_videos, inputs=tool_inputs)
            case "Split Subtitle":
                tool_inputs = draw_split_subtitle()
                run_button.click(fn=run_split_subtitle, inputs=tool_inputs)
            case _:
                gr.Markdown("## Welcome to FFmpeg Box")
                gr.Markdown(
                    "Select a tool from the dropdown above to get started with video processing."
                )

    run_button = gr.Button(value="Run", variant="primary")


if __name__ == "__main__":
    app.launch()
