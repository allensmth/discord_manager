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

# 创建机器人实例
intents = discord.Intents.default()
intents.members = True  # 启用成员权限
intents.message_content = True  # 启用消息内容权限

# 创建机器人实例
bot = commands.Bot(
    command_prefix='!', 
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Bot已登录为 {bot.user.name}')
    
    # 获取第一个服务器
    guild = bot.guilds[0]
    
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

    # 完成后关闭机器人
    await bot.close()

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