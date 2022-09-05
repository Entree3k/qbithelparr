# QBitHelper - made by [Opaquer](https://github.com/Opaque02)

Hey guys, and welcome to Qbittorrent/discord notifier bot!

So, first thing's first: I'm not a programmer at all. There may be bugs, and I haven't actually tried this on anything other than my Windows PC. I'm more than happy for people to work on it and make better versions as needed. Also, I've never done this before, so I don't know if there's a better way to do this. I'm going to walk through the steps of making the bot, installing all the necessary things, and finally the code to run. I know it's a lot, and I'm sorry, but if there's a better way to do it, I'd love to hear it!

Step 1: you'll want to make a discord bot and a server on discord. There's plenty of guides out there - since I was also trying to make one, I used [this](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) one. Just go until you add the bot to your server. For permissions, I added a bunch of ones you probably won't need for testing purposes, but I think [this](https://i.imgur.com/xUfYkWo.png) is the minimum you'll need (if not, feel free to update me). Basically, it needs to be able to send/read messages and delete messages. At some point you'll get a long token for your bot - keep it for step 3. You'll need to enable some intents for the bot to work. Head over to settings -> Bot on the Discord Developer Portal for your application and enable all the intents so it looks like [this](https://i.imgur.com/0JlTvES.png).

Step 3: Once your bot is created open the config.ini file and edit the following section with your details:

    [QBITTORRENT]
    host = localhost
    port = 8080
    username = username
    password = password
    
    [DISCORD]
    botChannel = BOT CHANNEL
    
    [SONARR]
    tvCategory = "tv-sonarr"
    
    [RADARR]
    movieCategory = "radarr"

With a bit of luck, if you save it and run it, it'll say that it's connected to the discord bot, and that it's ready to go! When that's done, go to your download tracker discord channel and type $status. This may take a sec, but it'll delete everything in the channel that's not pinned, then update the channel with what's currently downloading. 

NOTE: I set up the bot command to be /, but you can change it to whatever you want :)

Also, the reason I have it delete everything that's not pinned is so that I can have instructions on my channel with how to use the bot, and because it's pinned and everything gets deleted, this will always stay at the top. 

By default, typing /status will show everything currently downloading, but you can go a bit fancy too. There's technically 2 commands it takes - /status {media category} {download type}. The media category is either movies or tv, depending if you want to just see what movies/TV shows are downloading. The download type is either downloading (default), completed (to just see the completed stuff), or all, to see everything. For example:

    /status movies # will show all currently downloading movies, whereas /status tv will show all currently downloading TV shows
    
    /status movies completed # will show all movies that have completed downloading
    
    /status # all will show everything - all movies/tv shows currently downloading AND currently completed!

By default, the output will have everything that's not completed in descending order, so the things closest to completion will be at the top, and as you scroll down, it'll get closer to 0%. After all that, if there's anything that's 100% done, it'll show up at the end of the list

And with that, you should be good to go! Sorry again this was long winded! I hope you enjoy it, and that it works nicely for you! As I said, I'm not a programmer in any fashion, so there may be bugs that I may not be able to fix, but I'm also super happy for whoever to work on it as you see fit! If you make any cool updates, let me know!
