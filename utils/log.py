import asyncio
import datetime
import os

import nextcord as discord
import pymongo
from nextcord.ext import commands
from dotenv import load_dotenv

red = 0xF04747
green = 0x43B581
orange = 0xFAA61A
# -> This is the URL of all the embeds' thumbnails.
url = "https://cdn.discordapp.com/attachments/800381129223831592/814762083220324392/tuxpi.com.1613127751-removebg-preview.png"
website = "https://modbot.studio"
load_dotenv("../.env")
client = pymongo.MongoClient(str(os.getenv("URL")))
mydb = client["mydatabase"]
prefixes = mydb["guild"]


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        a = prefixes.find_one({"_id": str(member.guild.id)})
        chid = a["lChannel"]
        channel = self.bot.get_channel(int(chid))
        e = discord.Embed(color=green, timestamp=datetime.datetime.utcnow())
        e.set_author(name=f"modbot", url=url, icon_url=url)
        e.add_field(name=":wave:", value=f"{member.mention} ({member}) just joined.",
                    inline=True)
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_ban(self, gld, usr):
        await asyncio.sleep(0.5)
        found_entry = None
        a = prefixes.find_one({"_id": str(gld.id)})
        chid = a["lChannel"]
        channel = self.bot.get_channel(int(chid))
        async for entry in gld.audit_logs(limit=50, action=discord.AuditLogAction.ban,
                                          after=datetime.datetime.utcnow() - datetime.timedelta(seconds=15),
                                          oldest_first=False):
            if entry.target.id == usr.id:
                found_entry = entry
                break
        if not found_entry:
            return
        e = discord.Embed(color=red, timestamp=datetime.datetime.utcnow())
        e.set_author(name=f"modbot", url=url, icon_url=url)
        e.add_field(name=":lock:", value=f"{usr.mention} ({usr}) was banned.",
                    inline=True)
        e.add_field(name="Target",
                    value=f"<@{str(usr.id)}> ({str(usr)})", inline=True)
        e.add_field(
            name="Moderator", value=f"<@{str(found_entry.user.id)}> ({str(found_entry.user)})", inline=True)
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_unban(self, gld, usr):
        await asyncio.sleep(0.5)
        found_entry = None
        a = prefixes.find_one({"_id": str(gld.id)})
        chid = a["lChannel"]
        channel = self.bot.get_channel(int(chid))
        async for entry in gld.audit_logs(limit=50, action=discord.AuditLogAction.unban,
                                          after=datetime.datetime.utcnow() - datetime.timedelta(seconds=15),
                                          oldest_first=False):
            if entry.target.id == usr.id:
                found_entry = entry
                break
        if not found_entry:
            return
        e = discord.Embed(color=green, timestamp=datetime.datetime.utcnow())
        e.set_author(name=f"modbot", url=url, icon_url=url)
        e.add_field(name=":unlock:",
                    value=f"{usr.mention} ({usr}) was unbanned.\nModerator: {found_entry.user.mention}",
                    inline=True)
        e.add_field(name="Target",
                    value=f"<@{str(usr.id)}> ({str(usr)})", inline=True)
        e.add_field(
            name="Moderator", value=f"<@{str(found_entry.user.id)}> ({str(found_entry.user)})", inline=True)
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, usr):
        a = prefixes.find_one({"_id": str(usr.guild.id)})
        chid = a["lChannel"]
        channel = self.bot.get_channel(int(chid))
        await asyncio.sleep(0.5)
        found_entry = None
        async for entry in usr.guild.audit_logs(limit=50, action=discord.AuditLogAction.kick,
                                                after=datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
                                                oldest_first=False): 
            if entry.target.id == usr.id:
                found_entry = entry
                break
            try:
                e = discord.Embed(
                    color=orange, timestamp=datetime.datetime.utcnow())
                e.set_author(name=f"modbot", url=url, icon_url=url)
                e.add_field(name=":hammer:",
                            value=f"{usr.mention} was kicked.\nModerator: {found_entry.user.mention}",
                            inline=True)
                e.add_field(
                    name="Target", value=f"<@{str(usr.id)}> ({str(usr)})", inline=True)
                e.add_field(name="Moderator", value=f"<@{str(found_entry.user.id)}> ({str(found_entry.user)})",
                            inline=True)
                await channel.send(embed=e)
            except:
                    e = discord.Embed(
                        color=red, timestamp=datetime.datetime.utcnow())
                    e.set_author(name=f"modbot", url=url, icon_url=url)
                    e.add_field(name=":wave:", value=f"{usr.mention} ({usr}) just left.",
                                inline=True)
                    await channel.send(embed=e)
            

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            a = prefixes.find_one({"_id": str(before.guild.id)})
            chid = a["lChannel"]
            channel = self.bot.get_channel(int(chid))
        except:
            pass
        if before.display_name != after.display_name:
            embed = discord.Embed(title="Nickname change",
                            colour=after.colour,
                            timestamp=datetime.datetime.utcnow())
            fields = [("Before", before.display_name, False),
                        ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            try:
                a = prefixes.find_one({"_id": str(before.guild.id)})
                chid = a["lChannel"]
                channel = self.bot.get_channel(int(chid))
            except:
                pass
            await channel.send(embed=embed)

        elif before.roles != after.roles:
            embed = discord.Embed(title=f"Role updates ({before})",
                            colour=after.colour,
                            timestamp=datetime.datetime.utcnow())            
            l3 = [x for x in before.roles if x not in after.roles]
            removed = True
            if l3 == []:
                l3 = [x for x in after.roles if x not in before.roles]
                removed = False
            if removed is True:
                removed = "Removed"
            else:
                removed = "Added"

            value = (r.mention for r in l3)
            x = 0
            for r in l3:
                x = r.mention
            
            embed.add_field(name=f"{removed} role:", value=x, inline=False)
            try:
                a = prefixes.find_one({"_id": str(before.guild.id)})
                chid = a["lChannel"]
                channel = self.bot.get_channel(int(chid))
            except:
                pass
            try:
                a = prefixes.find_one({"_id": str(before.guild.id)})
                chid = a["lChannel"]
                channel = self.bot.get_channel(int(chid))
            except:
                pass
            await channel.send(embed=embed)
        if before.roles == after.roles:
            return
        muted_role = discord.utils.get(after.guild.roles, name="Muted")
        if not muted_role:
            return
        if muted_role in after.roles and not muted_role in before.roles:
            await asyncio.sleep(0.5)  # wait for audit log
            found_entry = None
            async for entry in after.guild.audit_logs(limit=50, action=discord.AuditLogAction.member_role_update,
                                                      after=datetime.datetime.utcnow() - datetime.timedelta(seconds=15),
                                                      oldest_first=False):
                if entry.target.id == after.id and not muted_role in entry.before.roles and muted_role in entry.after.roles:
                    found_entry = entry
                    break
            if not found_entry:
                return
            e = discord.Embed(color=orange, timestamp=datetime.datetime.utcnow())
            e.set_author(name=f"modbot", url=url, icon_url=url)
            e.add_field(name=":lock:", value=f"{after.mention} was muted.",
                        inline=True)
            e.add_field(name="Target", value=f"<@{str(after.id)}> ({str(after)})", inline=True)
            e.add_field(name="Moderator", value=f"<@{str(found_entry.user.id)}> ({str(found_entry.user)})", inline=True)
            try:
                a = prefixes.find_one({"_id": str(before.guild.id)})
                chid = a["lChannel"]
                channel = self.bot.get_channel(int(chid))
            except:
                pass
            await channel.send(embed=e)
        elif muted_role not in after.roles and muted_role in before.roles:
            if after.joined_at > (datetime.datetime.utcnow() - datetime.timedelta(seconds=10)):  # join persist unmute
                return
            await asyncio.sleep(0.5)
            found_entry = None
            async for entry in after.guild.audit_logs(limit=50, action=discord.AuditLogAction.member_role_update,
                                                      after=datetime.datetime.utcnow() - datetime.timedelta(seconds=15),
                                                      oldest_first=False):

                if entry.target.id == after.id and muted_role in entry.before.roles and not muted_role in entry.after.roles:
                    found_entry = entry
                    break
            if not found_entry:
                return
            e = discord.Embed(color=green, timestamp=datetime.datetime.utcnow())
            e.set_author(name=f"modbot", url=url, icon_url=url)
            e.add_field(name=":unlock:", value=f"{after.mention} was unmuted.",
                        inline=True)
            e.add_field(name="Target", value=f"<@{str(after.id)}> ({str(after)})", inline=True)
            e.add_field(name="Moderator", value=f"<@{str(found_entry.user.id)}> ({str(found_entry.user)})",
                        inline=True)
            await channel.send(embed=e)





def setup(bot):
    bot.add_cog(Log(bot))
