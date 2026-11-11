def __init__(self, bearer_token=None, consumer_key=None,
             consumer_secret=None, access_token=None,
             access_token_secret=None, *, wait_on_rate_limit=False):
    self.bearer_token = bearer_token
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token = access_token
    self.access_token_secret = access_token_secret

    self.wait_on_rate_limit = wait_on_rate_limit

    self.session = requests.Session()
    self.user_agent = (
        f"Python/{python_version()} "
        f"Requests/{requests.__version__} "
        f"Tweepy/{tweepy.__version__}"
    )
