# Work with Python 3.6
import pickle
import re
import shutil
import time
from os import path
from random import randint
from threading import Lock

import discord
import mail
import requests

####    #     #                 ##
#   #   ##   ##                #  #
#   #   # # # #               #
# ##    #  #  #      # ###  #####
#   #   #     #  ### ##       #
#   #   #     #      #        #
#   #   #     #      #        #       token

TOKEN = 'NzY2Mzc0OTIzMTczODg4MDkw.X4icRA.ucegXvFx7TcGOm7o1E5OmWxRivs'

client = discord.Client()

emoji_to_role = {
    "norway": b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb4',
    "belgium": b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xaa',
    "germany": b'\xf0\x9f\x87\xa9\xf0\x9f\x87\xaa',
    "united kingdom": b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7',
    "sweden": b'\xf0\x9f\x87\xb8\xf0\x9f\x87\xaa',
    "netherlands": b'\xf0\x9f\x87\xb3\xf0\x9f\x87\xb1',
    "south africa": b'\xf0\x9f\x87\xbf\xf0\x9f\x87\xa6',
    "morocco": b'\xf0\x9f\x87\xb2\xf0\x9f\x87\xa6',
    "france": b'\xf0\x9f\x87\xab\xf0\x9f\x87\xb7',
    "computer": b'\xf0\x9f\x92\xbb'
}

users_code = {"data": []}


def create_new_user(id, email, otp):
    user = {}
    user['id'] = id
    user['email'] = email.lower()
    user['otp'] = otp
    user['verified'] = False
    user['sconwar'] = None
    return user


def save_state():
    out_file = open("data.pkl", "wb")
    pickle.dump(users_code, out_file)
    out_file.close()


