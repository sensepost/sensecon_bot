# Work with Python 3.6
import discord
import sqlite3
import time

TOKEN = 'NzY2Mzc0OTIzMTczODg4MDkw.X4icRA.ucegXvFx7TcGOm7o1E5OmWxRivs'

client = discord.Client()

emoji_to_role = {
    "norway": b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb4', 
    "belgium": b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xaa', 
    "germany": b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xaa', 
    "united kingdom" : b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7',
    "sweden" : b'\xf0\x9f\x87\xb8\xf0\x9f\x87\xaa',
    "netherlands" : b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb1',
    "south africa" : b'\xf0\x9f\x87\xbf\xf0\x9f\x87\xa6',
    "morocco" : b'\xf0\x9f\x87\xb2\xf0\x9f\x87\xa6',
    "france" : b'\xf0\x9f\x87\xab\xf0\x9f\x87\xb7'
    }

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    
    elif message.guild is None:
        if "beautiful" in message.content.lower() or "bueatiful" in message.content.lower():
            roles = await client.guilds[0].fetch_roles()
            async for member in client.guilds[0].fetch_members():
                if member.id == message.author.id:
                    for role in roles:
                        if str(role) == "challenge:eavesdropper":
                            await member.add_roles(role)

    elif message.content.startswith('!'):
        msg = 'Hello {0.author.mention}'.format(message)
        channel = message.channel
        await channel.send('Say hello!')

    else:
        counter = 0
        messages = await message.channel.history(limit=200).flatten()
        
        authors = []
        previous_message_contents = message.content

        print("I am here")

        for m in messages:
            
            if counter == 0:
                authors.append(m.author)
                pass
            else:
                if m.content == previous_message_contents:
                    new_author = True
                    for author in authors:
                        if m.author == author:
                            new_author = False
                            break
                    
                    if new_author:
                        authors.append(m.author)
                        print("found a message")
                    else:
                        break
                else:
                    break
            #print(m.content)
            #print(message.content)
            #if message.author == client.user:
            #    counter += 1
            counter+=1
            previous_message_contents = m.content


        if len(authors) > 10:
            roles = await client.guilds[0].fetch_roles()
            for author in authors:
                for role in roles:
                    if str(role) == "challenge:mexican wave":
                        await member.add_roles(role)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    return
    pass
    #initialise roles
    for chanchan in client.get_all_channels():
        if chanchan.name == "announcements":
            print("I see anouncements")
            msgs = await chanchan.history(limit=100).flatten()
            for msg in msgs:
                member = msg.author
                #role = discord.utils.get(msg.server.roles, name="Bots")
                ##print(role)
                #for guild in client.guilds:
                #    roles = await guild.fetch_roles()
                #    for role in roles:
                #        print(role)
                
                print("x")
                for reac in msg.reactions:
                    #print("y")
                    #print(bytes(str(reac)))
                    #print(discord.utils.get(discord.Guild.emojis, name=reac.emoji))
                    #print(discord.utils.get(reac.emoji))
                    #if isinstance(reac.emoji, str):
                    #    print('eh')
                    #else:
                    #print(reac.emoji)
                    print(reac.emoji.encode('utf8'))

                    '''

                    users = await reac.users().flatten()

                    #for guild in client.guilds:
                    #    for member in guild.members:
                    #        print(member.name)


                    members = []
                    async for member in msg.guild.fetch_members():
                        members.append(member)
                    #for mem in members:
                    #    print(mem.name)
                    roles = await msg.guild.fetch_roles()

                    #for u in msg.guild.members:
                    #    print(u.name)
                    
                    #for member in client.get_all_members():
                    #    print("mem "+member.name)

                    #for u in users:
                    #    print("user "+u.name)
                    #pass    
                    for u in users:
                        if reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb4': #Norway
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "norway":
                                            print("added role")
                                            await member.add_roles(role)
                            #await set_role(members, u, "norway")
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xaa': #Blegium
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "belgium":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xaa': #Germany
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "germany":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7': #United Kingdom
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "united kingdom":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xb8\xf0\x9f\x87\xaa': #Sweden
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "sweden":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb1': #Netherlands
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "netherlands":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xbf\xf0\x9f\x87\xa6': #South Africa
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "south africa":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

                        elif reac.emoji.encode('utf8') == b'\xf0\x9f\x87\xb2\xf0\x9f\x87\xa6': #Morocco
                            for member in members:
                                if u.name == member.name:
                                    for role in roles:
                                        if str(role) == "morocco":
                                            print("added role")
                                            await member.add_roles(role)
                            pass

'''



                    

#async def set_role(_members, _user, _role):

    #for member in _members:

    
    #for guild in client.guilds:
    #    for member in guild.members:
    #        if member.name == _user.name:
    #            print("found member")
    #        
        #for role in roles:
        #    if str(role) == _role:
        #        print("did we find it?")
        #        member.add_roles(role)

