#a multiguild folder is needed, also inside of that multiguild server it is requiered to make a "servers" folder

import json
import os

import discord
from discord import member
import discord.ext
from discord.ext import commands
from discord.ext.commands import has_permissions
from typing import Optional
import asyncio
import random
from random import choice
import shutil

from discord.utils import time_snowflake
from discord.webhook.async_ import interaction_message_response_params

from discord import ui
import datetime
from datetime import datetime, time, timedelta
import time

#intents
intents = discord.Intents.default()

intents.bans = True
intents.message_content = True
intents.members = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

#keepalive and prefix config
bot_prefix = "<"



#gets token
bot_token = os.environ["bot_token"]

#prefix
client = commands.Bot(command_prefix=bot_prefix, intents=discord.Intents.all())
client.remove_command('help')

#status/onready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{round(client.latency * 1000)}ms | /help"))
    print(f"Logged into {client.user.name}")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(e)

    i = 0
    for guild in client.guilds:
        directory = str(guild.id)
        parent = "./multiguild/servers/"
        path = os.path.join(parent, directory)
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
            i += 1
    print(f"Created {i} directories for servers.")
    created_folders = 0

    for guild in client.guilds:
        server_id = str(guild.id)
        folder_name = f'mini-cad/{server_id}'
        os.makedirs(folder_name, exist_ok=True)

        subfolders = ['name-database', 'plate-database', 'warrant-status']
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_name, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            created_folders += 1

    if created_folders > 0:
        print(f'Created {created_folders} mini-cad folders')
    else:
        print('All mini-cad folders created')

@client.event
async def on_error(event, *args, **kwargs):
    print(f"Error during {event}: {str(args[0])}")

#Premium whitelist system
@client.event
async def on_guild_join(guild):
    required_role_name = " "
    bot_server_id = " "

    invites = await guild.invites()
    if invites:
        inviter = invites[0].inviter
        bot_server = client.get_guild(bot_server_id)
        inviter_in_bot_server = bot_server.get_member(inviter.id)

        if not any(role.name == required_role_name for role in inviter_in_bot_server.roles):
            try:
                await invite.send("Sorry, you don't have the required role to invite this bot to the server.")
            except discord.HTTPException:
                owner = await guild.fetch_owner()
                channel = discord.utils.get(guild.text_channels, name="general")
                if channel:
                    await channel.send(f"Error: {inviter.mention} invited the bot, but they don't have the required role. Contact {owner.mention}.")
                else:
                    system_channel = guild.system_channel
                    if system_channel:
                        await system_channel.send(f"Error: {inviter.mention} invited the bot, but they don't have the required role. Contact {owner.mention}.")
                    else:
                        text_channels = list(guild.text_channels)
                        if text_channels:
                            await text_channels[0].send(f"Error: {inviter.mention} invited the bot, but they don't have the required role. Contact {owner.mention}.")

            log_channel = client.get_channel(1151056468204859412)
            embed_log = discord.Embed(title="Bot Joined Error", description=f"Bot left {guild.name} because the inviter didn't have the required role.")
            await log_channel.send(embed=embed_log)

            await guild.leave()
        else:
            embed = discord.Embed(title="Bot Joined", description=f"The inviter has the required role in the server {guild.name}.")
            print(f"Bot joined {guild.name}, the inviter has the required role.")
    else:
        print("Could not determine inviter.")

    log_channel = client.get_channel(1151056468204859412)
    await log_channel.send(embed=embed)


######### Bug Report Module #########

@client.tree.command()
async def bug_report(interaction, bug_description: str):
                  from datetime import datetime

                  if not os.path.exists("bot-bug-reports"):
                      os.mkdir("bot-bug-reports")

                  bug_number = len(os.listdir("bot-bug-reports")) + 1
                  user_id = interaction.user.id
                  filename = f"bot-bug-reports/bug-{bug_number}_{user_id}.json"

                  user_name = interaction.user.name
                  current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                  server_name = interaction.guild.name

                  bug_data = {
                      "user_id": user_id,
                      "user_name": user_name,
                      "server_name": server_name,
                      "bug_report": bug_description,
                      "reported_at": current_time
                  }

                  with open(filename, 'w') as file:
                      json.dump(bug_data, file, indent=4)

                  receiving_channel_file = "./bot-bug-reports/receiving-channel"
                  if os.path.exists(receiving_channel_file):
                      with open(receiving_channel_file, 'r') as channel_file:
                          receiving_channel_id = int(channel_file.read().strip())
                          receiving_channel = client.get_channel(receiving_channel_id)

                      if receiving_channel:
                          report_message = f"Bug report from {user_name} in server {server_name}:\n{bug_description}\nReported at {current_time}"
                          await receiving_channel.send(report_message)
                      else:
                          await interaction.response.send_message("Receiving channel not found. Please configure it.")
                  else:
                      await interaction.response.send_message("Receiving channel not configured. Please set it up.")

                  await interaction.response.send_message(f"Bug report has been sent to the developers. We appreciate your assistance in helping improve the bot!")
                  await interaction.response.send_message("Thank you for reporting the bug!")


@client.tree.command()
async def set_bug_receiving_channel(interaction, receiving_channel: discord.TextChannel):
          if not os.path.exists("bot-bug-reports"):
              os.mkdir("bot-bug-reports")

          receiving_channel_file = "./bot-bug-reports/receiving-channel"
          with open(receiving_channel_file, 'w') as file:
              file.write(str(receiving_channel.id))

          await interaction.response.send_message(f"Receiving channel set to {receiving_channel.mention} for bug reports.")


@client.tree.command()
async def view_bug_receiving_channel(interaction):
    receiving_channel_file = "./bot-bug-reports/receiving-channel"
    if os.path.exists(receiving_channel_file):
        with open(receiving_channel_file, 'r') as file:
            receiving_channel_id = int(file.read().strip())
            receiving_channel = interaction.guild.get_channel(receiving_channel_id)

        if receiving_channel:
            embed = discord.Embed(
                title="Bug Receiving Channel",
                description=f"Channel Name: {receiving_channel.name}\nChannel Mention: {receiving_channel.mention}\nChannel ID: {receiving_channel_id}",
                color=discord.Color.blue()
            )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("The configured receiving channel does not exist in this server.")
    else:
        await interaction.response.send_message("Receiving channel not configured. Please set it up using the set_bug_receiving_channel command.")


#####################################
###########ECON COMMANDS#############
#####################################


@client.event
async def on_member_join(member):
    guild = member.guild
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"users": []}

    member_id = str(member.id)

    found = False
    for user_data in data["users"]:
        if member_id in user_data:
            found = True
            break

    if not found:

      user_data = {
            member_id: {
                "bank": 5000,
                "cash": 500
            }
        }
      data["users"].append(user_data)

      with open(file_path, "w") as file:
            json.dump(data, file, indent=4)


@client.tree.command(name="refresheconomy", description="Refreshes the economy files")
@has_permissions(administrator=True)
async def refresh_economy(interaction:discord.Interaction):
    embed = discord.Embed(title="Refreshing...",description="Refreshing economy files...", color = discord.Colour.yellow())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    guild = interaction.guild
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    with open(file_path, "r") as file:
        data = json.load(file)

    for member in guild.members:
        member_id = str(member.id)

        found = False
        for user_data in data["users"]:
            if member_id in user_data:
                found = True
                break

        if not found:
            user_data = {
                member_id: {
                    "bank": 5000,
                    "cash": 500
                }
            }
            data["users"].append(user_data)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    await asyncio.sleep(3)
    embed_two = discord.Embed(title="Successfully Refreshed! :heavy_check_mark:",description="Economy refreshed!", color = discord.Colour.yellow())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.edit_original_response(embed=embed_two)


@client.tree.command(name="deposit",description="Deposit a selected amount into your bank account")
async def deposit(interaction:discord.Interaction,amount:int):
    guild = interaction.guild
    id = interaction.user.id
    embed = discord.Embed(title="Depositing...",description=f"Depositing ${amount}...", color = discord.Colour.green())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    edited = False
    found = False
    for user_data in data["users"]:
        if str(id) in user_data:
            found = True
            cash_amount = user_data[str(id)]["cash"]
            if user_data[str(id)]["cash"] >= amount:
                user_data[str(id)]["bank"] += amount
                user_data[str(id)]["cash"] -= amount
            else:
                embed_two = discord.Embed(title="**ERROR**",description=f"You don't have that much cash. Your current cash balance is ${cash_amount}", color = discord.Colour.red())
                edited = True
                embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                await interaction.edit_original_response(embed=embed_two)
            break

    if not found:
        user_data = {
                str(id): {
                    "bank": 5000+amount,
                    "cash": 500-amount,
                }
            }
        data["users"].append(user_data)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    cash_amount = user_data[str(id)]["cash"]
    bank_amount = user_data[str(id)]["bank"]
    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="Deposited!",description=f"Deposited ${amount}. You have ${cash_amount} in cash and ${bank_amount} in bank.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)

