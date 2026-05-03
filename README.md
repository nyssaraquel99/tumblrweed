# tumblrweed
**tumblrweed** is a simple script powered by Tumblr API for basic blog management. Use **app** to open a local server and retrieve OAuth1 tokens from Tumblr (necessary for private methods).   
**nuke** uses tumblrweed to algorithmically delete all posts off a blog.   
I wrote **tumblrweed** and **nuke** because I wanted to refresh my blog, but Tumblr doesn't natively have a way to easily delete all posts. Even the Mass Post Editor requires you to select each post to delete one by one. I had nearly 3000 posts on my 14 year old blog, so that simply wasn't going to happen. But I didn't want to give up my url or make a new blog. So over the course of a week, I riffled through Tumblr's API docs and put this script together to automate the process. Would it have been faster to suffer through Mass Post Editor and delete my posts manually? Probably. Could I have use the pytumblr client library instead of writing my own code? Sure. But now I have these scripts at hand in case of my next ego death. And, thanks to this repo, so do you!   
- - - - - - - - - - - -   
Notes:   
1. In order to use **tumblrweed** you need to record your secrets in a .env file with the following format:
>TUMBLR_CLIENT_ID=xxxxxxxxxx   
>TUMBLR_CLIENT_SECRET=xxxxxxxxxx   
>TUMBLR_REDIRECT_URI=http://localhost:3000/callback   
>TUMBLR_OAUTH_TOKEN=xxxxxxxxxx   
>TUMBLR_OAUTH_TOKEN_SECRET=xxxxxxxxxx
The client tokens are retrieved after successfully registering your application. The OAuth1 tokens are retrieved from running **app** and opening the server in your browser of choice.   
2. **tumblrweed** is optimized for creating simple text posts for testing purposes, and for deleting posts. You can use get_info to verify your API keys are working, and get_follower_count to verify your OAuth1 keys are working. If you want to do anything more than creating test posts and deleting posts, I would recommend looking at Tumblr's client libraries, as listed on their API docs.
3. **nuke** is not a perfect script, meaning if you have more than 1000 posts, you will have to run the script multiple times. This is due to the rate limit of 1000 calls per hour per consumer key. I decided to optimize for not hitting the minute rate limit, as opposed to the hour rate limit, because I didn't want a script running for hours in the background. As written, **nuke** maxes out at deleting 250 posts per minute, and will run for about five minutes start to end per session. After running, **nuke** will let you know how many posts are left on your account. Wait about an hour from the first call to restart the script. If you have more than 5000 posts, you will have to wait one calendar day due to the rate limit of 5000 calls a day per consumer key.
