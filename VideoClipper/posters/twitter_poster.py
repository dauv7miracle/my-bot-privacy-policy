import tweepy
import os

class TwitterPoster:
    def __init__(self, api_key, api_key_secret, access_token, access_token_secret):
        auth = tweepy.OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def post_clip(self, clip_path, status_text=""):
        """
        Posts a video clip to Twitter with optional status text.
        :param clip_path: Path to the video clip file
        :param status_text: Text to accompany the video post
        """
        if not os.path.exists(clip_path):
            raise FileNotFoundError(f"Clip file not found: {clip_path}")

        media = self.api.media_upload(clip_path, media_category='tweet_video')
        self.api.update_status(status=status_text, media_ids=[media.media_id])
        print(f"Posted clip to Twitter: {clip_path}")

# Example usage:
# if __name__ == "__main__":
#     poster = TwitterPoster(api_key="YOUR_API_KEY", api_key_secret="YOUR_API_SECRET",
#                            access_token="YOUR_ACCESS_TOKEN", access_token_secret="YOUR_ACCESS_SECRET")
#     poster.post_clip("path_to_clip.mp4", "Check out this clip!")
