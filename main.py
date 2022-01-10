import logging
import platform
import re
from statistics import mean, mode, median, stdev

import praw
from yaml import safe_load
from tqdm import tqdm


def is_mod(author, subreddits: list) -> bool:
    """
    Checks if the author is moderator or not
    :param subreddits: The subreddits whose moderator list will be compared to.
    :param author: The reddit instance which will be checked in the list of mods
    :return: True if author is moderator otherwise False
    """
    for subreddit_name in subreddits:
        subreddit = author._reddit.subreddit(subreddit_name)
        moderators_list = subreddit.moderator()
        if author in moderators_list:
            return True
        else:
            return False


def calculate_statistics(submission, bot_config, skip_op):
    all_ratings = []
    rating_regex = re.compile(r"\d+(\.\d+)?(-\d+(\.\d+)?)?", re.IGNORECASE)
    submission.comments.replace_more(limit=None)
    for top_level_comment in tqdm(submission.comments, desc="Reading top level comments"):
        # Skip over the comments by OP
        if skip_op and top_level_comment.author == submission.author:
            continue

        if rating_str := rating_regex.match(top_level_comment.body.replace(" ", "")):
            # If rating is range like (5.0-5.5), mean is considered instead.
            if '-' in rating_str.group():
                range_split = [float(x) for x in rating_str.group().split('-')]
                rating = mean(range_split)
            else:
                rating = float(rating_str.group())

            # Throwing away ratings more than 10 since the scale is not correct.
            if rating <= 10.0:
                comment_preview = top_level_comment.body[:10].replace("\n", "")
                logger.debug(f"Comment: \"{comment_preview}...\" -> Extraction: {rating_str.group()} Conversion: -> {rating:.2f}")
                all_ratings.append(rating)

    if len(all_ratings):
        submission_stats = {':num_ratings:': len(all_ratings),
                            ':mean:': mean(all_ratings),
                            ':mode:': mode(all_ratings),
                            ':median:': median(all_ratings),
                            ':stdev:': stdev(all_ratings),
                            ':max:': max(all_ratings),
                            ':min:': min(all_ratings)}

        response = bot_config['comment']
        for key, value in submission_stats.items():
            response = response.replace(f"{key}", f"{value:.2f}")
    else:
        response = "The bot could not find any ratings in the comment section. Please try again later."

    response = f"{response}\n\n^(This action was performed by a bot, please contact the mods for any questions. For info on bot, check out my Reddit profile.)"
    return response


def mention_listener(reddit, bot_config):
    while True:
        try:
            for mention in praw.models.util.stream_generator(reddit.inbox.mentions, skip_existing=True):
                logger.info(f"Bot mentioned by u/{mention.author} in comment {mention.id} and subreddit r/{mention.subreddit}.")

                if is_mod(mention.author, bot_config['subreddits']) and str(mention.subreddit).lower() in [sub.lower() for sub in bot_config['subreddits']]:
                    skip_op = True if "--ignore-op" in mention.body.lower() else False
                    response = calculate_statistics(mention.submission, bot_config, skip_op)
                    mention.reply(response)
        except praw.exceptions.APIException:
            logger.error("Reddit Error. If the HTTP Error is 5XX then the issue is with reddit servers. 4XX Error are client errors.", exc_info=True)
        except Exception:
            logger.critical("Something went wrong, please contact bot dev (u/is_fake_Account).", exc_info=True)


def main():
    with open('config.yaml') as config_file:
        bot_config = safe_load(config_file)

    # Logging into Reddit
    reddit = praw.Reddit(client_id=bot_config['reddit_credentials']['client_id'],
                         client_secret=bot_config['reddit_credentials']['client_secret'],
                         username=bot_config['reddit_credentials']['username'],
                         password=bot_config['reddit_credentials']['password'],
                         user_agent=f"{platform.platform()}:TrueRateMeStatsCalculator by (u/is_fake_Account)")
    logger.info(f"Logged in as Reddit User {reddit.user.me()}.")
    mention_listener(reddit, bot_config)


if __name__ == '__main__':
    # Setting up root logger
    logger = logging.getLogger("TrueRateMeStatBot")
    logger.setLevel(logging.DEBUG)

    # Setting up the streaming
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.INFO)   # To make the script verbose set level to logging.DEBUG
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)
    main()
