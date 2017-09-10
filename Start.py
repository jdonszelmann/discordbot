
import discord
import asyncio
import logging
import sys,os
from discord.ext import commands
import re
import math
import threading

# to set up a bot:
# make an application on 
# https://discordapp.com/developers/applications
# activate the "bot user" setting.
# copy the CLIENTID on your bot's page.
# to get back to this page, use this link:
# https://discordapp.com/developers/applications/me/<CLIENTID HERE>

# in the section about the BOT USER get your bot's token
# insert it below to make the bot work.

# to set up permissions and servers for you bot, go to the following link
# https://discordapp.com/oauth2/authorize?client_id=<CLIENTID HERE>&scope=bot&permissions=0

# this bot is made to work on multiple servers AT ONCE.

#===============================================================================
# APP BOT USER TOKEN: (str)

token = "MzU1NzE2MzA2NjcyMTU2Njcy.DJQ4bQ.VQidstm_WtcbPKHphP7ztwEnuaM"

#===============================================================================
# APP BOT CLIENT ID: (str)

# clientID = "355716306672156672"

# leave the line above commented for it is not used in the program. 
# it is however usefull for you if you decide to change permissions on your bot

#===============================================================================
# YOUR USERNAME TO DISPLAY WHEN YOU MESSGE SERVERS FROM THE COMMANDLINE/TERMINAL:

username = "jonay2000"

#===============================================================================
# THE PREFIX TO SIGNIFY A MESSAGE IS A BOT COMMAND
command_prefix = "."

#make sure to use a prefix that is not used by any other bot that is on the server.

#===============================================================================

#DEFAULT NAME IN ALL SERVERS
default_nickname = "WorkBot"

#===============================================================================


class connect:
	def __init__(self):
		# logging.basicConfig(level=logging.INFO)

		self.client = commands.Bot(command_prefix=command_prefix, description='cross-server discord bot')

	def connect(self):
		self.client.run(token)

#preinit to make classes work
Bot = connect()
client = Bot.client

class Servers:
	def __init__(self):
		self.servers = {}

	# finds channel names in servers and logs them in a dict, used to find the "bot" channel or the "general" channel
	def add(self,server):
		IDs = {"bot area":"","general":"","announcements":""}
		for channel in server.channels:
			if "bot" in str(channel):
				IDs["bot area"] = str(channel.id)
			if "general" in str(channel):
				IDs["general"] = str(channel.id)
			if "announcement" in str(channel):
				IDs["announcements"] = str(channel.id)
			if any(ext in str(channel) for ext in [str(i).lower() for i in client.servers]):
				IDs["crossserver"] = str(channel.id)

		self.servers[str(server.id)] = IDs

	# finds other channels in other servers which have the same name as this server.
	# used for cross-server communication using .cross
	def get_all_crossover(self,server):
		matches = []
		for i in client.servers:
			for j in i.channels:
				if str(j).lower() == str(server).lower():
					yield j
					 
	def get_channel(self,ctype,server):
		return discord.Object(id=self.servers[str(server.id)][ctype])

	def get_all(self,ctype):
		for key,server in self.servers.items():
			yield discord.Object(id=server[ctype])

	def get_all_servers(self):
		for i in self.servers.keys():
			yield discord.Server(id=i)

	def get_channel_by_ctx(self,ctx):
		return discord.Object(id = ctx.message.channel.id)

@client.event
async def on_ready():
	for server in client.servers:
		servers.add(server)
		await client.change_nickname(server.me,default_nickname)
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	print(client)
	for i in servers.get_all("bot area"):
		await client.send_message(i,'ONLINE')

@client.command(pass_context=True)
async def test(ctx):
	'''
	test bot status
	'''
	await client.send_message(servers.get_channel("bot area",ctx.message.server), 'Hey, im alive')

@client.command(pass_context=True)
async def channellist(ctx):
	channels = []
	for server in client.servers:
		if ctx.message.server.id == server.id:
			for channel in server.channels:
				channels.append(str(channel))
	await client.send_message(servers.get_channel_by_ctx(ctx), "\n".join(channels))

@client.command(pass_context=True)
async def serverlist(ctx):
	servers_t = []
	for server in client.servers:
		servers_t.append(str(server))
	await client.send_message(servers.get_channel_by_ctx(ctx), "\n".join(servers_t))

