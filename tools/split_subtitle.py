from io import StringIO
from pathlib import Path
import gradio as gr


def run_split_subtitle(input_path):
    input_path = input_path.strip('"')
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    group = []
    langs = []

    for line in lines:
        line = line.strip("\n")
        if not line.strip():
            for i in range(len(group) - 2):
                if len(langs) <= i:
                    langs.append(StringIO())
                langs[i].write(f"{group[0]}\n")
                langs[i].write(f"{group[1]}\n")
                langs[i].write(f"{group[i + 2]}\n")
                langs[i].write("\n")
            group = []
        else:
            group.append(line)

    file_info = Path(input_path)
    for index, lang in enumerate(langs, start=1):
        output_path = file_info.parent / f"{file_info.stem} ({index}){file_info.suffix}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(lang.getvalue())


def draw_split_subtitle():
    with gr.Group():
        gr.Markdown("## Split Multilingual Subtitle Tool", padding=True)
        input_path = gr.Textbox(label="Enter Subtitle File Path")
        return input_path
