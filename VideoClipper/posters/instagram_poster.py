import requests
import os

class InstagramPoster:
    def __init__(self, access_token, instagram_account_id):
        """
        :param access_token: Instagram Graph API access token
        :param instagram_account_id: Instagram Business Account ID
        """
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.graph_api_url = "https://graph.facebook.com/v15.0"

    def post_clip(self, clip_path, caption=""):
        """
        Posts a video clip to Instagram Feed.
        :param clip_path: Path to the video clip file
        :param caption: Caption text for the post
        """
        if not os.path.exists(clip_path):
            raise FileNotFoundError(f"Clip file not found: {clip_path}")

        # Step 1: Upload video container
        upload_url = f"{self.graph_api_url}/{self.instagram_account_id}/media"
        files = {
            'video_file': open(clip_path, 'rb')
        }
        params = {
            'access_token': self.access_token,
            'media_type': 'VIDEO',
            'caption': caption
        }
        response = requests.post(upload_url, params=params, files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload video container: {response.text}")
        creation_id = response.json().get('id')

        # Step 2: Publish media
        publish_url = f"{self.graph_api_url}/{self.instagram_account_id}/media_publish"
        publish_params = {
            'access_token': self.access_token,
            'creation_id': creation_id
        }
        publish_response = requests.post(publish_url, params=publish_params)
        if publish_response.status_code != 200:
            raise Exception(f"Failed to publish media: {publish_response.text}")

        print(f"Posted clip to Instagram: {clip_path}")

# Example usage:
# if __name__ == "__main__":
#     poster = InstagramPoster(access_token="YOUR_ACCESS_TOKEN", instagram_account_id="YOUR_INSTAGRAM_ACCOUNT_ID")
#     poster.post_clip("path_to_clip.mp4", "Check out this clip!")
