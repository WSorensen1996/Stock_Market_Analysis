from numpy import True_, append
from pandas.core.frame import DataFrame
from pandas import DataFrame
import praw
from data import *
import time
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import nltk
nltk.downloader.download('vader_lexicon') 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date, datetime
import sys 
from tqdm import tqdm


def run_sentiment(unix,lengthOfInterval):
    mySQLunix = unix
    print("Extracting data from reddit")
    start_time = time.time()
    reddit = praw.Reddit(user_agent = "Comment Extraction by /u/ ... ", #insert username
        client_id=" ... ", 
        client_secret=" ... ",
        username=" ... ",
        password=" ... ")

    '''############################################################################'''
    # set the program parameters --- 
    subs = ['stocks','investing','stockmarket','wallstreetbets', 'pennystocks', 'robinhood','povertyfinance','cryptocurrency']  # sub-reddit to search
    post_flairs = {'Daily Discussion','Weekend Discussion', 'Discussion'}    #   -- posts flairs to search || None flair is automatically considered
    goodAuth = {'AutoModerator'}   # authors whom comments are allowed more than once
    uniqueCmt = True                # allow one comment per author per symbol
    ignoreAuthP = {'example'}       # authors to ignore for posts 
    ignoreAuthC = {'example'}       # authors to ignore for comment 
    upvoteRatio = 0.65        # upvote ratio for post to be considered, 0.70 = 70%
    ups = 7       # define # of upvotes, post is considered if upvotes exceed this #
    limit = 1000      # define the limit, comments 'replace more' limit
    upvotes = 4     # define # of upvotes, comment is considered if upvotes exceed this #
    picks = 40     # define # of picks here, prints as "Top ## picks are:"
    picks_ayz = 40   # define # of picks for sentiment analysis

    '''############################################################################'''

    #Defining containers:
    posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
    cmt_auth = {}

    #Converting to unix: 
    unix = mySQLunix 

    for sub in tqdm(subs):
        subreddit = reddit.subreddit(sub)
        hot_python = subreddit.hot()    # sorting posts by hot

        # Extracting comments, symbols from subreddit
        for submission in hot_python:
            if submission.created_utc > unix and submission.created_utc < (unix + lengthOfInterval) : 

                flair = submission.link_flair_text 

                if submission.author is not None:
                    author = submission.author.name  
                
                # checking: post upvote ratio # of upvotes, post flair, and author 
                if submission.upvote_ratio >= upvoteRatio and submission.ups > ups and (flair in post_flairs or flair is None) and author not in ignoreAuthP:   
                    submission.comment_sort = 'new'   


                    comments = submission.comments
                    titles.append(submission.title)
                    posts += 1
                    submission.comments.replace_more(limit=limit)   
                    for comment in comments:

                        # try except for deleted account?
                        try: auth = comment.author.name
                        except: pass
                        c_analyzed += 1
                        
                        # checking: comment upvotes and author
                        if comment.score > upvotes and auth not in ignoreAuthC:      
                            split = comment.body.split(" ")
                            for word in split:
                                word = word.replace("$", "")        
                                # upper = ticker, length of ticker <= 5, excluded words,                     
                                if word.isupper() and len(word) <= 5 and word not in blacklist and word in us:
                                    
                                    # unique comments, try/except for key errors
                                    if uniqueCmt and auth not in goodAuth:
                                        try: 
                                            if auth in cmt_auth[word]: break
                                        except: pass
                                        
                                    # counting tickers
                                    if word in tickers:
                                        tickers[word] += 1
                                        a_comments[word].append(comment.body)
                                        cmt_auth[word].append(auth)
                                        count += 1
                                    else:                               
                                        tickers[word] = 1
                                        cmt_auth[word] = [auth]
                                        a_comments[word] = [comment.body]
                                        count += 1    

    # sorts the dictionary
    symbols = dict(sorted(tickers.items(), key=lambda item: item[1], reverse = True))
    top_picks = list(symbols.keys())[0:picks]

    # print top picks
    new_time = (time.time()-start_time)
    print("It took %s seconds to analyze %s comments in %s posts in %s subreddits.\n" %(new_time, c_analyzed, posts, len(subs)))
    times = []
    top = []
    for i in top_picks:
        print(f"{i}: {symbols[i]}")
        times.append(symbols[i])
        top.append(f"{i}: {symbols[i]}")

    # Applying Sentiment Analysis
    scores, s = {}, {}

    vader = SentimentIntensityAnalyzer()
    # adding custom words from data.py 
    vader.lexicon.update(new_words)

    picks_sentiment = list(symbols.keys())[0:picks_ayz]
    for symbol in picks_sentiment:
        stock_comments = a_comments[symbol]
        for cmnt in stock_comments:
            score = vader.polarity_scores(cmnt)
            if symbol in s:
                s[symbol][cmnt] = score
            else:
                s[symbol] = {cmnt:score}      
            if symbol in scores:
                for key, _ in score.items():
                    scores[symbol][key] += score[key]
            else:
                scores[symbol] = score

        # calculating avg.
        for key in score:
            scores[symbol][key] = scores[symbol][key] / symbols[symbol]
            scores[symbol][key]  = "{pol:.3f}".format(pol=scores[symbol][key])

    df = pd.DataFrame(scores)
    df.index = ['Bearish', 'Neutral', 'Bullish' ,'Total/Compound']
    df = df.T
    print(df)

    #Exporting to .csv
    df['MT']=times
    List1=(str(df))
    now = datetime.now()
    with open ("Output_Sentiment.csv","w") as out_file:
        outstring = ""
        outstring += str(List1)
        out_file.write(outstring)

