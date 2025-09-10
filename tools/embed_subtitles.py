import os
import glob
import subprocess
import gradio as gr


def run_embed_subtitles(input_dir, output_dir, dry_run=False):
    """
    Embed subtitles from input directory to output directory using FFmpeg.
    
    Args:
        input_dir: Directory containing video files (.mp4)
        output_dir: Directory to save output .mkv files
        dry_run: If True, only print commands without executing
    
    Returns:
        Status message
    """
    if not input_dir or not output_dir:
        return "Please provide both input and output directories."
    
    input_dir = input_dir.strip().strip('"')
    output_dir = output_dir.strip().strip('"')
    
    if not os.path.exists(input_dir):
        return f"Input directory does not exist: {input_dir}"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .mp4 files in input directory
    video_files = glob.glob(os.path.join(input_dir, "*.mp4"))
    
    if not video_files:
        return f"No .mp4 files found in {input_dir}"
    
    results = []
    processed_count = 0
    
    for video_file in video_files:
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        sub_dir = os.path.join(input_dir, "Subs", base_name)
        
        # Check if we have subtitles in either location
        has_subs_dir = os.path.exists(sub_dir)
        same_dir_chi = os.path.join(os.path.dirname(video_file), f"{base_name}.chi.srt")
        same_dir_eng = os.path.join(os.path.dirname(video_file), f"{base_name}.eng.srt")
        has_same_dir_subs = os.path.exists(same_dir_chi) or os.path.exists(same_dir_eng)
        
        if not has_subs_dir and not has_same_dir_subs:
            results.append(f"No subtitle files found for {base_name}, skipping...")
            continue
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-y"]  # -y to overwrite output files
        inputs = ["-i", video_file]
        
        # Base mapping for video and audio
        mappings = ["-map", "0:v", "-map", "0:a", "-c:v", "copy", "-c:a", "copy"]
        
        # Remove metadata for title
        metadata = ["-metadata", "title="]
        
        subtitle_index = 1
        subtitle_mappings = []
        subtitle_metadata = []
        
        # Look for Chinese subtitles in two locations:
        # 1. Same directory as video with .chi.srt suffix (PRIORITY)
        # 2. In Subs/{basename}/ directory
        chi_subs = []
        
        # Pattern 1: Same directory with .chi.srt suffix (PRIORITY)
        same_dir_chi = os.path.join(os.path.dirname(video_file), f"{base_name}.chi.srt")
        if os.path.exists(same_dir_chi):
            chi_subs.append(same_dir_chi)
        
        # Pattern 2: Subs directory (fallback)
        if not chi_subs and os.path.exists(sub_dir):
            chi_patterns = ["*_Chinese.srt", "*_chi.srt", "*_ch.srt"]
            for pattern in chi_patterns:
                chi_subs.extend(glob.glob(os.path.join(sub_dir, pattern)))
        
        if chi_subs:
            inputs.extend(["-i", chi_subs[0]])
            subtitle_mappings.extend(["-map", f"{subtitle_index}:s"])
            subtitle_metadata.extend([
                f"-metadata:s:s:{subtitle_index-1}", "language=chi",
                f"-metadata:s:s:{subtitle_index-1}", "title=中文"
            ])
            subtitle_index += 1
        
        # Look for English subtitles in two locations:
        # 1. Same directory as video with .eng.srt suffix (PRIORITY)
        # 2. In Subs/{basename}/ directory
        eng_subs = []
        
        # Pattern 1: Same directory with .eng.srt suffix (PRIORITY)
        same_dir_eng = os.path.join(os.path.dirname(video_file), f"{base_name}.eng.srt")
        if os.path.exists(same_dir_eng):
            eng_subs.append(same_dir_eng)
        
        # Pattern 2: Subs directory (fallback)
        if not eng_subs and os.path.exists(sub_dir):
            eng_patterns = ["*_English.srt", "*_eng.srt", "*_en.srt"]
            for pattern in eng_patterns:
                eng_subs.extend(glob.glob(os.path.join(sub_dir, pattern)))
        
        if eng_subs:
            inputs.extend(["-i", eng_subs[0]])
            subtitle_mappings.extend(["-map", f"{subtitle_index}:s"])
            subtitle_metadata.extend([
                f"-metadata:s:s:{subtitle_index-1}", "language=eng",
                f"-metadata:s:s:{subtitle_index-1}", "title=English"
            ])
            subtitle_index += 1
        
        # If we found subtitles, add subtitle codec and default disposition
        if subtitle_index > 1:
            subtitle_mappings.extend(["-c:s", "srt", "-disposition:s:0", "+default"])
        
        # Output file
        output_file = os.path.join(output_dir, f"{base_name}.mkv")
        
        # Combine all command parts
        full_cmd = cmd + inputs + mappings + metadata + subtitle_mappings + subtitle_metadata + [output_file]
        
        if dry_run:
            cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in full_cmd)
            results.append(f"Command: {cmd_str}")
        else:
            try:
                subprocess.run(full_cmd, check=True, capture_output=True, text=True)
                results.append(f"Successfully processed: {base_name}.mkv")
                processed_count += 1
            except subprocess.CalledProcessError as e:
                error_msg = f"Error processing {base_name}: {e.stderr if e.stderr else str(e)}"
                results.append(error_msg)
    
    if dry_run:
        summary = f"Dry run completed. Found {len(video_files)} video file(s)."
    else:
        summary = f"Processing completed. Successfully processed {processed_count}/{len(video_files)} video file(s)."
    
    return summary + "\n\n" + "\n".join(results)


def draw_embed_subtitles():
    """
    Draw the UI for embed subtitles tool.
    
    Returns:
        Tuple of input components for the tool
    """
    with gr.Group():
        gr.Markdown("## Embed Subtitles Tool")
        gr.Markdown("Embed subtitle files into video files and convert to MKV format.")
        gr.Markdown("**Supported File Structures:**")
        gr.Markdown("input_dir/")
        gr.Markdown("├── video1.mp4")
        gr.Markdown("├── video1.chi.srt    ← PRIORITY")
        gr.Markdown("├── video1.eng.srt    ← PRIORITY")
        gr.Markdown("├── video2.mp4")
        gr.Markdown("├── Subs/")
        gr.Markdown("│   ├── video1/")
        gr.Markdown("│   │   ├── video1_Chinese.srt (or *_chi.srt, *_ch.srt)")
        gr.Markdown("│   │   └── video1_English.srt (or *_eng.srt, *_en.srt)")
        gr.Markdown("│   └── video2/")
        gr.Markdown("│       ├── video2_Chinese.srt")
        gr.Markdown("│       └── video2_English.srt")
        
        input_dir = gr.Textbox(
            label="Input Directory Path",
            placeholder="Enter the directory containing video files and Subs folder",
            lines=1
        )
        output_dir = gr.Textbox(
            label="Output Directory Path", 
            placeholder="Enter the directory to save output MKV files",
            lines=1
        )
        dry_run = gr.Checkbox(
            label="Dry Run", 
            value=False,
            info="Check to preview commands without executing them"
        )
        
        return input_dir, output_dir, dry_run