@client.event
async def on_raw_reaction_add(payload):
    #if payload.guild_id is None:
    #    return  # Reaction is on a private message
    #guild = client.get_guild(payload.guild_id)
    #role = discord.utils.get(guild.roles, name="check-in")
    #member = guild.get_member(payload.user_id)
    #if str(payload.channel_id) in check_in:
    #    await member.add_roles(role, reason="check-in")

    #guild = client.guilds[0]

    #message=await client.get_message(payload.channel_id,payload.message_id)
    #print(message.content)

    roles = await client.guilds[0].fetch_roles()
    #print(payload.emoji.name)

    channel = await client.fetch_channel(payload.channel_id)
    if channel.name == "lobby":
        message = await channel.fetch_message(payload.message_id)
        if "welcome" in message.content:
            for flag in emoji_to_role:
                if payload.emoji.name.encode('utf8') == emoji_to_role[flag]:
                    for role in roles:
                        if str(role) == flag:
                            await payload.member.add_roles(role)
                            print("added role")


@client.event
async def on_raw_reaction_remove(payload):
    roles = await client.guilds[0].fetch_roles()
    #print(payload.emoji.name)
    #print(payload.user_id)

    #print(client.guilds[0].get_member(payload.user_id))

    #for mem in client.guilds[0].members:
    #    print(mem.name)

    #message=await client.get_message(payload.channel_id,payload.message_id)
    #print(message.content)

    channel = await client.fetch_channel(payload.channel_id)
    if channel.name == "lobby":
        message = await channel.fetch_message(payload.message_id)
        if "welcome" in message.content:
            async for member in client.guilds[0].fetch_members():
                if member.id == payload.user_id:
                    for flag in emoji_to_role:
                        if payload.emoji.name.encode('utf8') == emoji_to_role[flag]:
                            for role in roles:
                                if str(role) == flag:
                                    await member.remove_roles(role)
                                    print("removed role")

    #message=await client.get_message(payload.channel_id,payload.message_id)
    #print(message.content)

   
            
        #print(member.name)
        #print(member.id)


@client.event
async def on_raw_message_edit(payload):
    roles = await client.guilds[0].fetch_roles()
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = message.author
    async for member in client.guilds[0].fetch_members():
        if member.id == user.id:
            for role in roles:
                if str(role) == "challenge:sneaky":
                    print("I want to add role")
                    await member.add_roles(role)


@client.event
async def on_member_join(member):
    await member.send("Hello there fellow hacker! Could you please provide us with your Orange Cyberdefense or any Orange email address so we can verify you?")


@client.event
async def on_voice_state_update(member, before, after):
    print("picked up")
    counter = 0
    voice_channels = client.guilds[0].voice_channels
    for voice_channel in voice_channels:
        #someone is in the channel
        print("looping")
        if len(voice_channel.members) > 0:
            print("someone is here")
            counter += 1

    voice_channel = None
    exists = False
    #if more than 5 voice channels have people connected then we should start our secret bot
    if counter > 5:
        for voice_channel in voice_channels:
            if voice_channel.name == "Bots only":
                exists = True

        if not exists:
            voice_channel = await client.guilds[0].create_voice_channel("Bots only")
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(executable="/usr/bin/ffmpeg", source="robot_talk.mp3"))
            # Sleep while audio is playing.
            while vc.is_playing():
                time.sleep(.1)

            vc.play(discord.FFmpegPCMAudio(executable="/usr/bin/ffmpeg", source="robot_countdown.mp3"))
            # Sleep while audio is playing.
            while vc.is_playing():
                time.sleep(.1)

            vc.play(discord.FFmpegPCMAudio(executable="/usr/bin/ffmpeg", source="morse.mp3"))
            # Sleep while audio is playing.
            while vc.is_playing():
                time.sleep(.1)

            await vc.disconnect()
            await voice_channel.delete()



'''
    

'''


'''


    if payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb4': #Norway
        
        #await set_role(members, u, "norway")
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xaa': #Blegium
        for role in roles:
            if str(role) == "belgium":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xaa': #Germany
        for role in roles:
            if str(role) == "germany":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7': #United Kingdom
        for role in roles:
            if str(role) == "united kingdom":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xb8\xf0\x9f\x87\xaa': #Sweden
        for role in roles:
            if str(role) == "sweden":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb1': #Netherlands
        for role in roles:
            if str(role) == "netherlands":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xbf\xf0\x9f\x87\xa6': #South Africa
        for role in roles:
            if str(role) == "south africa":
                print("added role")
                await payload.member.add_roles(role)
        pass

    elif payload.emoji.name.encode('utf8') == b'\xf0\x9f\x87\xb2\xf0\x9f\x87\xa6': #Morocco
        for role in roles:
            if str(role) == "morocco":
                print("added role")
                await payload.member.add_roles(role)
        pass
'''

    #channel = client.get_channel(message.channel_id)
    #await channel.send('I saw a reaction!')

client.run(TOKEN)