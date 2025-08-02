import os
import ffmpeg as ffmpeg_py
from yt_dlp import YoutubeDL
import whisper
import json
import tempfile
from gtts import gTTS

# Explicitly point to the ffmpeg executable
ffmpeg_executable_path = os.path.abspath("VideoClipper/ffmpeg/bin/ffmpeg.exe")

def download_video(url, output_path="."):
    """Downloads a video from a URL and returns the path to the downloaded file."""
    ydl_opts = {
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "ffmpeg_location": ffmpeg_executable_path
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def transcribe_audio(video_path, model_name="base"):
    """Transcribes the audio of a video using OpenAI Whisper and returns segments with timestamps."""
    os.environ["FFMPEG_PATH"] = ffmpeg_executable_path
    # Add ffmpeg to PATH for whisper
    os.environ["PATH"] += os.pathsep + ffmpeg_executable_path.replace("ffmpeg.exe", "")
    model = whisper.load_model(model_name)
    result = model.transcribe(video_path)
    return result['segments']

def generate_srt(segments, srt_path):
    """Generate an SRT subtitle file from transcription segments."""
    def format_timestamp(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, start=1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text'].replace('\n', ' ')
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

def text_to_speech(text, lang='en'):
    """Generate speech audio from text using gTTS."""
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def burn_subtitles_and_narration(clip_path, srt_path, narration_audio_path=None, output_path=None):
    """Burn subtitles and optionally narration audio into a video clip."""
    if output_path is None:
        base, ext = os.path.splitext(clip_path)
        output_path = f"{base}_subtitled{ext}"

    input_video = ffmpeg_py.input(clip_path)
    video = input_video.video.filter('subtitles', srt_path)

    if narration_audio_path:
        narration_audio = ffmpeg_py.input(narration_audio_path)
        audio = ffmpeg_py.filter([input_video.audio, narration_audio], 'amix', inputs=2, duration='first')
    else:
        audio = input_video.audio

    out = ffmpeg_py.output(video, audio, output_path, vcodec='libx264', acodec='aac', strict='experimental')
    out.run(overwrite_output=True)
    print(f"Created subtitled video: {output_path}")
    return output_path

def cut_video_into_clips(video_path, clip_duration=60, output_dir="output", lang='en'):
    """
    Transcribes a video, then cuts it into fixed-duration clips with narration and subtitles.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Transcribing the full video... (This may take a while)")
    all_segments = transcribe_audio(video_path)
    if not all_segments:
        print("Transcription failed. Cannot proceed with clipping.")
        return []

    try:
        import subprocess
        probe_cmd = [ffmpeg_executable_path.replace("ffmpeg.exe", "ffprobe.exe"), '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        total_duration = float(result.stdout.strip())
    except Exception as e:
        print(f"Error probing video file: {e}")
        return []

    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    final_clip_paths = []

    num_clips = int(total_duration // clip_duration) + (1 if total_duration % clip_duration > 0 else 0)

    for i in range(num_clips):
        clip_start_time = i * clip_duration
        clip_end_time = min((i + 1) * clip_duration, total_duration)
        current_clip_duration = clip_end_time - clip_start_time

        print(f"Processing clip {i + 1}/{num_clips} ({clip_start_time:.2f}s to {clip_end_time:.2f}s)")

        # 1. Gather text for the current clip
        clip_segments = []
        full_text = ""
        for seg in all_segments:
            # Check for overlap between segment and clip time range
            if seg['start'] < clip_end_time and seg['end'] > clip_start_time:
                text = seg['text'].strip()
                if text:
                    full_text += text + " "
                    # Adjust segment timestamps to be relative to the clip's start time
                    relative_start = max(0, seg['start'] - clip_start_time)
                    relative_end = min(current_clip_duration, seg['end'] - clip_start_time)
                    clip_segments.append({
                        'start': relative_start,
                        'end': relative_end,
                        'text': text
                    })

        if not full_text.strip():
            print(f"No text found for clip {i + 1}. Skipping narration and subtitles.")
            # Still, we need to cut the video
            clip_path = os.path.join(output_dir, f"{base_filename}_clip_{i + 1}.mp4")
            try:
                (ffmpeg_py
                 .input(video_path, ss=clip_start_time, t=current_clip_duration)
                 .output(clip_path, vcodec='libx264', acodec='aac', strict='experimental')
                 .run(overwrite_output=True, capture_stdout=True, capture_stderr=True))
                final_clip_paths.append(clip_path)
                print(f"Created clip (no text): {clip_path}")
            except Exception as e:
                print(f"Error creating raw clip {i+1}: {e}")
            continue


        # 2. Cut the raw video clip
        raw_clip_path = os.path.join(output_dir, f"{base_filename}_raw_clip_{i + 1}.mp4")
        try:
            (ffmpeg_py
             .input(video_path, ss=clip_start_time, t=current_clip_duration)
             .output(raw_clip_path, vcodec='libx264', acodec='aac', strict='experimental')
             .run(overwrite_output=True, capture_stdout=True, capture_stderr=True))
            print(f"Created raw clip: {raw_clip_path}")
        except Exception as e:
            print(f"Error creating raw clip {i+1}: {e}")
            continue

        # 3. Generate SRT subtitles for the clip
        srt_path = os.path.join(output_dir, f"{base_filename}_clip_{i + 1}.srt")
        generate_srt(clip_segments, srt_path)
        print(f"Generated SRT: {srt_path}")

        # 4. Generate narration audio
        narration_audio_path = None
        try:
            print("Generating narration...")
            narration_audio_path = text_to_speech(full_text, lang=lang)
        except Exception as e:
            print(f"Could not generate narration for clip {i + 1}: {e}")


        # 5. Burn subtitles and add narration
        final_clip_path = os.path.join(output_dir, f"{base_filename}_final_clip_{i + 1}.mp4")
        try:
            print("Adding subtitles and narration...")
            burn_subtitles_and_narration(raw_clip_path, srt_path, narration_audio_path, output_path=final_clip_path)
            final_clip_paths.append(final_clip_path)
        except Exception as e:
            print(f"Error burning subtitles/narration for clip {i + 1}: {e}")
            # If burning fails, add the raw clip path as a fallback
            final_clip_paths.append(raw_clip_path)


        # 6. Clean up temporary files
        os.remove(raw_clip_path)
        os.remove(srt_path)
        if narration_audio_path and os.path.exists(narration_audio_path):
            os.remove(narration_audio_path)

    return final_clip_paths


def save_segments_to_json(segments, json_path):
    """Save segments with timestamps to a JSON file."""
    with open(json_path, 'w') as f:
        json.dump(segments, f, indent=2)


if __name__ == "__main__":
    # Example usage:
    # This will download a video, and then clip it into 60-second parts,
    # each with its own subtitles and narration.
    video_url = "https://youtu.be/KUXjXW7PtC0?si=apd-eOD34bLub8Ly" # A sample video
    output_directory = "VideoClipper/output"
    
    print(f"Downloading video from {video_url}...")
    downloaded_video_path = download_video(video_url, output_path="VideoClipper")
    
    if downloaded_video_path:
        print(f"Video downloaded to: {downloaded_video_path}")
        print("Starting clipping process...")
        
        final_clips = cut_video_into_clips(
            video_path=downloaded_video_path,
            clip_duration=60,
            output_dir=output_directory,
            lang='en'
        )
        
        if final_clips:
            print("\nClipping complete. Final clips created:")
            for clip in final_clips:
                print(f"- {clip}")
        else:
            print("\nClipping process finished, but no clips were created.")
    else:
        print("Failed to download the video.")