def load_state():
    global users_code
    in_file = open("data.pkl", "rb")
    users_code = pickle.load(in_file)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    elif message.guild is None:
        if message.content.startswith('!verify'.lower()) and ("@orangecyberdefense.com" in message.content.lower()):
            # add code to ensure they pick a country

            verified = False
            country_selected = False
            async for member in client.guilds[0].fetch_members():
                if member.id == message.author.id:
                    for user_roles in member.roles:
                        if user_roles.name == "verified":
                            verified = True
                        if user_roles.name in emoji_to_role.keys():
                            country_selected = True

            if not country_selected:
                await message.author.send(
                    "You do not have a country role assigned. To have a country role assigned, please react to the message in the lobby channel with your country's flag.")

            elif not verified and country_selected:
                # todo add check for email is unique

                emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", message.content)

                verified_and_used = False

                for user in users_code['data']:
                    if user['verified'] and user['email'] == emails[0]:
                        verified_and_used = True

                if not verified_and_used:
                    otp = randint(10000, 99999)
                    mail.send_mail(emails[0], otp)
                    await message.author.send(
                        "An email has been sent to {}. Please submit your otp with the command `!otp`.".format(
                            emails[0]))
                    users_code["data"].append(create_new_user(message.author.id, emails[0], otp))
                    save_state()
                else:
                    await message.author.send(
                        "An account has already been verified with the email {}".format(emails[0]))

        elif message.content.startswith('!verify'.lower()) and not (
                "@orangecyberdefense.com" in message.content.lower()):
            await message.author.send("Please provide an email address with @orangecyberdefense.com.")

        # sconwar registration
        elif message.content.startswith('!sconwar register'.lower()):
            async for member in client.guilds[0].fetch_members():
                if member.id == message.author.id:
                    verified = False
                    for user_roles in member.roles:
                        if user_roles.name == "verified":
                            verified = True
                            break

                    if verified:

                        for user in users_code['data']:
                            if user["id"] == message.author.id:
                                if not user["sconwar"] is None:
                                    await member.send(
                                        "You have already registered with sconwar. Your token is {}".format(
                                            user["sconwar"]))
                                    # maybe can store their sconwar uuid? and reply back if they forget/lose it?

                                else:
                                    await message.author.send("Please wait while we register you for sconwar :D")
                                    # add code here to register for sconwar

                                    # sconwar registration
                                    headers = {
                                        'accept': 'application/json',
                                        'token': '9b0c3e10-26ea-48a5-8097-599b4824c35c',  # <-- sekret
                                        'Content-Type': 'application/json',
                                    }

                                    r = requests.post('https://api.sconwar.com/api/player/register',
                                                      headers=headers, json={"name": member.name}, verify=False).json()

                                    if "created" not in r:
                                        await message.author.send("welp, that failed.")
                                        return

                                    # To get name use - member.name
                                    user["sconwar"] = r["uuid"]
                                    save_state()

                                    await message.author.send(
                                        "You have been registered for sconwar, your token is {}".format(
                                            user["sconwar"]))

                    else:
                        await member.send(
                            "Please verify your account first before registering for sconwar. To verify your account, send me a message with `!verify ` and your @orangecyberdefense.com email address so that I can send you an OTP.")


        # if we recieve a DM from any user with the word beautiful then it means they eavesdropped on the Bots only chat, completing the one challenge :D
        elif "beautiful" in message.content.lower() or "bueatiful" in message.content.lower():
            roles = await client.guilds[0].fetch_roles()
            async for member in client.guilds[0].fetch_members():
                if member.id == message.author.id:
                    for role in roles:
                        if str(role) == "challenge:eavesdropper":
                            await member.add_roles(role)
                            await anounce(member.id, role.id)

        elif message.content.startswith('!otp'.lower()):
            for user in users_code['data']:
                if user["id"] == message.author.id:
                    otps = re.findall(r"(?<!\d)\d{5}(?!\d)", message.content)
                    if otps[0] == str(user["otp"]):
                        roles = await client.guilds[0].fetch_roles()
                        async for member in client.guilds[0].fetch_members():
                            if member.id == message.author.id:
                                for role in roles:
                                    if str(role) == "verified":
                                        await member.add_roles(role)
                                        await anounce(member.id, role.id)
                                        user["verified"] = True
                                        save_state()

                                if not '@orangecyberdefense.com' in user['email']:
                                    for role in roles:
                                        if str(role) == "challenge:hacker":
                                            await member.add_roles(role)
                                            await anounce(member.id, role.id)

    elif message.content.startswith('!'):
        msg = 'Hello {0.author.mention}'.format(message)
        channel = message.channel
        await channel.send('Say hello!')

    else:
        counter = 0
        messages = await message.channel.history(limit=200).flatten()

        authors = []
        previous_message_contents = message.content

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
                    else:
                        break
                else:
                    break

            counter += 1
            previous_message_contents = m.content

        if len(authors) > 10:
            roles = await client.guilds[0].fetch_roles()
            for author in authors:
                for role in roles:
                    if str(role) == "challenge:mexican wave":
                        async for member in client.guilds[0].fetch_members():
                            if author.id == member.id:
                                await member.add_roles(role)
                                await anounce(member.id, role.id)


@client.event
async def on_ready():
    if path.exists("data.pkl"):
        load_state()

    if not path.exists('morse.mp3') or not path.exists('robot_countdown.mp3') or not path.exists('robot_talk.mp3'):
        print('Audio files are missing for eavesdropper challenge.')

    # set up lobby message.
    channels = await client.guilds[0].fetch_channels()
    for channel in channels:
        if channel.name == 'lobby':
            messages = await channel.history(limit=1000).flatten()
            intro_exists = False
            for message in messages:
                if 'Welcome all to SenseCon 2020.' in message.content:
                    intro_exists = True

            if not intro_exists:
                await channel.send(
                    '**Welcome all to SenseCon 2020.**\nBefore you can do anything please react to this message with the flag of the region you belong to.\nYour options are: :flag_no:, :flag_se:, :flag_za:, :flag_fr:, :flag_be:, :flag_gb: and :flag_ma:.\nBy reacting with the flag of a country a role will be assigned to you, this will help others know where you are from :D.')
                await channel.send(
                    'Once you have reacted with the flag of your region, please verify yourself with me.\nSend me <@{}>, a direct message with `!verify` and an email address with @orangecyberdefense.com in it.'.format(
                        client.user.id))
                await channel.send(
                    'After verifying, you should have recieved a verified role and able to see all the channels on this server. If you have any issues, please ping either <@{}> or <@{}>'.format(
                        '398925835794645002', '737218332628877342'))

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    return
    pass


