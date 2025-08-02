import json
import datetime
import os
import time
from video_clipper import download_video, transcribe_audio, cut_video_into_clips, save_segments_to_json
from scheduler import ClipScheduler
from posters.twitter_poster import TwitterPoster
from posters.instagram_poster import InstagramPoster
from posters.tiktok_poster import TikTokPoster

def load_config(config_path="VideoClipper/config.json"):
    with open(config_path, 'r') as f:
        return json.load(f)

def post_to_platforms(clip_path, platforms, api_credentials, caption=""):
    for platform in platforms:
        if platform == "twitter":
            creds = api_credentials.get("twitter", {})
            poster = TwitterPoster(
                api_key=creds.get("api_key"),
                api_key_secret=creds.get("api_key_secret"),
                access_token=creds.get("access_token"),
                access_token_secret=creds.get("access_token_secret")
            )
            poster.post_clip(clip_path, caption)
        elif platform == "instagram":
            creds = api_credentials.get("instagram", {})
            poster = InstagramPoster(
                access_token=creds.get("access_token"),
                instagram_account_id=creds.get("instagram_account_id")
            )
            poster.post_clip(clip_path, caption)
        elif platform == "tiktok":
            creds = api_credentials.get("tiktok", {})
            poster = TikTokPoster(access_token=creds.get("access_token"))
            poster.post_clip(clip_path, caption)
        else:
            print(f"Unsupported platform: {platform}")

def main():
    config = load_config()
    clip_scheduler = ClipScheduler()

    for video_config in config.get("videos", []) :
        url = video_config.get("url")
        clip_duration = video_config.get("clip_duration", 60)
        lang = video_config.get("language", "en")
        output_dir = "VideoClipper/output"

        print(f"Processing video: {url}")
        downloaded_video_path = download_video(url, output_path="VideoClipper")
        if not downloaded_video_path:
            print(f"Failed to download video: {url}")
            continue

        # The new function handles transcription, clipping, narration, and subtitles all at once.
        final_clip_paths = cut_video_into_clips(
            video_path=downloaded_video_path,
            clip_duration=clip_duration,
            output_dir=output_dir,
            lang=lang
        )

        if not final_clip_paths:
            print("No clips were created. Moving to next video.")
            continue

        print(f"Successfully created {len(final_clip_paths)} clips.")

        # Scheduling the created clips for posting
        for schedule_info in video_config.get("post_schedule", []) :
            clip_index = schedule_info.get("clip_index")
            post_time_str = schedule_info.get("post_time")
            platforms = schedule_info.get("platforms", [])
            caption = schedule_info.get("caption", "Check out this clip!")

            if clip_index is None or clip_index < 1 or clip_index > len(final_clip_paths):
                print(f"Invalid clip_index: {clip_index}. Skipping schedule.")
                continue

            try:
                post_time = datetime.datetime.fromisoformat(post_time_str)
            except (ValueError, TypeError):
                print(f"Invalid post_time format: '{post_time_str}'. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
                continue

            # The final clip path already includes the `_final_` part
            clip_to_post = final_clip_paths[clip_index - 1]

            # Define a function to pass to the scheduler
            def schedule_post(path, plat, creds, cap):
                print(f"Executing scheduled post for {path} to {plat} at {datetime.datetime.now()}")
                post_to_platforms(path, plat, creds, caption=cap)

            clip_scheduler.schedule_clip_post(
                clip_path=clip_to_post,
                post_time=post_time,
                post_function=schedule_post,
                # Pass arguments for post_function
                args=(platforms, config.get("api_credentials", {}), caption)
            )
            print(f"Scheduled clip {clip_to_post} for posting at {post_time} to {platforms}")

    print("\nAll video processing and scheduling is complete.")
    print("The scheduler is running in the background. Press Ctrl+C to exit.")
    try:
        # Keep the script running to allow the scheduler to execute jobs
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        clip_scheduler.shutdown()
        print("\nScheduler has been shut down.")

if __name__ == "__main__":
    main()
