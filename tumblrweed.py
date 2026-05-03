# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 03:19:52 2026

@author: nyssa

tumblrweed uses tumblr api for basic blog management. 
"""

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
import os, requests

class TumblrWeed():
    def __init__(self, blog_id):
        """
        initialize TumblrWeed class        

        Parameters
        ----------
        blog_id
            blog name, hostname, or uuid identifying the blog to be manipulated.

        Returns
        -------
        None.

        """
        load_dotenv()
        
        # retrieve secrets
        self.client_id = os.getenv("TUMBLR_CLIENT_ID")
        self.client_secret = os.getenv("TUMBLR_CLIENT_SECRET")
        self.oauth_token = os.getenv("TUMBLR_OAUTH_TOKEN")
        self.oauth_token_secret = os.getenv("TUMBLR_OAUTH_TOKEN_SECRET")
        
        # set blog identifier
        self.blog_id = blog_id
        
        # create oauth1 session
        self.session = OAuth1Session(
            self.client_id,
            client_secret=self.client_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret
            )
        
        # base url
        self.base = f"https://api.tumblr.com/v2/blog/{self.blog_id}"
    
    def get_res(self, endpoint, method="GET", oauth=False, params=None, data=None):
        """
        get response from tumblr api
        supports:
            - public GET (api_key)
            - private GET (oauth1)
            - private POST (oauth1)
            
        Parameters
        ----------
        endpoint : str
            api method described in tumblr docs.
            e.g.: "/info", "/followers"
        method : str, optional
            "GET" or "POST" http method. The default is "GET".
        oauth : boolean, optional
            private authentication. The default is False.
        params : dict, optional
            parameters described in tumblr docs. The default is None.
    
        Returns
        -------
        dict
            json response in dictionary form.
    
        """
        url = self.base + endpoint
        
        # oauth1 request
        if oauth:
            if method.upper() == "POST":
                return self.session.post(url, json=data).json()
            elif method.upper() == "GET":
                return self.session.get(url, params=params).json()
        
        # public get request (api_key)
        params = params or {} # if params is None, set as empty dict
        params["api_key"] = self.client_id
        
        return requests.get(url, params=params).json()
    
    def print_err_code(self, res):
        print(str(res["meta"]["status"]) + " " + res["meta"]["msg"])
    
    def get_info(self):
        """
        retrieve basic blog information. 
        
        Returns
        -------
        blog_info : dict
            title, description, number of posts, last updated.
    
        """
        res = self.get_res("/info")
        
        if (res["meta"]["status"] != 200):
            self.print_err_code(res)
        else:
            blog_info={
                "title":res["response"]["blog"]["title"],
                "description":res["response"]["blog"]["description"],
                "posts":res["response"]["blog"]["posts"],
                "updated":res["response"]["blog"]["updated"]            
                }
            return blog_info
    
    def get_follower_count(self):
        """
        retrieve number of followers for a blog.
    
        Returns
        -------
        int
            number of users following a blog.
    
        """
        res = self.get_res("/followers", oauth=True)
        
        if (res["meta"]["status"] != 200):
            self.print_err_code(res)
        else:
            return res["response"]["total_users"]
    
    def get_posts(self):
        """
        retrieve post ids for every post on a blog.
    
        Returns
        -------
        post_ids : list
            a list containing post ids.
    
        """
        res = self.get_res("/posts")
        
        if (res["meta"]["status"] != 200):
            self.print_err_code(res)
        else:
            post_ids=[]
            offset = 0
            # by default, /posts retrieves 20 posts at a time.
            # offset parameter allows for iteration through pages.
            while (len(res["response"]["posts"]) > 0):
                for post in res["response"]["posts"]:
                    post_ids.append(post["id"])
                offset += 20
                res = self.get_res("/posts", params={"offset": offset})
            return post_ids
    
    def get_content(self, filename, title=False):
        """
        convert a simple (no formatting) plain text file into a content packet
        for /posts. 

        Parameters
        ----------
        filename : str
            the full path to the text file.
        title : bool, optional
            if the first line in the text file is the title, set as True. 
            The default is False.

        Returns
        -------
        content : list
            the content packet formatted in npf as per tumblr api docs.

        """        
        content = [] # each content block in npf is a dictionary inside the list
        
        with open(filename, "r") as file:
            # load and fill content blocks
            for line in file:
                block = {"type":"text"}
                if title:
                    block["subtype"] = "heading1"
                    title = False
                block["text"] = line.strip()
                content.append(block)
        return content
    
    def create_post(self, content, state="published", publish_on=None, tags=None):
        """
        create a new post.

        Parameters
        ----------
        content : list
            content packet formatted in inpf as per tumblr api docs.
        state : str, optional
            initial state of new post. The default is "published".
        publish_on : str, optional
            exact future date and time (iso 8601 format) to publish post. only 
            used by api if state parameter is "queue". The default is None.
        tags : str, optional
            string of comma-separated tags. The default is None.

        Returns
        -------
        str
            created post id as a string.

        """
        data = {
            "content":content,
            "state":state
            }
        if publish_on:
            data["publish_on"] = publish_on
        if tags:
            data["tags"] = tags
            
        res = self.get_res("/posts", method="POST", oauth=True, data=data)
        
        if (res["meta"]["status"] != 201):
            self.print_err_code(res)
            return res["errors"]
        else:
            return res["response"]["id"]
    
    def delete_post(self, post_id):
        """
        delete a post.

        Parameters
        ----------
        post_id : int
            id of the post to delete.

        Returns
        -------
        bool
            true.

        """
        data = {"id":post_id}
        
        res = self.get_res("/post/delete", method="POST", oauth=True, data=data)
        
        if (res["meta"]["status"] != 200):
            self.print_err_code(res)
        else:
            return True