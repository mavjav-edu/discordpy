def main():
    import re, threading, time, asyncio, json, keyring, sys
    from cryptography.fernet import Fernet # required for decrypting our `token` and `key`
    from discord.ext import commands
    
    # Below, we choose the exclam (!) to signify commands to the bot; we could have chosen any character (or none at all, but then the bot might chat when people say things to humans) 
    bot = commands.Bot(command_prefix='!') # `bot` is the discord.py `commands.Bot` object we will use to call the Discord API

    modlogs = 628771287501766657 # The channel ID on my server for the mod-logs channel
    # It is an admin-only channel on my server where I want the bot to dump its errors
    # You can create one for your server too but, you'll have a different channel ID (of course).
    # Find out more here: 
    # https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

    @bot.command()
    async def remind(ctx, *, args):
        durationalias = { # natural lang time to corresponding seconds
            "second":1,
            "sec":1,
            "s":1,
            "minute":60,
            "min": 60,
            "m": 60,
            "hour": (60*60),
            "hr": (60*60),
            "h": (60*60),
            "day": (60*60*24),
            "d": (60*60*24),
            "week": (60*60*24*7),
            "wk": (60*60*24*7)
        }
        durationdict = { # seconds to corresponding en-US time
            1:"second",
            60:"minute",
            (60*60):"hour",
            (60*60*24):"day",
            (60*60*24*7):"week"
        }
        pattern = re.compile("""
            \s*     # matches zero or more whitespace characters; In case the user put spaces (or none) after the `timer` keyword
            (\d+)   # capturing group 1: matches one or more digit characters (this will be the number of seconds per duration specifier); We will interpret this as the number of seconds the user wants our bot to wait before reminding the channel
            (?:(""" + ('|'.join(durationalias.keys())) + """)s?) # capturing group 2: duration specifier
            \s*     # matches zero or more whitespace characters; In case the user put spaces (or none) after the number of duration specifier
            (.*)    # capturing group 3: matches zero or more of any character (the message to repeat as reminder); We will interpret any characters after the duration specifier as the message that the user wants echoed into the channel
            """,re.VERBOSE)
        matches = re.match(pattern,args) # `matches[0]` is the entire string matching the pattern; `matches[1]` is the first capture group; `matches[2]` is the second capture group
        await ctx.send("Sure. I'll remind you in "+matches[1]+" "+str(durationdict[durationalias[matches[2]]])+('','s')[int(matches[1])>1]) # bot uses the correct plural (when time is more or less than one unit) or singular (when time is exactly one unit) for time based on number of units-time specified
        asyncio.ensure_future(setreminder(int((matches[1])*durationalias[matches[2]]),ctx.channel,matches[3])) # multithreaded function calls

    async def setreminder(t,channel,message): # A simple reminder function that reminds a `channel` of a `message` after `t` seconds; this is a helper method to start a separate thread for enabling the bot's execution of parallel commands (without freezing between commands)
        await asyncio.sleep(t) # the helper thread goes to sleep for `t` seconds
        await channel.send("Remember, "+"'"+message+"'") # when the thread awakes, it will send a `message` to the `channel` worded as a reminder

    @bot.event # This is a function decorator to let Python know to call our `on_error` function when client events happen
    async def on_error(event, *args, **kwargs): # Here, we intercept errors by the code and dump them into the `modlogs` channel by overriding a built-in discord.py method called `on_error`
        await bot.get_channel(modlogs).send("🤢") # The bot prefaces error notifications with this sick emoji 
        await asyncio.sleep(1) # wait a second
        await bot.get_channel(modlogs).send(event) # Specify the event that caused the error
        await asyncio.sleep(0.5) # wait half a second
        await bot.get_channel(modlogs).send(sys.exc_info()) # Dump the error information into the `modlogs` channel
        await bot.get_channel(modlogs).send("🤮") # The bot concludes error notifications with barf emoji 


    @bot.event # This is a function decorator to let Python know to call our `on_ready` function when client events happen
    async def on_ready(): # Here, we announce the presence of our bot locally and remotely by overriding a built-in discord.py method called `on_ready`
        print('We have logged in as {0.user}'.format(bot)) # This will print to the local terminal that the bot is connected
        await bot.get_channel(modlogs).send(bot.user.name +' reporting for duty!') # This will send a message to the `modlogs` channel announcing the presence of our bot


    @bot.command()
    async def hello(ctx):
        await ctx.send('Hello!') # Tell user hello
    
    @bot.command()
    async def goaway(ctx):
        await ctx.send("I'm going...")
        await bot.logout() # Bot logs out

    #TODO: 
            
    #The four steps below require that we copied the bot auth token and ran the `writeToken.py` script prior to running this bot code (below will produce an unhandled `IOError` if `writeToken.py` step is skipped)
    key=open("key",'rb') # load the `key` file
    fernet=Fernet(key.read()) # read the key into the Fernet cryptography object
    token=open("token",'rb') # load the encrypted `token` file
    bot.run((fernet.decrypt(token.read())).decode()) # read the encrypted contents of the `token` file as binary, convert them into encrypted UTF8 text, decrypt the UTF8 text to retrieve the original Discord bot auth token