@client.command(pass_context=True)
async def announcement(ctx,*args):
	"""
	use as a prefix on an announcement message, will be broadcasted to all "announcement" channels this bot can find on any server
	it is connected to
	"""
	for j,i in zip(client.servers,servers.get_all("announcements")):
		await client.change_nickname(j.me,"{}@{}".format(str(ctx.message.author),str(ctx.message.server)))
		await client.send_message(i,  ' '.join(args))
		await client.change_nickname(j.me,client.user.name)


@client.command(pass_context=True)
async def cross(ctx,*args):
	"""
		use this prefix on a message to broadcast your message to all the servers this bot is connected to, and which have a channel
		named the same as the server you are broadcasting from.

		example:
		servername = foo
		servers_bot_is_connected_to = bar,baz

		.cross hi
		
		for i in servers_bot_is_connected_to:
			if any channelname == servername:
				send hi to this channel

	"""
	others = []
	for i in client.servers:
		await client.change_nickname(i.me, "{}@{}".format(str(ctx.message.author),str(ctx.message.server)))
	for i in servers.get_all_crossover(ctx.message.server):
		await client.send_message(i,  ' '.join(args))
		others.append(i)
	for i in client.servers:
		await client.change_nickname(i.me,client.user.name)

	others_t = []
	for i in client.servers:
		for j in i.channels:
			for k in others:
				if j.id == k.id:
					others_t.append("{}@{}".format(str(j),str(i)))
	if len(others_t) > 0:
		await client.send_message(servers.get_channel_by_ctx(ctx), "your message has been broadcast to {}".format(", ".join(others_t)))
	else:
		await client.send_message(servers.get_channel_by_ctx(ctx), "your message could not been broadcasted for there are no other servers with name {} ".format(str(ctx.message.server)))

@client.command(pass_context=True)
async def reconnect(ctx):
	'''
	reconnects the bot
	'''
	perm = False
	for i in ctx.message.author.roles:
		if "mod" in str(i.name):
			perm=True
		if "admin" in str(i.name):
			perm=True

	if username in str(ctx.message.author) or perm:
		await client.send_message(servers.get_channel("bot area",ctx.message.server), 'be right back!')
		# os.system('python3 Start.py')
		os.system('python Start.py')
		sys.exit()
	else:
		await client.send_message(servers.get_channel_by_ctx(ctx), 'PermissionError - you do not have permissions to deactivate this bot')


@client.command(pass_context=True)
async def disconnect(ctx):
	'''
	disconnects the bot
	'''

	perm = False
	for i in ctx.message.author.roles:
		if "mod" in str(i.name):
			perm=True
		if "admin" in str(i.name):
			perm=True

	if username in str(ctx.message.author) or perm:
		await client.send_message(servers.get_channel("bot area",ctx.message.server), 'bye')
		await client.close()
		await sys.exit()
	else:
		await client.send_message(servers.get_channel_by_ctx(ctx), 'PermissionError - you do not have permissions to deactivate this bot')

# comment this if you want to see errors section
@client.event
async def on_command_error(error, ctx):
	print("An error occured during the handling of the previous command")
	print("loggin error to /tmp/errors.txt")
	with open(path + "/tmp/errors.txt",a) as f:
		f.write(error)
		f.close()
	await client.send_message(servers.get_channel("bot area",ctx.message.server), 'an error   occured (ArgumentError)')
#until here

@client.event
async def on_message(message):
	print(message.author, "@",message.server, '    ', message.content)
	await client.process_commands(message)

async def my_background_task():
	await client.wait_until_ready()
	await asyncio.sleep(5)
	while not client.is_closed:

		with open(path+"/tmp/inputs.txt") as f:
			a = f.readlines()
			f.close()
		open(path+"/tmp/inputs.txt", 'w').close()
	
		for item in a:
			if item == ".disconnect":
				for i in servers.get_all("bot area"):
					await client.send_message(i, 'bye')
				await client.close()
				await sys.exit()
			elif item == ".reconnect":
				for i in servers.get_all("bot area"):
					await client.send_message(i, 'be right back!')
				# os.system('python3 Start.py')
				os.system('python Start.py')
				sys.exit()
			elif item != "":
				for i,j in zip(servers.get_all("general"),client.servers):
					await client.change_nickname(j.me,username)
					await client.send_message(i, item)
					await client.change_nickname(j.me,client.user.name)
			
		await asyncio.sleep(0.1)

path = os.path.dirname(os.path.realpath(__file__))
servers = Servers()
addnewlines = lambda x: x + '\n'

client.loop.create_task(my_background_task())

a = threading.Thread(target=Bot.connect)
a.daemon = True
a.start()

while 1:
	inp = input()
	with open(path + "/tmp/inputs.txt","a") as f:
		f.write(inp)
		f.close()