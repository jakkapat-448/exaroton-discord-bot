import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
EXAROTON_API_KEY = os.getenv('EXAROTON_API_KEY')

intents = discord.Intents.default()
intents.message_content = True

# สร้างบอทดิสคอร์ด
bot = commands.Bot(command_prefix="!exaroton ", intents=intents)
bot.remove_command('help')

headers = {
    'Authorization': f'Bearer {EXAROTON_API_KEY}',
    'Content-Type': 'application/json'
}

# แปลงสถานะเป็นภาษาไทยพร้อมคำอธิบายเพิ่มเติม
def get_thai_status(status):
    status_map = {
        'ONLINE': '🟢 ออนไลน์ - เซิร์ฟเวอร์กำลังทำงานและพร้อมให้ผู้เล่นเข้าร่วม',
        'OFFLINE': '🔴 ออฟไลน์ - เซิร์ฟเวอร์ไม่ได้ทำงานอยู่ในขณะนี้',
        'STARTING': '🟡 กำลังเริ่ม - เซิร์ฟเวอร์กำลังเริ่มต้นและจะพร้อมในไม่ช้า',
        'STOPPING': '🟠 กำลังหยุด - เซิร์ฟเวอร์กำลังปิดการทำงาน',
        'RESTARTING': '🔵 กำลังรีสตาร์ท - เซิร์ฟเวอร์กำลังเริ่มต้นใหม่',
        'CRASHED': '⚫ เกิดข้อผิดพลาด - เซิร์ฟเวอร์ล้มเหลวเนื่องจากเกิดข้อผิดพลาด',
        'LOADING': '🟣 กำลังโหลด - เซิร์ฟเวอร์กำลังโหลดข้อมูล'
    }
    
    status_map_numbers = {
        0: "OFFLINE",
        1: "ONLINE",
        2: "STARTING",
        3: "STOPPING",
        4: "RESTARTING",
        5: "CRASHED",
        6: "LOADING"
    }
    if isinstance(status, int):
        status = status_map_numbers.get(status, f"{status} - ไม่มีข้อมูลสถานะ")
    
    return status_map.get(status, f"{status} - ไม่มีข้อมูลสถานะ")

# ฟังก์ชันสำหรับการตรวจสอบบทบาท Minecrafter
def has_minecrafter_role():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        
        role = discord.utils.get(ctx.author.roles, name="Minecrafter")
        if role is None:
            await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้ ต้องมีบทบาท 'Minecrafter'")
            return False
        return True
    return commands.check(predicate)

# ฟังก์ชันสำหรับ API exaroton
async def get_servers():
    """ขอข้อมูลเซิร์ฟเวอร์ทั้งหมด"""
    try:
        response = requests.get('https://api.exaroton.com/v1/servers', headers=headers)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการขอข้อมูลเซิร์ฟเวอร์: {e}")
        return None

async def get_server_status(server_id):
    """ขอข้อมูลสถานะเซิร์ฟเวอร์"""
    try:
        response = requests.get(f'https://api.exaroton.com/v1/servers/{server_id}', headers=headers)
        response.raise_for_status()
        return response.json().get('data', {})
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการขอข้อมูลสถานะเซิร์ฟเวอร์: {e}")
        return None

