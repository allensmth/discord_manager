import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp
import asyncio

# 加载环境变量
load_dotenv()

# 根据环境变量配置代理
if os.getenv('PROXY_ENABLED', 'false').lower() == 'true':
    # 设置代理环境变量
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

# 创建机器人实例，设置帮助命令
class CustomBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()  # 同步斜杠命令

    async def on_ready(self):
        print(f'Bot已登录为 {self.user.name}')
        
        # 获取第一个服务器
        guild = self.guilds[0]
        
        # 显示服务器信息
        print(f'\n服务器: {guild.name} (ID: {guild.id})\n')
        print('成员信息:')
        print('-' * 50)
        print(f'{"用户名":<20} {"昵称":<20} {"身份组":<30} {"备注":<20}')
        print('-' * 50)
        
        # 遍历服务器中的所有成员
        for member in guild.members:
            # 获取成员的身份组（去除@everyone）
            roles = [role.name for role in member.roles if role.name != '@everyone']
            roles_str = ', '.join(roles) if roles else '无'
            
            # 获取成员的昵称（如果没有则显示用户名）
            nickname = member.nick if member.nick else '无'
            
            # 打印成员信息
            print(f'{member.name:<20} {nickname:<20} {roles_str:<30} {member.nick or "无":<20}')

# 创建机器人实例
intents = discord.Intents.default()
intents.members = True  # 启用成员权限
intents.message_content = True  # 启用消息内容权限

bot = CustomBot(
    command_prefix='!', 
    intents=intents,
    help_command=commands.DefaultHelpCommand(
        no_category='基础命令',
        command_attrs={
            'help': '显示此帮助消息',
            'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user)
        }
    )
)

@bot.command(name='weekly', help='将用户添加到weekly组。用法：!weekly @用户名')
async def weekly(ctx, member: discord.Member):
    """
    将指定用户添加到weekly组
    
    参数：
    member: 要添加到weekly组的用户（使用@提及）
    """
    # 检查机器人是否有管理身份组权限
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("错误：机器人没有管理身份组的权限！请联系服务器管理员授予权限。")
        return

    # 检查命令执行者是否有管理身份组权限
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("错误：您没有管理身份组的权限！此命令仅限管理员使用。")
        return

    try:
        # 检查weekly身份组是否存在
        weekly_role = discord.utils.get(ctx.guild.roles, name='weekly')
        if not weekly_role:
            weekly_role = await ctx.guild.create_role(
                name='weekly',
                color=discord.Color.blue(),
                reason="Created for weekly member tracking"
            )
            print(f'Created new weekly role: {weekly_role.name}')
        
        # 添加身份组到成员
        await member.add_roles(weekly_role)
        await ctx.send(f'✅ 已将 {member.mention} 添加到 weekly 组')
        
    except discord.Forbidden:
        await ctx.send("错误：机器人权限不足，无法管理身份组！")
    except discord.HTTPException:
        await ctx.send("错误：添加身份组时发生网络错误，请稍后重试。")
    except Exception as e:
        await ctx.send(f"发生未知错误：{str(e)}")

@weekly.error
async def weekly_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("使用方法：!weekly @用户名")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("找不到指定的用户！请确保用户名正确。")
    else:
        await ctx.send(f"执行命令时发生错误：{str(error)}")

@bot.command(name='info')
async def get_member_info(ctx, username: str):
    """获取指定用户的备注信息"""
    # 检查是否在服务器中使用
    if ctx.guild is None:
        await ctx.send("此命令只能在服务器中使用")
        return
    
    # 在服务器中查找匹配的用户
    member = discord.utils.get(ctx.guild.members, name=username)
    
    if member:
        note = member.nick if member.nick else "无备注"
        await ctx.send(f"用户 {username} 的备注: {note}")
    else:
        await ctx.send(f"未找到用户 {username}")

@bot.command(name='ping', help='测试机器人是否在线')
async def ping(ctx):
    """测试机器人的响应时间"""
    await ctx.send(f'🏓 Pong! 延迟: {round(bot.latency * 1000)}ms')

# 根据环境变量配置代理
if os.getenv('PROXY_ENABLED', 'false').lower() == 'true':
    # 创建带代理的HTTP客户端
    class ProxyHTTPClient(discord.http.HTTPClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.proxy = 'http://127.0.0.1:7897'
        
        async def request(self, route, *args, **kwargs):
            kwargs['proxy'] = self.proxy
            return await super().request(route, *args, **kwargs)

    # 替换默认的HTTP客户端
    bot.http = ProxyHTTPClient(bot.loop)

# 运行机器人
bot.run(os.getenv('DISCORD_TOKEN'))