@client.tree.command(name="withdraw",description="Withdraw a selected amount into cash")
async def withdraw(interaction:discord.Interaction,amount:int):
    guild = interaction.guild
    id = interaction.user.id
    embed = discord.Embed(title="Withdrawing...",description=f"Withdrawing {amount}$...", color = discord.Colour.green())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    edited = False
    found = False
    for user_data in data["users"]:
        if str(id) in user_data:
            found = True
            bank_amount = user_data[str(id)]["bank"]
            if user_data[str(id)]["bank"] >= amount:
                user_data[str(id)]["bank"] -= amount
                user_data[str(id)]["cash"] += amount
            else:
                edited = True
                embed = discord.Embed(title="Insufficient Funds",description=f"You don't have that much in your bank. Your current cash balance is ${bank_amount}", color = discord.Colour.green())
                embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                await interaction.response.send_message(embed=embed)
            break

    if not found:
        user_data = {
                str(id): {
                    "bank": 5000-amount,
                    "cash": 500+amount,
                }
            }
        data["users"].append(user_data)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    cash_amount = user_data[str(id)]["cash"]
    bank_amount = user_data[str(id)]["bank"]
    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="Withdrew! :moneybag:",description=f"You withdrew ${amount}. You have ${cash_amount} in cash and ${bank_amount} in bank.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)

@client.tree.command(name="create_inventory",description="Creates the necessary files for the inventory || Necessary for the economy")
async def inv(interaction:discord.Interaction):
    await interaction.response.send_message("Creating files...",ephemeral=True)
    guild = interaction.guild

    directory = "members"
    parent = f"./multiguild/servers/{str(guild.id)}"
    path = os.path.join(parent,directory)
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)

    for member in guild.members:
        inventory = {
            "items":{
                "Water":{
                    "amount":0
                },
                "Candy Bar":{
                    "amount":0
                },
                "Burger":{
                    "amount":0
                },
                "Ball":{
                    "amount":0
                },
                "Hammer":{
                    "amount":0
                },
                "Knuckle Duster":{
                    "amount":0
                },
                "Jerry Can":{
                    "amount":0
                },
                "CrowBar":{
                    "amount":0
                },
                "BaseBall Bat":{
                    "amount":0
                },
                "Pistol":{
                    "amount":0
                },
                "Shotgun":{
                    "amount":0
                },
                "Assault Rifle":{
                    "amount":0
                },
                "Submachine Gun":{
                    "amount":0
                },
                "Light-Machine Gun":{
                    "amount":0
                },
                "Sniper Rifle":{
                    "amount":0
                },
                "Heavy Weapon":{
                    "amount":0
                },
            }
        }
        with open(f"./multiguild/servers/{str(guild.id)}/members/{str(member.id)}.json","w") as file:
            json.dump(inventory,file,indent=4)
    await interaction.edit_original_response(content="Files created!")




class BuyItems(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Water",description="$4"),
            discord.SelectOption(label="Candy Bar",description="$4"),
            discord.SelectOption(label="Burger",description="$8"),
            discord.SelectOption(label="Ball",description="$15"),
            discord.SelectOption(label="Hammer",description="$15"),
            discord.SelectOption(label="Knuckle Duster",description="$20"),
            discord.SelectOption(label="Jerry Can",description="20"),
            discord.SelectOption(label="CrowBar",description="$30"),
            discord.SelectOption(label="BaseBall Bat",description="$35"),
            discord.SelectOption(label="Pistol",description="$450"),
            discord.SelectOption(label="Shotgun",description="$700"),
            discord.SelectOption(label="Assault Rifle",description="$1200"),
            discord.SelectOption(label="Submachine Gun",description="$2000"),
            discord.SelectOption(label="Light-Machine Gun",description="$3500"),
            discord.SelectOption(label="Sniper Rifle",description="$8000"),
            discord.SelectOption(label="Heavy Weapon",description="$10000")

        ]
        super().__init__(placeholder="Select item(s) to buy",options=options,min_values=1,max_values=16)
    async def callback(self, interaction: discord.Interaction):
        value = ", ".join(self.values)
        embed = discord.Embed(title="Purchasing...",description="Loading...")
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed,ephemeral=True)
        guild = interaction.guild
        user_id = interaction.user.id
        file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"

        with open(file_path, "r") as file:
            data = json.load(file)

        found = False
        edited = False
        total_cost = 0

        for selected_label in value.split(", "):
            for option in self.options:
                if option.label == selected_label:
                    description = option.description
                    item_cost = int(description.strip('$'))
                    total_cost += item_cost
                    break

        for user_data in data["users"]:
            if str(user_id) in user_data:
                found = True
                cash_amount = user_data[str(user_id)]["cash"]
                if cash_amount >= total_cost:
                    user_data[str(user_id)]["cash"] -= total_cost
                    edited = True
                    break

        if not found:
            embed = discord.Embed(title="**ERROR** :exclamation:",description="You don't have an account! Please contact the server administrators!", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
        elif not edited:
            embed_two = discord.Embed(title="**ERROR** :exclamation:",description=f"You don't have enough cash. Your current cash balance is ${cash_amount}", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed_two)
        else:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

            member = interaction.user

            with open(f"./multiguild/servers/{str(guild.id)}/members/{str(member.id)}.json", "r") as file:
                data2 = json.load(file)

            for item_name in value.split(", "):
                if item_name in data2["items"]:
                    data2["items"][item_name]["amount"] += 1

            with open(f"./multiguild/servers/{str(guild.id)}/members/{str(member.id)}.json", "w") as file:
                json.dump(data2, file, indent=4)

            await asyncio.sleep(3)
            embed = discord.Embed(title="Purchased Item! :moneybag: ", description=f"You successfully bought {value}. Your remaining cash is ${cash_amount - total_cost}", color=discord.Colour.green())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)

class BuyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(BuyItems())


@client.tree.command(name="buy",description="Choose item(s) to buy:")
async def buy(interaction:discord.Interaction):
    embed = discord.Embed(title="item menu :bookmark_tabs:",description=f"Choose item(s) to buy:", color = discord.Colour.yellow())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed, ephemeral=True, view=BuyView())

