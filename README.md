# QBitHelparr

Hey guys, and welcome to Qbittorrent/discord notifier bot!

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

NOTE: I set up the bot command to be /, but you can change it to whatever you want :) 

By default, typing /status will show everything currently downloading, but you can go a bit fancy too. There's technically 2 commands it takes - /status {media category} {download type}. The media category is either movies or tv, depending if you want to just see what movies/TV shows are downloading. The download type is either downloading (default), completed (to just see the completed stuff), or all, to see everything. For example:

    /status movies # will show all currently downloading movies, whereas /status tv will show all currently downloading TV shows
    
    /status movies completed # will show all movies that have completed downloading
    
    /status # all will show everything - all movies/tv shows currently downloading AND currently completed!

By default, the output will have everything that's not completed in descending order, so the things closest to completion will be at the top, and as you scroll down, it'll get closer to 0%. After all that, if there's anything that's 100% done, it'll show up at the end of the list

And with that, you should be good to go! I hope you enjoy it, and that it works nicely for you! As I said, I'm not a programmer in any fashion, so there may be bugs that I may not be able to fix, but I'm also super happy for whoever to work on it as you see fit! If you make any cool updates, let me know!
made by [Opaquer](https://github.com/Opaque02)
