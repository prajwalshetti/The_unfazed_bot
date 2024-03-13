from discord.ext import commands
import discord

intents = discord.Intents.all()
thank_points = {}
reaction_counts = {}
final_reactions = {}
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="with thanks"))

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        welcome_message = f"Welcome to the server, {member.mention}! Feel free to introduce yourself."
        await channel.send(welcome_message)

@bot.event
async def on_message(message):
    if not message.author.bot:
        reaction_counts[message.jump_url] = sum(reaction.count for reaction in message.reactions)
    await bot.process_commands(message)
    print(reaction_counts)

@bot.command()
async def thanks(ctx, member: discord.Member):
    await ctx.send(f"{member.mention} has been thanked!")
    print(f"{member.name} thanked by {ctx.author.name}")
    
    if member.id not in thank_points:
        thank_points[member.id] = 1
    else:
        thank_points[member.id] += 1

@bot.command()
async def thank_leaderboard(ctx):
    embed = discord.Embed(
        title="Thank Leaderboard",
        color=discord.Color.blue()
    )
    sorted_points = sorted(thank_points.items(), key=lambda x: x[1], reverse=True)
    
    for idx, (member_id, points) in enumerate(sorted_points, start=1):
        member = bot.get_user(member_id)
        if member:
            embed.add_field(name=f"{idx}. {member.display_name}", value=f"Thanks: {points}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def menu(ctx):
    menu_message = (
        "**Choose a command:**\n"
        "- `!thanks @mention`: Thank a user.\n"
        "- `!thank_leaderboard`: Display the thank leaderboard.\n"
        "- `!kick @mention`: Kick a user from the server.\n"
        "- `!mute @mention duration`: Mute a user for a specified duration (in minutes)."
    )
    await ctx.send(menu_message)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked from the server. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"{member.mention} has been muted. Reason: {reason}")
    
@bot.command()
async def count_reactions(ctx, message_link=None):
    if message_link is None:
        await ctx.send("Please provide the message link.")
        return

    try:
        message_id = int(message_link.split('/')[-1])
        message = await ctx.fetch_message(message_id)
        n_reactions = sum(reaction.count for reaction in message.reactions)

        total_reactions = n_reactions
        reaction_counts[message_id] = total_reactions  # Use message ID as the key

        await ctx.send(f"Total reactions for {message_link}: {total_reactions}")
        print(f"Total reactions for {message_link}: {total_reactions}")
    except discord.errors.NotFound:
        await ctx.send("Message not found. Please make sure the message link is correct.")
    except Exception as e:
        await ctx.send("An error occurred while processing the command.")

bot.run('bot_token_is_hidden')