@client.tree.command(name="wire", description="Wire an amount to the selected member")
async def wire(interaction: discord.Interaction, member: discord.Member, amount: int):
    guild = interaction.guild
    id = interaction.user.id
    wire_id = member.id
    embed = discord.Embed(title="Wiring...",description=f"Wiring ${amount}...", color = discord.Colour.green())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    edited = False

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        sender_found = False
        receiver_found = False
        sender_bank = 0

        for user_data in data["users"]:
            if str(id) in user_data:
                sender_found = True
                sender_bank = user_data[str(id)]["bank"]
                if sender_bank >= amount:
                    user_data[str(id)]["bank"] -= amount
                else:
                    edited = True
                    embed = discord.Embed(title="Insufficient Funds! :exclamation:",description=f"You don't have that much in your bank. Your current bank balance is ${sender_bank}", color = discord.Colour.red())
                    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                    await interaction.response.send_message(embed=embed)
                    return

            if str(wire_id) in user_data:
                receiver_found = True
                user_data[str(wire_id)]["bank"] += amount

        if not sender_found or not receiver_found:
            edited = True
            embed = discord.Embed(title="**ERROR** :exclamation:",description="You or the person you are trying to wire does not have an account. Contact an administrator to resolve the problem.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
            return

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    except FileNotFoundError:
        embed = discord.Embed(title="**ERROR** :exclamation:",description="File not found. Please contact the server admins.", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)
        return
    except json.JSONDecodeError:
        embed = discord.Embed(title="**ERROR** :exclamation:",description="Error reading user data. Please contact the server admins.", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)
        return

    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="Wired Successfully! :moneybag:",description=f"Wired ${amount} to {member.mention}. You have ${sender_bank - amount} in bank.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)


@client.tree.command(name="pay", description="Pays an amount to the selected member")
async def pay(interaction: discord.Interaction, member: discord.Member, amount: int):
    guild = interaction.guild
    id = interaction.user.id
    wire_id = member.id
    embed = discord.Embed(title="Paying...",description=f"Paying ${amount}...", color = discord.Colour.green())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    edited = False

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        sender_found = False
        receiver_found = False
        sender_cash = 0

        for user_data in data["users"]:
            if str(id) in user_data:
                sender_found = True
                sender_cash = user_data[str(id)]["cash"]
                if sender_cash >= amount:
                    user_data[str(id)]["cash"] -= amount
                else:
                    edited = True
                    embed = discord.Embed(title="Insufficient Funds! :exclamation:",description=f"You don't have that much in cash. Your current bank balance is ${sender_cash}", color = discord.Colour.red())
                    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                    await interaction.edit_original_response(embed=embed)
                    return

            if str(wire_id) in user_data:
                receiver_found = True
                user_data[str(wire_id)]["cash"] += amount

        if not sender_found or not receiver_found:
            edited = True
            embed = discord.Embed(title="**ERROR** :exclamation:",description="You or the person you are trying to wire does not have an account. Contact an administrator to resolve the problem.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
            return

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    except FileNotFoundError:
        embed = discord.Embed(title="*ERROR** :exclamation:",description="File not found. Please contact the server admins.", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)
        return
    except json.JSONDecodeError:
        embed = discord.Embed(title="*ERROR** :exclamation:",description="Error reading user data. Please contact the server admins.", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)
        return

    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="Payment Successful! :moneybag:",description=f"Paid ${amount} to {member.mention}. You have ${sender_cash - amount} in cash.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)


@client.tree.command(name="balance",description="Shows your economy balance.")
async def balance(interaction:discord.Interaction):
    guild = interaction.guild
    id = interaction.user.id
    embed = discord.Embed(title="Searching For Account...",description=f"Finding account...", color = discord.Colour.green())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
    with open(file_path, "r") as file:
        data = json.load(file)
    edited = False
    found = False
    for user_data in data["users"]:
        if str(id) in user_data:
            found = True
            break
    if not found:
        edited = True
        embed = discord.Embed(title="**ERROR** :exclamation:",description="You don't have an account. Please contact the server admins for more information", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

    cash_amount = user_data[str(id)]["cash"]
    bank_amount = user_data[str(id)]["bank"]
    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="User Balance :moneybag: ",description=f"You have ${cash_amount} in cash and ${bank_amount} in bank.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)

COOLDOWN_DURATION = 86400
last_execution = {}

@client.tree.command(name="collect", description="Collects daily income.")
@commands.cooldown(1, COOLDOWN_DURATION, commands.BucketType.user)
async def collect(interaction: discord.Interaction):
    embed = discord.Embed(title="Checking...",description="Checking for last collection time...", color = discord.Colour.yellow())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)
    id = interaction.user.id
    guild = interaction.guild
    current_time = datetime.now()
    amount = 250
    edited = False

    if id in last_execution:
        cooldown_end_time = last_execution[id] + timedelta(seconds=COOLDOWN_DURATION)
        if current_time < cooldown_end_time:
            remaining_time = cooldown_end_time - current_time
            edited = True
            embed = discord.Embed(title="**ERROR** :exclamation:",description=f"Sorry, you can use this command again in {int(remaining_time.total_seconds())} seconds.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
            return
    else:
        file_path = f"./multiguild/servers/{guild.id}/{guild.id}.json"
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            found = False
            for user_data in data["users"]:
                if str(id) in user_data:
                    found = True
                    user_data[str(id)]["cash"] += amount
                    break
            if not found:
                edited = True
                embed = discord.Embed(title="**ERROR** :exclamation:",description="You don't have an account. Please contact the server admins for more information.", color = discord.Colour.red())
                embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                await interaction.edit_original_response(embed=embed)
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

            last_execution[id] = current_time
        except FileNotFoundError:
            embed = discord.Embed(title="**ERROR** :exclamation:",description="File not found. Please contact the server admins.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
            return
        except json.JSONDecodeError:
            embed = discord.Embed(title="**ERROR** :exclamation:",description="Error reading user data. Please contact the server admins.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.edit_original_response(embed=embed)
            return

    cash_amount = user_data[str(id)]["cash"]
    if not edited:
        await asyncio.sleep(3)
        embed = discord.Embed(title="Collected Income Successfully! :moneybag: ",description=f"You have collected ${amount} in cash. Your current cash is ${cash_amount}.", color = discord.Colour.green())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.edit_original_response(embed=embed)



#####################################
######## MINI CAD COMMANDS ##########
#####################################


@client.event
async def on_guild_join(guild):
    try:
        server_id = str(guild.id)
        folder_name = f'mini-cad/{server_id}'
        os.makedirs(folder_name, exist_ok=True)

        subfolders = ['name-database', 'plate-database', 'warrant-status']
        for subfolder in subfolders:
            os.makedirs(os.path.join(folder_name, subfolder), exist_ok=True)
    except Exception as e:
        print(f"Error during on_guild_join: {str(e)}")

@client.event
async def on_guild_remove(guild):
    try:
        server_id = str(guild.id)
        folder_name = f'mini-cad/{server_id}'
        if os.path.exists(folder_name):
            os.rmdir(folder_name)
    except Exception as e:
        print(f"Error during on_guild_remove: {str(e)}")

@client.event
async def on_member_join(member):
    try:
        server_id = str(member.guild.id)
        user_id = str(member.id)
        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'
        os.makedirs(user_folder, exist_ok=True)
    except Exception as e:
        print(f"Error during on_member_join: {str(e)}")


def get_active_character_name(server_id, user_id):
  user_folder = f'mini-cad/{server_id}/name-database/{user_id}'
  active_character_file = os.path.join(user_folder, 'active_character.json')

  if os.path.exists(active_character_file):
      with open(active_character_file, 'r') as active_char_file:
          active_character_data = json.load(active_char_file)
          return active_character_data.get('Name')

  return None


@client.tree.command(name='new_character', description='Create a new character')
async def new_character(
        interaction: discord.Interaction,
        name: str,
        sex: str,
        ethnicity: str,
        date_of_birth: str,
        license_status: str
):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'

        os.makedirs(user_folder, exist_ok=True)

        timestamp = int(time.time())
        character_id = f'character_{timestamp}'

        character_data = {
            'Name': name,
            'Sex': sex,
            'Ethnicity': ethnicity,
            'Date of Birth': date_of_birth,
            'License Status': license_status
        }

        character_file = os.path.join(user_folder, f'{character_id}_data.json')
        with open(character_file, 'w') as json_file:
            json.dump(character_data, json_file)

        embed = discord.Embed(
            title="Character Created :bookmark_tabs:",
            description=f"Character with ID `{character_id}` has been created.\n"
                        f"Name: {name}\n"
                        f"Sex: {sex}\n"
                        f"Ethnicity: {ethnicity}\n"
                        f"Date of Birth: {date_of_birth}\n"
                        f"License Status: {license_status}",
            color=0x27ae60
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during new_name: {str(e)}")

@client.tree.command(name='list_registered_characters', description='List all registered characters')
async def list_registered_characters(interaction: discord.Interaction):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'

        if not os.path.exists(user_folder):
            embed = discord.Embed(
                title="No Registered Characters :x:",
                description="You haven't created any characters yet.",
                color= discord.Colour.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        character_files = [file for file in os.listdir(user_folder) if file.endswith("_data.json")]

        if not character_files:
            embed = discord.Embed(
                title="No Registered Characters :x:",
                description="You haven't created any characters yet.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        character_info = []

        for character_file in character_files:
            with open(os.path.join(user_folder, character_file), 'r') as json_file:
                character_data = json.load(json_file)

            info = (
                f"**Name:** {character_data['Name']}\n"
                f"**Sex:** {character_data['Sex']}\n"
                f"**Ethnicity:** {character_data['Ethnicity']}\n"
                f"**Date of Birth:** {character_data['Date of Birth']}\n"
                f"**License Status:** {character_data['License Status']}"
            )

            character_info.append(info)

        characters_info_str = '\n\n---\n\n'.join(character_info)

        embed = discord.Embed(
            title="Registered Characters :bookmark_tabs:",
            description=characters_info_str,
            color= discord.Colour.yellow()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during list_registered_characters: {str(e)}")

@client.tree.command(name='show_id', description="Display character's information")
async def show_id(interaction: discord.Interaction):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'
        active_character_file = os.path.join(user_folder, 'active_character.json')

        if not os.path.exists(active_character_file):
            embed = discord.Embed(
                title="No Active Character :x:",
                description="You haven't set an active character. Use `/set_active_character` to set one.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        with open(active_character_file, 'r') as json_file:
            character_data = json.load(json_file)

        info = (
            f"**Name:** {character_data['Name']}\n"
            f"**Sex:** {character_data['Sex']}\n"
            f"**Ethnicity:** {character_data['Ethnicity']}\n"
            f"**Date of Birth:** {character_data['Date of Birth']}\n"
            f"**License Status:** {character_data['License Status']}"
        )

        embed = discord.Embed(
            title="Character Information :bookmark_tabs:",
            description=info,
            color= discord.Colour.yellow()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during show_id: {str(e)}")

@client.tree.command(name='set_active_character', description='Set your active character')
async def set_active_character(interaction: discord.Interaction, character_name: str):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'

        if not os.path.exists(user_folder):
            embed = discord.Embed(
                title="No Registered Characters :x:",
                description="You haven't created any characters yet.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        character_files = [file for file in os.listdir(user_folder) if file.endswith("_data.json")]

        found = False

        for character_file in character_files:
            with open(os.path.join(user_folder, character_file), 'r') as json_file:
                character_data = json.load(json_file)

            if character_data.get('Name') == character_name:
                found = True
                active_character_file = os.path.join(user_folder, 'active_character.json')

                with open(active_character_file, 'w') as active_char_file:
                    json.dump(character_data, active_char_file)

                embed = discord.Embed(
                    title="Active Character Set :bookmark_tabs:",
                    description=f"Your active character is now: {character_name}",
                    color= discord.Colour.green()
                )
                embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                await interaction.response.send_message(embed=embed)
                break

        if not found:
            embed = discord.Embed(
                title="Character Not Found :x:",
                description=f"No character with the name `{character_name}` found in your characters.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during set_active_character: {str(e)}")

@client.tree.command(name='set_id_state', description='Set the state on the ID')
async def set_id_state(interaction: discord.Interaction, state_name: str):
    try:
        server_id = str(interaction.guild.id)
        state_file_path = f'mini-cad/{server_id}/{server_id}-id_state.json'

        state_info = {"state_name": state_name}

        with open(state_file_path, 'w') as state_file:
            json.dump(state_info, state_file)

        embed = discord.Embed(
            title="ID State Set :identification_card:",
            description=f"The state on the ID has been set to: {state_name}",
            color= discord.Colour.green()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during set_id_state: {str(e)}")

@client.tree.command(name='register_vehicle', description='Register a vehicle')
async def register_vehicle(
              interaction: discord.Interaction,
              vehicle_make: str,
              vehicle_model: str,
              vehicle_color: str,
              registration_status: str,
              plate_number: str
      ):
          try:
              server_id = str(interaction.guild.id)
              user_id = str(interaction.user.id)
              character_name = get_active_character_name(server_id, user_id)
              if character_name is None:
                  embed = discord.Embed(
                      title="No Active Character Set",
                      description="You must set an active character before registering a vehicle.",
                      color=discord.Colour.red()
                  )
                  await interaction.response.send_message(embed=embed)
                  return

              user_folder = f'mini-cad/{server_id}/plate-database/{user_id}'

              timestamp = int(time.time())
              vehicle_id = f'vehicle_{timestamp}'

              vehicle_data = {
                  'Vehicle Make': vehicle_make,
                  'Vehicle Model': vehicle_model,
                  'Vehicle Color': vehicle_color,
                  'Registration Status': registration_status,
                  'Plate Number': plate_number,
                  'Registered Owner': character_name
              }

              vehicle_file = os.path.join(user_folder, f'{vehicle_id}.json')
              with open(vehicle_file, 'w') as json_file:
                  json.dump(vehicle_data, json_file)

              embed = discord.Embed(
                  title="Vehicle Registered",
                  description=f"Vehicle with ID `{vehicle_id}` has been registered.\n"
                              f"Make: {vehicle_make}\n"
                              f"Model: {vehicle_model}\n"
                              f"Color: {vehicle_color}\n"
                              f"Plate Number: {plate_number}\n"
                              f"Registration Status: {registration_status}\n"
                              f"Registered Owner: {character_name}",
                  color=discord.Colour.green()
              )
              await interaction.response.send_message(embed=embed)

          except Exception as e:
              print(f"Error during register_vehicle: {str(e)}")


@client.tree.command(name='list_registered_vehicles', description='List all registered vehicles')
async def list_registered_vehicles(interaction: discord.Interaction):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/plate-database/{user_id}'

        if not os.path.exists(user_folder):
            embed = discord.Embed(
                title="No Registered Vehicles :x:",
                description="You haven't registered any vehicles yet.",
                color=discord.Colour.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        vehicle_files = [file for file in os.listdir(user_folder) if file.endswith(".json")]

        if not vehicle_files:
            embed = discord.Embed(
                title="No Registered Vehicles :x:",
                description="You haven't registered any vehicles yet.",
                color=discord.Colour.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        vehicle_info = []

        for vehicle_file in vehicle_files:
            with open(os.path.join(user_folder, vehicle_file), 'r') as json_file:
                vehicle_data = json.load(json_file)

            info = (
                f"**Plate Number:** {vehicle_data['Plate Number']}\n"
                f"**Make:** {vehicle_data['Vehicle Make']}\n"
                f"**Model:** {vehicle_data['Vehicle Model']}\n"
                f"**Color:** {vehicle_data['Vehicle Color']}\n"
                f"**Registration Status:** {vehicle_data['Registration Status']}\n"
                f"**Registered Owner:** {vehicle_data.get('Registered Owner', 'N/A')}"
            )

            vehicle_info.append(info)

        vehicles_info_str = '\n\n---\n\n'.join(vehicle_info)

        embed = discord.Embed(
            title="Registered Vehicles :blue_car:",
            description=vehicles_info_str,
            color=discord.Colour.yellow()
        )
        embed.set_footer(text='CopBot',
                         icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during list_registered_vehicles: {str(e)}")

@client.tree.command(name='delete_vehicle', description='Delete a registered vehicle by license plate')
async def delete_vehicle(interaction: discord.Interaction, plate_number: str):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/plate-database/{user_id}'

        if not os.path.exists(user_folder):
            embed = discord.Embed(
                title="No Registered Vehicles :x:",
                description="You haven't registered any vehicles yet.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        vehicle_files = [file for file in os.listdir(user_folder) if file.endswith(".json")]

        deleted = False

        for vehicle_file in vehicle_files:
            with open(os.path.join(user_folder, vehicle_file), 'r') as json_file:
                vehicle_data = json.load(json_file)

            if vehicle_data.get('Plate Number') == plate_number:
                os.remove(os.path.join(user_folder, vehicle_file))
                deleted = True
                break

        if deleted:
            embed = discord.Embed(
                title="Vehicle Deleted :closed_book:",
                description=f"Vehicle with Plate Number `{plate_number}` has been deleted.",
                color= discord.Colour.green()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Vehicle Not Found :x:",
                description=f"No vehicle with Plate Number `{plate_number}` found in your registered vehicles.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during delete_vehicle: {str(e)}")

@client.tree.command(name='delete_character', description='Delete a character by name')
async def delete_character(interaction: discord.Interaction, character_name: str):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/name-database/{user_id}'

        if not os.path.exists(user_folder):
            embed = discord.Embed(
                title="No Characters Found :x:",
                description="You don't have any characters registered.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        character_files = [file for file in os.listdir(user_folder) if file.endswith("_data.json")]

        deleted = False

        for character_file in character_files:
            with open(os.path.join(user_folder, character_file), 'r') as json_file:
                character_data = json.load(json_file)

            if character_data.get('Name') == character_name:
                os.remove(os.path.join(user_folder, character_file))
                deleted = True
                break

        if deleted:
            embed = discord.Embed(
                title="Character Deleted :closed_book:",
                description=f"Character with name `{character_name}` has been deleted.",
                color= discord.Colour.green()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Character Not Found :x:",
                description=f"No character with name `{character_name}` found in your characters.",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during delete_character: {str(e)}")

@client.tree.command(name='create_warrant', description='Create a new warrant')
async def create_warrant(
        interaction: discord.Interaction,
        character_name: str,
        issuing_department: str,
        reason: str,
        date: str
):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/warrant-status/{user_id}'

        os.makedirs(user_folder, exist_ok=True)

        open_warrants_folder = os.path.join(user_folder, 'open-warrants')
        os.makedirs(open_warrants_folder, exist_ok=True)

        case_id = str(random.randint(100000, 999999))

        warrant_data = {
            'Character Name': character_name,
            'Issuing Department': issuing_department,
            'Reason': reason,
            'Date': date,
            'Case ID': case_id
        }

        warrant_file = os.path.join(open_warrants_folder, f'{case_id}.json')
        with open(warrant_file, 'w') as json_file:
            json.dump(warrant_data, json_file)

        embed = discord.Embed(
            title="Warrant Created :bookmark_tabs:",
            description=f"Case ID: `{case_id}`\n"
                        f"Character Name: {character_name}\n"
                        f"Issuing Department: {issuing_department}\n"
                        f"Reason: {reason}\n"
                        f"Date: {date}",
            color= discord.Colour.green()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during create_warrant: {str(e)}")

@client.tree.command(name='close_warrant', description='Close a warrant by Case ID')
async def close_warrant(
        interaction: discord.Interaction,
        case_id: str
):
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_folder = f'mini-cad/{server_id}/warrant-status/{user_id}'

        open_warrants_folder = os.path.join(user_folder, 'open-warrants')
        closed_warrants_folder = os.path.join(user_folder, 'closed-warrants')

        os.makedirs(closed_warrants_folder, exist_ok=True)

        warrant_file = os.path.join(open_warrants_folder, f'{case_id}.json')

        if not os.path.exists(warrant_file):
            embed = discord.Embed(
                title="Warrant Not Found :x:",
                description=f"No open warrant found with Case ID: `{case_id}`",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        closed_warrant_file = os.path.join(closed_warrants_folder, f'{case_id}.json')
        shutil.move(warrant_file, closed_warrant_file)

        embed = discord.Embed(
            title="Warrant Closed :closed_book:",
            description=f"Warrant with Case ID: `{case_id}` has been closed.",
            color= discord.Colour.green()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during close_warrant: {str(e)}")

@client.tree.command(name='search_name', description='Search for character information by name')
async def search_name(
        interaction: discord.Interaction,
        character_name: str
):
    try:
        server_id = str(interaction.guild.id)
        user_folder = f'mini-cad/{server_id}/name-database'

        found_character_info = []
        found_warrant_info = []
        isFelon = False

        felon_aliases = ["criminal", "offender","felony","felon","Felony"]

        for user_id in os.listdir(user_folder):
            user_character_folder = os.path.join(user_folder, user_id)
            character_files = [file for file in os.listdir(user_character_folder) if file.endswith("_data.json")]

            for character_file in character_files:
                with open(os.path.join(user_character_folder, character_file), 'r') as json_file:
                    character_data = json.load(json_file)

                if character_data.get('Name') == character_name:
                    character_info = (
                        f"**Name:** {character_data['Name']}\n"
                        f"**Sex:** {character_data['Sex']}\n"
                        f"**Ethnicity:** {character_data['Ethnicity']}\n"
                        f"**Date of Birth:** {character_data['Date of Birth']}\n"
                        f"**License Status:** {character_data['License Status']}"
                    )
                    found_character_info.append(character_info)

        embed = discord.Embed(
            title=f"Character Information for Civilian: {character_name} :blond_haired_person:",
            color= discord.Colour.yellow()
        )

        if found_character_info:
            character_info_str = '\n\n---\n\n'.join(found_character_info)
            embed.description = character_info_str

        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

        for user_id in os.listdir(user_folder):
            open_warrants_folder = f'mini-cad/{server_id}/warrant-status/{user_id}/open-warrants'
            open_warrant_files = [file for file in os.listdir(open_warrants_folder) if file.endswith(".json")]

            for warrant_file in open_warrant_files:
                with open(os.path.join(open_warrants_folder, warrant_file), 'r') as json_file:
                    warrant_data = json.load(json_file)

                if warrant_data.get('Character Name') == character_name:
                    for alias in felon_aliases:
                        if alias in warrant_data['Reason'].lower():
                            is_felon = True
                            break

        if is_felon:
            felon_embed = discord.Embed(
                title=f"Felon Status for Civilian: {character_name} :rotating_light:",
                color= discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            felon_embed.add_field(name="Felon Status", value="This civilian is marked as a felon.", inline=False)
            await interaction.followup.send(embed=felon_embed)

    except Exception as e:
        print(f"Error during search_name: {str(e)}")

@client.tree.command(name='list_open_warrants', description='List all open warrants')
async def list_open_warrants(interaction: discord.Interaction):
    try:
        server_id = str(interaction.guild.id)
        warrant_status_folder = f'mini-cad/{server_id}/warrant-status'

        warrant_info_list = []

        for user_id in os.listdir(warrant_status_folder):
            open_warrants_folder = os.path.join(warrant_status_folder, user_id, 'open-warrants')

            if not os.path.exists(open_warrants_folder):
                continue

            open_warrant_files = [os.path.join(open_warrants_folder, file) for file in os.listdir(open_warrants_folder) if file.endswith(".json")]

            for warrant_file in open_warrant_files:
                with open(warrant_file, 'r') as json_file:
                    warrant_data = json.load(json_file)

                warrant_info = (
                    f"**Case ID:** {warrant_data['Case ID']}\n"
                    f"**Character Name:** {warrant_data['Character Name']}\n"
                    f"**Issuing Department:** {warrant_data['Issuing Department']}\n"
                    f"**Reason:** {warrant_data['Reason']}\n"
                    f"**Date:** {warrant_data['Date']}"
                )
                warrant_info_list.append(warrant_info)

        if not warrant_info_list:
            embed = discord.Embed(
                title="No Open Warrants :x:",
                description="There are no open warrants at the moment.",
                color= discord.Colour.yellow()
            )
            await interaction.response.send_message(embed=embed)
            return

        warrant_info_str = '\n\n---\n\n'.join(warrant_info_list)

        embed = discord.Embed(
            title="Open Warrants",
            description=warrant_info_str,
            color=0x3498db
        )

        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during list_open_warrants: {str(e)}")

@client.tree.command(name='list_closed_warrants', description='List all closed warrants')
async def list_closed_warrants(interaction: discord.Interaction):
    try:
        server_id = str(interaction.guild.id)
        warrant_status_folder = f'mini-cad/{server_id}/warrant-status'

        warrant_info_list = []

        for user_id in os.listdir(warrant_status_folder):
            closed_warrants_folder = os.path.join(warrant_status_folder, user_id, 'closed-warrants')

            if not os.path.exists(closed_warrants_folder):
                continue

            closed_warrant_files = [os.path.join(closed_warrants_folder, file) for file in os.listdir(closed_warrants_folder) if file.endswith(".json")]

            for warrant_file in closed_warrant_files:
                with open(warrant_file, 'r') as json_file:
                    warrant_data = json.load(json_file)

                warrant_info = (
                    f"**Case ID:** {warrant_data['Case ID']}\n"
                    f"**Character Name:** {warrant_data['Character Name']}\n"
                    f"**Issuing Department:** {warrant_data['Issuing Department']}\n"
                    f"**Reason:** {warrant_data['Reason']}\n"
                    f"**Date:** {warrant_data['Date']}"
                )
                warrant_info_list.append(warrant_info)

        if not warrant_info_list:
            embed = discord.Embed(
                title="No Closed Warrants :x:",
                description="There are no closed warrants at the moment.",
                color= discord.Colour.yellow()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        warrant_info_str = '\n\n---\n\n'.join(warrant_info_list)

        embed = discord.Embed(
            title="Closed Warrants",
            description=warrant_info_str,
            color= discord.Colour.yellow()
        )

        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during list_closed_warrants: {str(e)}")


@client.tree.command(name='ncic', description='Perform an NCIC check for a character')
async def ncic_check(interaction: discord.Interaction, character_name: str):
    try:
        server_id = str(interaction.guild.id)
        warrant_status_folder = f'mini-cad/{server_id}/warrant-status'

        open_warrant_info_list = []
        closed_warrant_info_list = []

        for user_id in os.listdir(warrant_status_folder):
            open_warrants_folder = os.path.join(warrant_status_folder, user_id, 'open-warrants')
            closed_warrants_folder = os.path.join(warrant_status_folder, user_id, 'closed-warrants')

            if os.path.exists(open_warrants_folder):
                open_warrant_files = [os.path.join(open_warrants_folder, file) for file in os.listdir(open_warrants_folder) if file.endswith(".json")]
                for warrant_file in open_warrant_files:
                    with open(warrant_file, 'r') as json_file:
                        warrant_data = json.load(json_file)

                    if warrant_data.get('Character Name') == character_name:
                        open_warrant_info = (
                            f"**Case ID:** {warrant_data['Case ID']}\n"
                            f"**Issuing Department:** {warrant_data['Issuing Department']}\n"
                            f"**Reason:** {warrant_data['Reason']}\n"
                            f"**Date:** {warrant_data['Date']}"
                        )
                        open_warrant_info_list.append(open_warrant_info)

            if os.path.exists(closed_warrants_folder):
                closed_warrant_files = [os.path.join(closed_warrants_folder, file) for file in os.listdir(closed_warrants_folder) if file.endswith(".json")]
                for warrant_file in closed_warrant_files:
                    with open(warrant_file, 'r') as json_file:
                        warrant_data = json.load(json_file)

                    if warrant_data.get('Character Name') == character_name:
                        closed_warrant_info = (
                            f"**Case ID:** {warrant_data['Case ID']}\n"
                            f"**Issuing Department:** {warrant_data['Issuing Department']}\n"
                            f"**Reason:** {warrant_data['Reason']}\n"
                            f"**Date:** {warrant_data['Date']}"
                        )
                        closed_warrant_info_list.append(closed_warrant_info)

        if not open_warrant_info_list and not closed_warrant_info_list:
            embed = discord.Embed(
                title=f"No NCIC Records Found for {character_name} :x:",
                description="There are no open or closed warrants for this character.",
                color= discord.Colour.yellow()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
            return

        open_warrant_info_str = '\n\n---\n\n'.join(open_warrant_info_list)
        closed_warrant_info_str = '\n\n---\n\n'.join(closed_warrant_info_list)

        embed = discord.Embed(
            title=f"NCIC Check for {character_name}",
            color= discord.Colour.red()
        )

        if open_warrant_info_list:
            embed.add_field(name="Open Warrants", value=open_warrant_info_str, inline=False)

        if closed_warrant_info_list:
            embed.add_field(name="Closed Warrants", value=closed_warrant_info_str, inline=False)

        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error during ncic_check: {str(e)}")



def get_registered_owner(vehicle_data):
                            if 'Registered Owner' in vehicle_data:
                                return vehicle_data['Registered Owner']
                            return "Unknown"

@client.tree.command(name='mark_stolen', description='Mark a vehicle as stolen')
async def mark_stolen(
                                interaction: discord.Interaction,
                                vehicle_plate: str
                        ):
                            try:
                                server_id = str(interaction.guild.id)
                                user_id = str(interaction.user.id)
                                character_name = get_active_character_name(server_id, user_id)

                                if character_name is None:
                                    embed = discord.Embed(
                                        title="No Active Character Set",
                                        description="You must set an active character (police officer) before marking a vehicle as stolen.",
                                        color=discord.Colour.red()
                                    )
                                    await interaction.response.send_message(embed=embed)
                                    return

                                user_folder = f'mini-cad/{server_id}/plate-database'

                                for user_id_folder in os.listdir(user_folder):
                                    vehicle_folder = os.path.join(user_folder, user_id_folder)
                                    vehicle_files = [file for file in os.listdir(vehicle_folder) if file.endswith(".json")]

                                    for vehicle_file in vehicle_files:
                                        with open(os.path.join(vehicle_folder, vehicle_file), 'r') as json_file:
                                            vehicle_data = json.load(json_file)

                                        if vehicle_data.get('Plate Number') == vehicle_plate:
                                            if 'Flags' not in vehicle_data:
                                                vehicle_data['Flags'] = []

                                            if 'Stolen' in vehicle_data['Flags']:
                                                embed = discord.Embed(
                                                    title="Vehicle Already Stolen",
                                                    description=f"The vehicle with plate number `{vehicle_plate}` is already marked as stolen.",
                                                    color=discord.Colour.orange()
                                                )
                                                registered_owner = get_registered_owner(vehicle_data)
                                                embed.add_field(name="Registered Owner", value=registered_owner)
                                                await interaction.response.send_message(embed=embed)
                                            else:
                                                vehicle_data['Flags'].append('Stolen')

                                                with open(os.path.join(vehicle_folder, vehicle_file), 'w') as json_file:
                                                    json.dump(vehicle_data, json_file)

                                                registered_owner = get_registered_owner(vehicle_data)

                                                embed = discord.Embed(
                                                    title="Vehicle Marked as Stolen",
                                                    description=f"The vehicle with plate number `{vehicle_plate}` has been marked as stolen by {character_name}.",
                                                    color=discord.Colour.orange()
                                                )
                                                embed.add_field(name="Registered Owner", value=registered_owner)
                                                await interaction.response.send_message(embed=embed)
                                            return

                                embed = discord.Embed(
                                    title="Vehicle Not Found",
                                    description=f"No registered vehicle found with the plate number `{vehicle_plate}` within the server's database.",
                                    color=discord.Colour.red()
                                )
                                await interaction.response.send_message(embed=embed)

                            except Exception as e:
                                print(f"Error during mark_stolen: {str(e)}")



#####################################
#########extra commands##############
#####################################


@client.tree.command(name="ping",description="Sends The Bot's Latency")
async def ping(interaction:discord.Interaction):
  embed = discord.Embed(title="Pong! :ping_pong:", description=f"CopBot's Ping is: {round(client.latency * 1000)}ms", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)
  guild = interaction.guild


@client.tree.command(name="credits",description="shows the team that made CopBot a thing")
async def credits(interaction:discord.Interaction):
  embed = discord.Embed(title="CopBot Credits :trophy:", color = discord.Colour.yellow())
  embed.description=f"""
  Lead Developers - 420Stax, ButterBoy
  Developers - zackp98
  Support Team - tasty_mattasom, urfavdev
  """
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/903519378438496296/1156172692135878696/copbot_site_logo.png?ex=6514013a&is=6512afba&hm=34fb415dd2681ae06ce107cf43dd9f44671c14feae677001544b79d1bf600c30&")
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="fuel",description="Fuels Your Vehicle")
async def fuel(interaction:discord.Interaction):
  embed = discord.Embed(title="Fuel Vehicle",description="Fueling Your Car! :fuelpump: please wait 15 seconds for your tank to be full...", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)
  time.sleep(5)
  ten_embed = discord.Embed(title="Fuel Vehicle :stopwatch:",description="10 Seconds Remaining... ", color = discord.Colour.orange())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed = ten_embed)
  time.sleep(7)
  three_embed = discord.Embed(title="Fuel Vehicle :stopwatch:",description="3 Seconds Remaining... ", color = discord.Colour.orange())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed = three_embed)
  time.sleep(2)
  two_embed = discord.Embed(title="Fuel Vehicle :stopwatch:",description="2 Seconds Remaining... ", color = discord.Colour.orange())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed = two_embed)
  time.sleep(2)
  one_embed = discord.Embed(title="Fuel Vehicle :stopwatch:",description="1 Second Remaining... ", color = discord.Colour.orange())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed = one_embed)
  time.sleep(2)
  finished_embed = discord.Embed(title="Vehicle Is Full! :fuelpump:",description="Your Vehicle's Tank Is Full!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed = finished_embed)


@client.tree.command(name="bcamon",description="Turns On Your Axon BodyCamera")
async def bcamon(interaction:discord.Interaction):
  embed = discord.Embed(title="Body Camera Activated :red_circle:",description="Your Axon BodyCam Is Now Recording! ", color = discord.Colour.red())
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/903519378438496296/1156168098789986374/axon2.png?ex=6513fcf3&is=6512ab73&hm=8344d178f52dced04a02e7b8041e2738044e9a97ecdd285388619ce1f40ee092&")
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)

@client.tree.command(name="bcamoff",description="Turns Off Your Axon BodyCamera")
async def bcamoff(interaction:discord.Interaction):
  embed = discord.Embed(title="Body Camera Deactivated :yellow_circle:",description="Your Axon BodyCam Is Now Off! ", color = discord.Colour.yellow())
  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/903519378438496296/1156168098789986374/axon2.png?ex=6513fcf3&is=6512ab73&hm=8344d178f52dced04a02e7b8041e2738044e9a97ecdd285388619ce1f40ee092&")
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="dcamon",description="Turns On Your Dash Camera")
async def dcamon(interaction:discord.Interaction):
  embed = discord.Embed(title="Dash Camera Activated :red_circle:",description="Your Dash Camera Is Now Recording!", color = discord.Color.red())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="dcamoff",description="Turns Off Your Dash Camera")
async def dcamoff(interaction:discord.Interaction):
  embed = discord.Embed(title="Dash Camera Deactivated :yellow_circle:",description="Your Dash Camera Is Now Off!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="radar",description="Runs Radar At A Selected Location")
async def radar(interaction:discord.Interaction, location: str):
  embed = discord.Embed(title="Running Radar :octagonal_sign:",description=f"{interaction.user.mention} Is Currently Running Radar At: {location}", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="cctv",description="Get information about a selected cctv camera")
async def cctv(interaction:discord.Interaction, location: str):
  embed = discord.Embed(title="CCTV :video_camera:",description=f"{interaction.user.mention} Is currently viewing the CCTV footage at {location}. **What do they see?**", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="call911",description="Calls 911 With A Custom Message And Location")
async def call911(interaction:discord.Interaction, caller: str, service: str, reason: str, location: str):
   embed = discord.Embed(title="Incoming 911 Call! :rotating_light: ", color = discord.Colour.red())
   embed.description=f"""
  Caller Name: {caller}
  Location: {location}
  Service Needed: {service}
  Reason: {reason}
  """
   embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
   await interaction.response.send_message(embed=embed)



@client.tree.command(name="call311",description="Calls 311 With A Custom Message And Location")
async def call311(interaction:discord.Interaction, caller: str, service: str, reason: str, location: str):
  embed = discord.Embed(title="Incoming 311 Call! :rotating_light: ", color = discord.Colour.yellow())
  embed.description=f"""
  Caller Name: {caller}
  Location: {location}
  Service Needed: {service}
  Reason: {reason}
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="engstart",description="Starts Your Vehicle's Engine")
async def engstart(interaction:discord.Interaction):
  embed = discord.Embed(title="Engine Started! :blue_car: ",description="Your Car Engine Was Started!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="engoff",description="Turns Off Your Vehicle's Engine")
async def engoff(interaction:discord.Interaction):
  embed = discord.Embed(title="Engine Turned Off! :blue_car: ",description="Your Car Engine Was Turned Off!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="cuff",description="Cuffs The Mentioned User With A Custom Reason")
async def cuff(interaction:discord.Interaction, reason: str, member: discord.User):
  embed = discord.Embed(title=f"User Cuffed! :chains:", description=f"{interaction.user.mention} Cuffed {member.mention} for: {reason}", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)



@client.tree.command(name="uncuff",description="Uncuffs The Mentioned User")
async def uncuff(interaction:discord.Interaction, member: discord.User):
  embed = discord.Embed(title=f"User Uncuffed! :chains:", description=f"{interaction.user.mention} Uncuffed {member.mention}", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="jail",description="Jails The Mentioned User For A Custom Amount Of Time")
async def jail(interaction:discord.Interaction, reason: str, member: discord.User, time: str):
  embed = discord.Embed(title="Jailed User :chains:", description=f"{interaction.user.mention} Jailed {member.mention} for: {reason}. they will be released in {time} seconds...", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)
  time.sleep({time})
  embed_two = discord.Embed(title="Jailed User :stopwatch:",description=f"{member.mention} will be released shortly...", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed=embed_two)
  time.sleep({time})
  embed_three = discord.Embed(title="User Released!",description=f"{member.mention} has been released!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.edit_original_response(embed=embed_three)


@client.tree.command(name="me",description="Sends A User's Action Within An Embedded Message")
async def me(interaction:discord.Interaction, action: str):
  embed = discord.Embed(title="User Action :speaking_head:", description=f"{interaction.user.mention} {action}", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="give",description="Gives A Selected Item To The Mentioned User")
async def give(interaction:discord.Interaction, item: str, member: discord.User):
  embed = discord.Embed(title="User Give :leftwards_hand:", description=f"{interaction.user.mention} Gave {member.mention} {item}", color = discord.Color.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="eat",description="Takes A Bite Of Your Snack")
async def eat(interaction:discord.Interaction):
  embed = discord.Embed(title="User Eat :canned_food:", description=f"{interaction.user.mention} has taken a bite of there snack!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.tree.command(name="drink",description="Takes A Sip Of Your Drink")
async def drink(interaction:discord.Interaction):
  embed = discord.Embed(title="User Drink :beer:", description=f"{interaction.user.mention} has taken a sip of there drink!", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


#####################################
#########moderation commands#########
#####################################


@client.tree.command(name="initialize_warnings", description="Initialize Warnings JSON File")
@commands.has_permissions(administrator=True)
async def initialize_warnings(interaction:discord.Interaction):
    try:
        server_json_file = ensure_server_directory(ctx.guild.id)

        if os.path.exists(server_json_file):
            embed = discord.Embed(description="Warnings JSON file already exists.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
        else:
            with open(server_json_file, 'w') as f:
                json.dump({'users': []}, f)
            embed = discord.Embed(description="Warnings JSON file initialized.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(description=f"An error occurred: {str(e)}", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="warn", description="Warn A Selected User For A Custom Reason")
@commands.has_permissions(manage_roles=True, kick_members=True)
async def warn(interaction:discord.Interaction, member: discord.User, reason: str):
    try:
        if not member:
            raise commands.MissingRequiredArgument("Member is missing.")

        if not reason:
            raise commands.MissingRequiredArgument("Reason is missing.")

        reason = ' '.join(reason.split())

        server_json_file = ensure_server_directory(interaction.guild.id)

        try:
            with open(server_json_file, 'r') as f:
                server_warnings = json.load(f)
        except FileNotFoundError:
            server_warnings = {'users': []}

        for current_user in server_warnings['users']:
            if current_user['id'] == member.id:
                current_user['reasons'].append(reason)
                break
        else:
            server_warnings['users'].append({
                'id': member.id,
                'name': str(member),
                'reasons': [reason]
            })

        with open(server_json_file, 'w+') as f:
            json.dump(server_warnings, f)

        embed = discord.Embed(description=f"{interaction.user.mention} Has Warned {member.mention} For {reason}", color = discord.Colour.yellow())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

    except commands.MissingRequiredArgument as error:
        embed = discord.Embed(description=f"**ERROR**:exclamation: : {error}", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(description=f"An error occurred :exclamation: : {str(e)}", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="warnings", description="Show Past Warnings Of The Mentioned User")
async def warnings(interaction:discord.Interaction, member: discord.User):
    try:
        server_json_file = ensure_server_directory(interaction.guild.id)

        try:
            with open(server_json_file, 'r') as f:
                server_warnings = json.load(f)
        except FileNotFoundError:
            server_warnings = {'users': []}

        for current_user in server_warnings['users']:
            if current_user['id'] == member.id:
                embed = discord.Embed(title=f"{member.mention} WARNINGS :hammer:", color = discord.Colour.yellow())
                for i, warning in enumerate(current_user['reasons'], 1):
                    embed.add_field(name=f"{i}.", value=warning, inline=False, color = discord.Colour.yellow())
                    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                await interaction.response.send_message(embed=embed)
                break
        else:
            embed = discord.Embed(title="User Warnings :hammer:", description=f"{member.mention} has no warnings!", color = discord.Colour.yellow())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(description=f"An error occurred :exclamation: : {str(e)}", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="remove_warning", description="Remove a Specific Warning from A User's Warnings List")
@commands.has_permissions(manage_roles=True, kick_members=True)
async def remove_warning(interaction:discord.Interaction, member: discord.User, warning_number: int):
    try:
        server_json_file = ensure_server_directory(interaction.guild.id)

        try:
            with open(server_json_file, 'r') as f:
                server_warnings = json.load(f)
        except FileNotFoundError:
            server_warnings = {'users': []}

        for current_user in server_warnings['users']:
            if current_user['id'] == member.id:
                if 1 <= warning_number <= len(current_user['reasons']):
                    removed_warning = current_user['reasons'].pop(warning_number - 1)
                    with open(server_json_file, 'w+') as f:
                        json.dump(server_warnings, f)
                    embed = discord.Embed(description=f"Removed warning {warning_number}: {removed_warning} from {member.mention}'s warnings.", color = discord.Colour.yellow())
                    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                    await interaction.response.send_message(embed=embed)
                    return
                else:
                    embed = discord.Embed(description="Invalid warning number. Please provide a valid warning number.", color = discorrd.Colour.red())
                    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
                    await interaction.response.send_message(embed=embed)
                    return
        else:
            embed = discord.Embed(description=f"{member.mention} has no warnings to remove.", color = discord.Colour.red())
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(description=f"An error occurred :exclamation: : {str(e)}", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)



@client.tree.command(name="dmuser", description="Make CopBot dm a user with a custom command")
async def dmuser(interaction: discord.Interaction, member: discord.User, message: str):
    try:
        await member.send(f"{message}, this message is from {interaction.user.mention}!")

        embed = discord.Embed(title="Messaged User :e_mail:", description=f"Message was sent to {member}!", color = discord.Colour.yellow())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(title="**ERROR** :exclamation:",description="Im unable to send a message to that user.", color = discord.Colour.red())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)


@client.tree.command(name="kick",description="Kick A Selected User For A Custom Reason")
@commands.has_permissions(kick_members=True)
async def kick(interaction:discord.Interaction, member: discord.User, reason: str):
    await User.kick(member, reason=reason)
    embed = discord.Embed(title="Kicked User :wave:",description=f"{interaction.user.mention} Has Kicked {member} for {reason}", color = discord.Colour.blue())
    embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
    await interaction.response.send_message(embed=embed)


###### Bot's Server Commands #########

role_id = 916782028672872568

@client.tree.command()
async def listservers(interaction):
    user = interaction.user
    if any(role.id == role_id for role in user.roles):
        server_list = "\n".join(f"{i+1}. {guild.name} | {guild.id}" for i, guild in enumerate(client.guilds))
        embed = discord.Embed(title="Server List :bookmark_tabs:", description=f"List of Servers:\n{server_list}", color=discord.Colour.yellow())
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="**ERROR** :exclamation:",
            description="You do not have permission to use this command.",
            color=discord.Colour.red()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def getinvite(interaction, server_number: int):
    user = interaction.user
    if any(role.id == role_id for role in user.roles):
        if 1 <= server_number <= len(client.guilds):
            selected_guild = client.guilds[server_number - 1]
            invite = await selected_guild.text_channels[0].create_invite()
            embed = discord.Embed(
                title="Invite :mailbox_with_mail:",
                description=f"Invite link to {selected_guild.name}: {invite.url}",
                color=discord.Colour.yellow()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="**ERROR** :exclamation:",
                description="Invalid server number. Please choose a number within the range.",
                color=discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="**ERROR** :exclamation:",
            description="You do not have permission to use this command.",
            color=discord.Colour.red()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def leaveserver(interaction, server_number: int):
    user = interaction.user
    if any(role.id == role_id for role in user.roles):
        if 1 <= server_number <= len(client.guilds):
            selected_guild = client.guilds[server_number - 1]
            await selected_guild.leave()
            embed = discord.Embed(
                title="Leaving Server :person_running:",
                description=f"Left server: {selected_guild.name}",color = discord.Colour.yellow()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="**ERROR** :exclamation:",
                description="Invalid server number. Please choose a number within the range.",
                color=discord.Colour.red()
            )
            embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
            await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="**ERROR** :exclamation:",
            description="You do not have permission to use this command.",
            color=discord.Colour.red()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def getowner(interaction, server_number: int):
    if 1 <= server_number <= len(client.guilds):
        selected_guild = client.guilds[server_number - 1]
        owner = selected_guild.owner
        member_count = selected_guild.member_count

        owner_mention = owner.mention
        owner_discord_name = f"{owner.name}#{owner.discriminator}"

        embed = discord.Embed(
            title="Server Information :bookmark_tabs:",
            description=f"Server: {selected_guild.name}\nOwner Mention: {owner_mention}\nOwner Discord Name: {owner_discord_name}\nMember Count: {member_count}",
            color=discord.Colour.blue()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="**ERROR** :exclamation:",
            description="Invalid server number. Please choose a number within the range.",
            color=discord.Colour.red()
        )
        embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
        await interaction.response.send_message(embed=embed)


#Normal Bot Commands
@client.tree.command(name="help",description="Sends a list of the bots commands and support server link.")
async def help(interaction:discord.Interaction):
  embed = discord.Embed(title="Help Command :hand_splayed: ", color = discord.Colour.yellow())
  embed.description=f"""
  Please Contact Our Support Server Here ---> (Coming Soon!)      
  Command List ---> (Coming Soon!)
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)

#embed command
@client.tree.command(name="embed",description="Embeds any message the user puts")
async def embed(interaction:discord.Interaction, message: str):
  embed = discord.Embed(title="User Embed :black_nib:",description=f"{message}", color = discord.Colour.yellow())
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)

#on duty/off duty commands
@client.tree.command(name="config",description="Adds any necessary files to your server to ensure the commands work as intended")
@has_permissions(administrator=True)
async def config(interaction:discord.Interaction):
  await interaction.response.send_message("Configuration in progress..." , ephemeral=True)
  guild = interaction.guild
  await guild.create_role(name="On Duty")
  await guild.create_role(name="Off Duty")
  guild = interaction.guild

  id = {
        "users":[]
    }

  with open(f"./multiguild/servers/{str(guild.id)}/ids.json", "w", encoding="utf-8") as file:
        json.dump(id,file,indent=4)
        guild = interaction.guild

  registered = {
        "firearms":[],
        "vehicles":[]
    }

  guild = interaction.guild
  if os.path.exists(f"./multiguild/servers/{str(guild.id)}"):
     users = {
            "users":[]
        }
  for member in guild.members:
            user_data = { str(member.id):{
                "bank":5000,
                "cash":500,
                }
            }
            users["users"].append(user_data)
  with open(f"./multiguild/servers/{str(guild.id)}/{str(guild.id)}.json","+a",encoding="utf-8") as file:
            json.dump(users,file,indent=2)
  await asyncio.sleep(3)
  await interaction.edit_original_response(content="Configuration complete! you may now use the following commands ``/buy (WIP) /collect /wire /balance /transfer /refresheconomy /deposit /withdraw /pay /registered (WIP) /onduty /offduty``")

@client.tree.command(name="onduty",description="Shows You As On Duty")
async def onduty(interaction:discord.Interaction, department: str, aop: str, shift_start: str):
  embed = discord.Embed(title="On Duty :police_officer:", color = discord.Colour.yellow())
  embed.description=f"""
  Unit Name: {interaction.user.mention}
  Unit Department: {department}
  Time Of Clocking In: {shift_start}
  AOP: {aop}
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)
  role = discord.utils.get(interaction.guild.roles, name="On Duty")
  await interaction.user.add_roles(role)
  role = discord.utils.get(interaction.guild.roles, name="Off Duty")
  await interaction.user.remove_roles(role)


@client.tree.command(name="offduty",description="Shows You As Off Duty")
async def offduty(interaction:discord.Interaction, department: str, aop: str, shift_start: str, shift_end: str, shift_description: str):
  embed = discord.Embed(title="Off Duty :police_officer:", color = discord.Colour.yellow())
  embed.description=f"""
  Unit Name: {interaction.user.mention}
  Unit Department: {department}
  Time Of Clocking In: {shift_start}
  Time Of Clocking Out: {shift_end}
  AOP: {aop}
  Shift Description: {shift_description}
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)
  role = discord.utils.get(interaction.guild.roles, name="Off Duty")
  await interaction.user.add_roles(role)
  role = discord.utils.get(interaction.guild.roles, name="On Duty")
  await interaction.user.remove_roles(role)


#panic button command
@client.tree.command(name="panic",description="Triggers your panic button")
async def panic(interaction:discord.Interaction, department: str, location: str, reason: str):
  embed = discord.Embed(title="Panic Triggered :rotating_light:", color = discord.Colour.yellow())
  embed.description=f"""
  Unit Name: {interaction.user.mention}
  Unit Department: {department}
  Location: {location}
  Reason: {reason}
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)

#social command
@client.tree.command(name="post",description="Post something on social media!")
async def post(interaction:discord.Interaction, platform: str, message: str):
  embed = discord.Embed(title=f"New {platform} post! :mobile_phone:", color = discord.Colour.yellow())
  embed.description=f"""
  {interaction.user.mention} posted:
  {message}
  """
  embed.set_footer(text='CopBot',icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=f941d50dfa5b2edef77d274e64894ae8e51bd3aad787792906e257d686aff533&")
  await interaction.response.send_message(embed=embed)


@client.event
async def on_guild_join(guild):
    invites = await guild.invites()
    if invites:
        member = invites[0].inviter
        embed = discord.Embed(title="Thanks for inviting me!", color=discord.Colour.yellow())
        embed.description = f"""
Thanks for inviting me to {guild.name}!
Please run the /config command in your server to unlock all of CopBot's commands!
If you need assistance, please join the server below!
Support Server: (Coming Soon!)
"""
        embed.set_footer(text='CopBot', icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=d787792906e2f941d50dfa5b2edef77d274e64894ae8e51bd3aa57d686aff533&")
        await member.send(embed=embed)

@client.event
async def on_guild_join(guild):
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
        inviter = entry.user
        embed = discord.Embed(title="Thanks for inviting me!", color=discord.Colour.yellow())
        embed.description = f"""
        Thanks for inviting me to **{guild.name}**!
        Please run the /config command in your server to unlock all of CopBot's commands!
        If you need assistance, please join the support server below!
        Support Server: [Click Here](https://discord.gg/JqvwH7QhaZ)
        """
        embed.set_footer(text='CopBot', icon_url="https://cdn.discordapp.com/attachments/1152316262676963489/1156869427279691776/copbot_site_logo.png?ex=65168a1d&is=6515389d&hm=d787792906e2f941d50dfa5b2edef77")
        await inviter.send(embed=embed)









######################################
##########runs the bot################
######################################
client.run(bot_token)

