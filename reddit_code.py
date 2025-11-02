%pip install praw python-dotenv

import praw
import csv
import os
import pandas as pd
from dotenv import load_dotenv

from google.colab import drive
drive.mount('/content/drive')

# Load environment variables from .env file
#load_dotenv('reddit_api.env') # This line was commented out
from dotenv import dotenv_values
import os

# Define the path to your .env file in Google Drive
# IMPORTANT: Update this path to the actual location of your reddit_api.env file in your Google Drive
env_file_path = '/content/drive/MyDrive/reddit_api.env'


# Load environment variables from reddit_api.env file if it exists
if os.path.exists(env_file_path):
    config = dotenv_values(env_file_path)
    print(f"✅ Environment variables loaded from {env_file_path}!")
else:
    config = {}
    print(f"❌ Error: '{env_file_path}' not found. Environment variables not loaded.")
    print("Please ensure the 'reddit_api.env' file is in the specified Google Drive path.")

    # Authenticate with Reddit using environment variables
reddit = praw.Reddit(
    client_id=config.get('REDDIT_CLIENT_ID'),
    client_secret=config.get('REDDIT_CLIENT_SECRET'),
    username=config.get('REDDIT_USERNAME'),
    password=config.get('REDDIT_PASSWORD'),
    user_agent=config.get('REDDIT_USER_AGENT')
)

print("✅ Reddit API authenticated successfully!")
print(f"Connected as: {reddit.user.me()}")

def _extract_post_row(post, fallback_subreddit, search_query=None, selftext_maxlen=500):
    title = getattr(post, "title", None)
    score = getattr(post, "score", None)
    upvote_ratio = getattr(post, "upvote_ratio", None)
    num_comments = getattr(post, "num_comments", None)
    author_obj = getattr(post, "author", None)
    author = getattr(author_obj, "name", None) if author_obj else None
    subreddit_name = getattr(getattr(post, "subreddit", None), "display_name", None) or fallback_subreddit
    url = getattr(post, "url", None)
    permalink = getattr(post, "permalink", None)
    created_utc = getattr(post, "created_utc", None)
    is_self = getattr(post, "is_self", None)
    raw_selftext = getattr(post, "selftext", None) or None

    if isinstance(raw_selftext, str) and len(raw_selftext) > selftext_maxlen:
        selftext = raw_selftext[:selftext_maxlen] + "..."
    else:
        selftext = raw_selftext

    flair = getattr(post, "link_flair_text", None)
    domain = getattr(post, "domain", None)

    return {
        "title": title,                 # String
        "score": score,                 # Integer
        "upvote_ratio": upvote_ratio,   # Float
        "num_comments": num_comments,   # Integer
        "author": author,               # String
        "subreddit": subreddit_name,    # String
        "url": url,                     # String
        "permalink": permalink,         # String
        "created_utc": created_utc,     # Integer/Float
        "is_self": is_self,             # Boolean
        "selftext": selftext,           # String (truncated to 500)
        "flair": flair,                 # String
        "domain": domain,               # String
        "search_query": search_query    # String or None
    }

NEEDED_COLUMNS = [
    "title", "score", "upvote_ratio", "num_comments",
    "author", "subreddit", "url", "permalink",
    "created_utc", "is_self", "selftext", "flair",
    "domain", "search_query"
]

def save_reddit_data(rows, output_filename="reddit_data.csv"):
    """
    Task 3: Convert list of row dicts -> DataFrame, dedupe by permalink, save without index.
    """
    df = pd.DataFrame(rows or [], columns=NEEDED_COLUMNS)
    # Ensure all required columns exist 
    for col in NEEDED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[NEEDED_COLUMNS]

    before = len(df)
    if "permalink" in df.columns:
        df = df.drop_duplicates(subset=["permalink"]).reset_index(drop=True)
    after = len(df)

    df.to_csv(output_filename, index=False)
    print(f"Saved '{output_filename}' with {after} unique rows (removed {before - after} duplicates).")


# Task 1: Fetching hot posts


def download_hot_posts_for_subreddits(subreddit_names, limit_per_subreddit=50):
    """
    Collect 'hot' posts from multiple subreddits (Task 1).
    Returns a list of row dicts (Section 3.2)
    """
    if not subreddit_names or not isinstance(subreddit_names, (list, tuple)) or not all(isinstance(s, str) and s for s in subreddit_names):
        raise ValueError("subreddit_names must be a non-empty list of strings")
    if not isinstance(limit_per_subreddit, int) or limit_per_subreddit <= 0:
        raise ValueError("limit_per_subreddit must be a positive integer")

    all_rows = []
    for sub in subreddit_names:
        subreddit = reddit.subreddit(sub)
        posts = subreddit.hot(limit=limit_per_subreddit)

        sub_count = 0
        for post in posts:
            all_rows.append(_extract_post_row(post, fallback_subreddit=sub, search_query=None))
            sub_count += 1

        print(f"Collected {sub_count} posts from r/{sub}.")  # Logging requirement

    return all_rows


# Task 2: Keyword-based search


def search_posts(query, subreddit_names, limit_per_subreddit=50):
    """
    Search for posts containing `query` across subreddits (Task 2).
    Returns rows with Section 3.2 schema and `search_query` populated.
    """
    if not query or not isinstance(query, str):
        raise ValueError("query must be a non-empty string")
    if not subreddit_names or not isinstance(subreddit_names, (list, tuple)) or not all(isinstance(s, str) and s for s in subreddit_names):
        raise ValueError("subreddit_names must be a non-empty list of strings")
    if not isinstance(limit_per_subreddit, int) or limit_per_subreddit <= 0:
        raise ValueError("limit_per_subreddit must be a positive integer")

    all_rows = []
    for sub in subreddit_names:
        subreddit = reddit.subreddit(sub)
        results = subreddit.search(query=query, sort='relevance', time_filter='all', limit=limit_per_subreddit)

        sub_count = 0
        for post in results:
            all_rows.append(_extract_post_row(post, fallback_subreddit=sub, search_query=query))
            sub_count += 1

        print(f"Collected {sub_count} searched posts from r/{sub} for query '{query}'.")  # Logging

    return all_rows



if __name__ == "__main__":
    target_subreddits = ["gym", "fitness", "workout"]
    limit_per_subreddit = 50
    keyword = "strength"

    # Task 1
    hot_rows = download_hot_posts_for_subreddits(target_subreddits, limit_per_subreddit=limit_per_subreddit)

    # Task 2
    search_rows = search_posts(keyword, target_subreddits, limit_per_subreddit=limit_per_subreddit)

    # Task 3: csv file
    combined_rows = (hot_rows or []) + (search_rows or [])
    save_reddit_data(combined_rows, output_filename="reddit_data.csv")