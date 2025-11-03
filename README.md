Assignment Overview: 
This assignment collects Reddit posts using the Python Reddit API Wrapper (PRAW) library. It collects posts from a list of subreddits and then perfoms a keyword search across those subreddits. The result is a CSV file.   

How to Run:  
1. Prerequisites:  
   -Python 3.8+  
   -Reddit API application with client credentials  
   -Packages: pandas, praw, python-dotenv  
2. Installation:  
   %pip install praw python-dotenv pandas  
3. Configuration:  
   Create a text file named reddit_api.env that contains Reddit API credentials, it should contain the following:  
   REDDIT_CLIENT_ID=your_client_id  
   REDDIT_CLIENT_SECRET=your_client_secret  
   REDDIT_USERNAME=your_reddit_username  
   REDDIT_PASSWORD=your_reddit_password  
   REDDIT_USER_AGENT=your_app_name_or_desc  
4. Execution:  
  from google.colab import drive  
  drive.mount('/content/drive')  
  env_file_path = '/content/drive/MyDrive/reddit_api.env'  

Output Description:   
The output file contains posts about physical fitness, specifically subreddits on gym, fitness, workout.   
These are the following columns:   
title: Post title (string).  
score:	Reddit score / upvotes (integer).  
upvote_ratio:	Upvote ratio (float 0–1).  
num_comments:	Number of comments (integer).  
author:	Post author’s username (string or null if unavailable).  
subreddit:	Subreddit name (string).  
url:	External URL for the post (string).  
permalink:	Reddit permalink to the post (string). Used for deduplication.  
created_utc:	Post creation time as UTC epoch seconds (float/int).  
is_self:	Whether the post is a self/text post (boolean).  
selftext:	Body text for self posts (string, truncated to 500 chars).  
flair:	Link flair text (string or null).  
domain:	Domain of the linked content (string).  
search_query:	The keyword used in the search task that found the post, or null for hot posts.  
