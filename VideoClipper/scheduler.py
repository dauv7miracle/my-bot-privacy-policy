from apscheduler.schedulers.background import BackgroundScheduler
import time

class ClipScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_clip_post(self, clip_path, post_time, post_function, *args, **kwargs):
        """
        Schedule a clip to be posted at a specific time.
        :param clip_path: Path to the clip file
        :param post_time: datetime object when to post
        :param post_function: function to call to post the clip
        :param args: positional arguments for post_function
        :param kwargs: keyword arguments for post_function
        """
        self.scheduler.add_job(post_function, 'date', run_date=post_time, args=(clip_path,)+args, kwargs=kwargs)

    def shutdown(self):
        self.scheduler.shutdown()

if __name__ == "__main__":
    import datetime

    def dummy_post(clip_path):
        print(f"Posting clip: {clip_path} at {datetime.datetime.now()}")

    clip_scheduler = ClipScheduler()
    post_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
    clip_scheduler.schedule_clip_post("example_clip.mp4", post_time, dummy_post)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        clip_scheduler.shutdown()
