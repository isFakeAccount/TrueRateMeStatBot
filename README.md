# r/TrueRateMe Statistics Bot

I'm a statistics bot designed to calculate the statistics of ratings given by users on r/TrueRateMe subreddit. This is what I do:

- Take the top level comments in posts where I'm summoned
- See if the comment starts with a number and extract it
- Then I calculate the following statistics on all the ratings
  - Mean
  - Median
  - Mode
  - Max
  - Min
  - Standard Deviation

**How to make sure your score is taken into account?**

- Reply to the post, not to another comment 
- Start your reply with the score 
- Stick to one of these formats:
  - 5 
  - 5.5 
  - 5.75 
  - 5-5.5 (I will take mean of the range)

**How to summon me?**

Just quote me in a comment: u/averagerBot

**What limitation do I have?**

- I can only be summoned in the subreddits mentions in the config file and by the moderators of subreddit.
- If I am summoned back to back, I will get slow due to rate limiting. 

# Configuration 

Before running me, you need to install Python 3.8 and above and install the requirements using pip command.

[Tutorial on how to install Python](https://www.reddit.com/r/RequestABot/comments/cyll80/a_comprehensive_guide_to_running_your_reddit_bot/)
```commandline
pip install -r requirements.txt
```

To configure me, edit the yaml file template provided. 

```yaml
reddit_credentials:
  username: "fakebot1"
  password: "invalidht4wd50gk"
  client_id: "revokedpDQy3xZ"
  client_secret: "revokedoqsMk5nHCJTHLrwgvHpr"

subreddits: ["subreddit1", "subreddit"]
comment: |
  I was able to extract :num_ratings: rating(s) from the comments. Here are the statistics for this submission at the moment.
  
  - Average: :mean:
  - Mode: :mode:
  - Median: :median:
  - Highest Rating: :max:
  - Lowest Rating: :min:
  - Standard Deviation: :stdev:
  
  Note: In case of high standard devition, average might not be a good assement of rating. In that case, median and mode will be more reliable.
```

You can modify the comment if you want. Value surrounded by colon gets replace by actual value. For example, :mean: will be replaced by the actual mean value. 

To obtain the client secret and client id, follow this [tutorial](https://redditclient.readthedocs.io/en/latest/oauth/). 