@client.event
async def on_raw_reaction_add(payload):
    roles = await client.guilds[0].fetch_roles()

    channel = await client.fetch_channel(payload.channel_id)
    if channel.name == "lobby":
        message = await channel.fetch_message(payload.message_id)
        if 'Welcome all to SenseCon 2020.' in message.content:
            for flag in emoji_to_role:
                if payload.emoji.name.encode('utf8') == emoji_to_role[flag]:
                    for role in roles:
                        if str(role) == flag:
                            await payload.member.add_roles(role)
                            await anounce(payload.member.id, role.id)
                        if flag == 'computer' and str(role) == 'challenge:fuzzer':
                            await payload.member.add_roles(role)
                            await anounce(payload.member.id, role.id)


@client.event
async def on_raw_reaction_remove(payload):
    roles = await client.guilds[0].fetch_roles()

    channel = await client.fetch_channel(payload.channel_id)
    if channel.name == "lobby":
        message = await channel.fetch_message(payload.message_id)
        if "Welcome all to SenseCon 2020." in message.content:
            async for member in client.guilds[0].fetch_members():
                if member.id == payload.user_id:
                    for flag in emoji_to_role:
                        if payload.emoji.name.encode('utf8') == emoji_to_role[flag]:
                            for role in roles:
                                if str(role) == flag:
                                    await member.remove_roles(role)


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
                    await member.add_roles(role)
                    await anounce(member.id, role.id)


@client.event
async def on_member_join(member):
    await member.send(
        "Hello there fellow hacker! Could you please provide us with a @orangecyberdefense.com email address using `!verify` so we can verify you?")


morse_challenge_lock = Lock()


@client.event
async def on_voice_state_update(member, before, after):
    global morse_challenge_lock

    if morse_challenge_lock.locked():
        return

    morse_challenge_lock.acquire()
    try:

        voice_channels = client.guilds[0].voice_channels

        exists = False
        for voice_channel in voice_channels:
            if voice_channel.name == "Bots only":
                exists = True

        if exists:
            return

        counter = 0

        for voice_channel in voice_channels:
            if len(voice_channel.members) > 0:
                counter += 1

        voice_channel = None
        if counter > 5:
            for voice_channel in voice_channels:
                if voice_channel.name == "Bots only":
                    exists = True

            if not exists:
                voice_channel = await client.guilds[0].create_voice_channel("Bots only")
                vc = await voice_channel.connect()
                ffmpeg = shutil.which('ffmpeg')
                vc.play(discord.FFmpegPCMAudio(executable=ffmpeg, source="robot_talk.mp3"))
                while vc.is_playing():
                    time.sleep(.1)

                vc.play(discord.FFmpegPCMAudio(executable=ffmpeg, source="robot_countdown.mp3"))
                while vc.is_playing():
                    time.sleep(.1)

                vc.play(discord.FFmpegPCMAudio(executable=ffmpeg, source="morse.mp3"))
                while vc.is_playing():
                    time.sleep(.1)

                await vc.disconnect()
                await voice_channel.delete()
    finally:
        morse_challenge_lock.release()


async def anounce(member, role):
    channels = await client.guilds[0].fetch_channels()
    for channel in channels:
        if channel.name == 'roles' and isinstance(channel, discord.TextChannel):
            await channel.send('<@{}> was assigned the role <@&{}>'.format(member, role))


client.run(TOKEN)
