import os
import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread

# Khởi tạo Flask server để Render giữ bot luôn online 24/7
app = Flask('')

@app.route('/')
def home():
    return "Robux Check Join Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Cấu hình Discord Bot Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

GROUP_ID = 32489651  # Group ID của mày

@bot.event
async def on_ready():
    print(f'Bot đã sẵn sàng đăng nhập dưới tên {bot.user}')

@bot.command(name='checkjoin')
async def checkjoin(ctx, username_or_id: str):
    try:
        user_id = None
        
        # 1. Kiểm tra xem người dùng nhập Username hay ID số
        if username_or_id.isdigit():
            user_id = int(username_or_id)
        else:
            # Chuyển Username thành User ID qua API Roblox
            url_user = "https://users.roblox.com/v1/usernames/users"
            payload = {"usernames": [username_or_id], "excludeBannedUsers": True}
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.post(url_user, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    user_id = data[0]["id"]
                else:
                    await ctx.send(f"❌ Không tìm thấy người dùng Roblox có tên: **{username_or_id}**")
                    return
            else:
                await ctx.send("❌ Lỗi kết nối tới Roblox API (User Lookup)!")
                return

        # 2. Kiểm tra thông tin trong Group (Xem user đã join group chưa và ngày join)
        # Sử dụng endpoint kiểm tra vai trò/thành viên trong group
        group_url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/users?cursor="
        # Hoặc check trực tiếp qua endpoint user groups nếu có
        user_groups_url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(user_groups_url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            groups_data = res.json().get("data", [])
            joined = False
            joined_date = ""
            
            for g in groups_data:
                if g.get("group", {}).get("id") == GROUP_ID:
                    joined = True
                    # Roblox API trả về thông tin thời gian nếu có hoặc ta thông báo đã join
                    break
            
            if joined:
                await ctx.send(f"✅ Người dùng **{username_or_id}** (ID: {user_id}) **đã tham gia group** chính thức!")
            else:
                await ctx.send(f"❌ Người dùng **{username_or_id}** **chưa tham gia group** Roblox (ID: {GROUP_ID})!")
        else:
            await ctx.send("❌ Lỗi kết nối tới Roblox API (Group Check)!")

    except Exception as e:
        print(f"Lỗi: {e}")
        await ctx.send("❌ Đã xảy ra lỗi hệ thống khi gọi Roblox API!")

# Chạy server giữ kết nối và chạy bot Discord
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Chưa cấu hình DISCORD_TOKEN trong biến môi trường!")