async def start_server(server_id):
    """เริ่มเซิร์ฟเวอร์"""
    try:
        response = requests.post(f'https://api.exaroton.com/v1/servers/{server_id}/start', headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเริ่มเซิร์ฟเวอร์: {e}")
        return False

async def stop_server(server_id):
    """หยุดเซิร์ฟเวอร์"""
    try:
        response = requests.post(f'https://api.exaroton.com/v1/servers/{server_id}/stop', headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการหยุดเซิร์ฟเวอร์: {e}")
        return False

async def restart_server(server_id):
    """รีสตาร์ทเซิร์ฟเวอร์"""
    try:
        response = requests.post(f'https://api.exaroton.com/v1/servers/{server_id}/restart', headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการรีสตาร์ทเซิร์ฟเวอร์: {e}")
        return False

async def get_account_credits():
    """ขอข้อมูลเครดิตที่เหลือของบัญชี"""
    try:
        response = requests.get('https://api.exaroton.com/v1/account', headers=headers)
        response.raise_for_status()
        return response.json().get('data', {}).get('credits')
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการขอข้อมูลเครดิต: {e}")
        return None

async def execute_command(server_id, command):
    """ส่งคำสั่ง console ไปยังเซิร์ฟเวอร์"""
    try:
        response = requests.post(f'https://api.exaroton.com/v1/servers/{server_id}/console', 
                                json={'command': command}, 
                                headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการส่งคำสั่ง: {e}")
        return False

# เมื่อบอทพร้อมทำงาน
@bot.event
async def on_ready():
    print(f'บอทกำลังทำงาน: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="exaroton servers"))

# คำสั่งดูรายการเซิร์ฟเวอร์
@bot.command(name="servers")
@has_minecrafter_role()
async def servers_command(ctx):
    servers = await get_servers()
    if not servers:
        await ctx.send("เกิดข้อผิดพลาดในการขอข้อมูลเซิร์ฟเวอร์")
        return
    
    embed = discord.Embed(title="รายการเซิร์ฟเวอร์ exaroton", color=discord.Color.green())
    
    for server in servers:
        embed.add_field(
            name=server['name'], 
            value=f"สถานะ: {get_thai_status(server['status'])}\nID: {server['id']}", 
            inline=False
        )
    
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# คำสั่งดูสถานะเซิร์ฟเวอร์
@bot.command(name="status")
@has_minecrafter_role()
async def status_command(ctx, server_id: str):
    server = await get_server_status(server_id)
    if not server:
        await ctx.send("เกิดข้อผิดพลาดในการขอข้อมูลสถานะเซิร์ฟเวอร์")
        return
    
    embed = discord.Embed(title=f"สถานะเซิร์ฟเวอร์: {server['name']}", color=discord.Color.green())
    embed.add_field(name="สถานะ", value=get_thai_status(server['status']), inline=False)
    embed.add_field(name="เวอร์ชั่น", value=server['software'].get('version', 'ไม่ทราบ'), inline=True)
    embed.add_field(name="ผู้เล่นออนไลน์", value=f"{server['players'].get('online', 0)}/{server['players'].get('max', 0)}", inline=True)
    embed.add_field(name="ที่อยู่", value=server.get('address', 'ไม่ทราบ'), inline=True)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

# คำสั่งเริ่มเซิร์ฟเวอร์
@bot.command(name="start")
@has_minecrafter_role()
async def start_command(ctx, server_id: str):
    message = await ctx.send("กำลังเริ่มเซิร์ฟเวอร์...")
    success = await start_server(server_id)
    
    if success:
        await message.edit(content="✅ เริ่มเซิร์ฟเวอร์สำเร็จ")
    else:
        await message.edit(content="❌ เกิดข้อผิดพลาดในการเริ่มเซิร์ฟเวอร์")

# คำสั่งหยุดเซิร์ฟเวอร์
@bot.command(name="stop")
@has_minecrafter_role()
async def stop_command(ctx, server_id: str):
    message = await ctx.send("กำลังหยุดเซิร์ฟเวอร์...")
    success = await stop_server(server_id)
    
    if success:
        await message.edit(content="✅ หยุดเซิร์ฟเวอร์สำเร็จ")
    else:
        await message.edit(content="❌ เกิดข้อผิดพลาดในการหยุดเซิร์ฟเวอร์")

# คำสั่งรีสตาร์ทเซิร์ฟเวอร์
@bot.command(name="restart")
@has_minecrafter_role()
async def restart_command(ctx, server_id: str):
    message = await ctx.send("กำลังรีสตาร์ทเซิร์ฟเวอร์...")
    success = await restart_server(server_id)
    
    if success:
        await message.edit(content="✅ รีสตาร์ทเซิร์ฟเวอร์สำเร็จ")
    else:
        await message.edit(content="❌ เกิดข้อผิดพลาดในการรีสตาร์ทเซิร์ฟเวอร์")

@bot.command(name="credits")
@has_minecrafter_role()
async def credits_command(ctx):
    message = await ctx.send("กำลังตรวจสอบเครดิตที่เหลือ...")
    credits = await get_account_credits()
    
    if credits is not None:
        embed = discord.Embed(title="ข้อมูลเครดิต exaroton", color=discord.Color.gold())
        embed.add_field(name="เครดิตที่เหลือ", value=f"{credits:,} เครดิต", inline=False)
        embed.add_field(name="", value="6 เครดิต = 1 ชั่วโมงการใช้งานเซิร์ฟเวอร์", inline=False)
        embed.timestamp = discord.utils.utcnow()
        await message.edit(content=None, embed=embed)
    else:
        await message.edit(content="❌ เกิดข้อผิดพลาดในการตรวจสอบเครดิต")
        
# คำสั่งส่งคำสั่งไปยังเซิร์ฟเวอร์
@bot.command(name="cmd")
async def cmd_command(ctx, server_id: str, *, command: str):
    message = await ctx.send(f"กำลังส่งคำสั่ง: {command}")
    success = await execute_command(server_id, command)
    
    if success:
        await message.edit(content=f"✅ ส่งคำสั่ง: {command} สำเร็จ")
    else:
        await message.edit(content="❌ เกิดข้อผิดพลาดในการส่งคำสั่ง")

# คำสั่งช่วยเหลือ
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="คำสั่งบอท exaroton", color=discord.Color.blue())
    
    embed.add_field(name="!exaroton servers", value="แสดงรายการเซิร์ฟเวอร์ทั้งหมด", inline=False)
    embed.add_field(name="!exaroton status <server_id>", value="แสดงสถานะของเซิร์ฟเวอร์", inline=False)
    embed.add_field(name="!exaroton start <server_id>", value="เริ่มเซิร์ฟเวอร์", inline=False)
    embed.add_field(name="!exaroton stop <server_id>", value="หยุดเซิร์ฟเวอร์", inline=False)
    embed.add_field(name="!exaroton restart <server_id>", value="รีสตาร์ทเซิร์ฟเวอร์", inline=False)
    embed.add_field(name="!exaroton credits", value="แสดงเครดิต exaroton ที่เหลือ", inline=False)
    embed.add_field(name="!exaroton cmd <server_id> <command>", value="ส่งคำสั่งไปยังเซิร์ฟเวอร์", inline=False)
    
    embed.add_field(name="หมายเหตุ", value="คำสั่งส่วนใหญ่สามารถใช้ได้เฉพาะผู้ที่มีบทบาท 'Minecrafter' เท่านั้น", inline=False)
    
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ ไม่พบคำสั่งนี้ ใช้ `!exaroton help` เพื่อดูคำสั่งทั้งหมด")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ คำสั่งไม่ครบถ้วน ใช้ `!exaroton help` เพื่อดูวิธีใช้คำสั่ง")
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        print(f"เกิดข้อผิดพลาด: {error}")
        
def run_webserver():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "บอททำงานอยู่! 🚀"
    
    app.run(host='0.0.0.0', port=8080)

# รันเว็บเซิร์ฟเวอร์ในเธรดแยก
threading.Thread(target=run_webserver).start()

# เริ่มการทำงานของบอท
if __name__ == "__main__":
    bot.run(BOT_TOKEN)