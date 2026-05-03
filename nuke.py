# -*- coding: utf-8 -*-
"""
Created on Fri May  1 04:14:20 2026

@author: nyssa

nuke uses tumblr api to mass delete posts on blog.
"""

import tumblrweed
import time

#%% load blog name
blog_id = ""

#%% create TumblrWeed instance
blog = tumblrweed.TumblrWeed(blog_id)

#%% retrieve post ids and confirm all ids have been collected
blog_info = blog.get_info()
if blog_info:
    post_count = blog_info["posts"]
    post_ids = blog.get_posts()
    if post_count == len(post_ids):
        print(f"all {post_count} post ids retrieved")
    else:
        print("missing %i posts", (post_count-len(post_ids)))
else:
    print("failed to retrieve blog info")

#%% delete all posts
counter = post_count
for post_id in post_ids:
    if blog.delete_post(post_id):
        print(f"post {post_id} deleted")
        counter -= 1
        time.sleep(0.24) # slow the script down to avoid maxing out call per minute limit
    else: 
        print(f"ERROR: post {post_id} NOT deleted")
        break

if counter == 0:
    print("all posts deleted")
else:
    print(f"{counter} posts left")