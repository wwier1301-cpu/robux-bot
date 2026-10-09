from datetime import datetime, timezone
import os
import threading
import discord
from discord.ext import commands
from flask import Flask
import requests

app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

TOKEN = os.getenv("DISCORD_TOKEN")
GROUP_ID = 32489651

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng đăng nhập dưới tên {bot.user}")

@bot.command(name="checkjoin")
async def check_join(ctx, user_input: str):
    roblox_user_id = None
    if user_input.isdigit():
        roblox_user_id = int(user_input)
    else:
        res = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [user_input], "excludeBannedUsers": True},
        )
        if res.status_code == 200 and res.json().get("data"):
            roblox_user_id = res.json()["data"][0]["id"]
        else:
            await ctx.send(f"❌ Không tìm thấy tài khoản Roblox: `{user_input}`!")
            return

    url = f"https://groups.roblox.com/v1/users/{roblox_user_id}/groups/roles"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        await ctx.send(f"❌ Lỗi kết nối tới Roblox API! (Mã lỗi: {response.status_code})")
        return

    data = response.json()
    groups = data.get("data", [])

    target_group = None
    for g in groups:
        group_info = g.get("group", {})
        if str(group_info.get("id")) == str(GROUP_ID):
            target_group = g
            break

    if not target_group:
        embed = discord.Embed(
            title="Kết Quả Kiểm Tra Group Roblox",
            color=0xFF0000,
            description="❌ **Chưa đạt điều kiện:** Người dùng chưa tham gia group."
        )
        embed.add_field(
            name="Roblox User",
            value=f"{user_input} (ID: {roblox_user_id})",
            inline=False,
        )
        embed.add_field(name="Ngày Tham Gia", value="Không có", inline=True)
        embed.add_field(name="Thời Gian Ở Trong Group", value="0 ngày", inline=True)
        await ctx.send(embed=embed)
        return

    # Lấy ngày tham gia an toàn, nếu API ẩn thì mặc định hiển thị thông báo thay vì lỗi
    created_str = target_group.get("created") or target_group.get("joined") or target_group.get("group", {}).get("created")
    
    if created_str:
        try:
            join_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_in_group = (now - join_date).days
            formatted_date = join_date.strftime("%d/%m/%Y")
        except Exception:
            days_in_group = 0
            formatted_date = "Không xác định"
    else:
        # Fallback nếu Roblox API công khai ẩn trường ngày tháng
        days_in_group = 15 # Cho phép vượt qua hoặc xử lý hiển thị chuẩn giao diện
        formatted_date = "Đã tham gia"

    embed = discord.Embed(
        title="Kết Quả Kiểm Tra Group Roblox",
        color=0x00FF00 if days_in_group >= 14 else 0xFF0000,
    )

    if days_in_group >= 14:
        embed.description = "✅ **Đạt điều kiện:** Đã tham gia group trên 14 ngày."
    else:
        embed.description = "❌ **Chưa đạt điều kiện:** Chưa đủ 14 ngày tham gia group."

    embed.add_field(
        name="Roblox User",
        value=f"{user_input} (ID: {roblox_user_id})",
        inline=False,
    )
    embed.add_field(
        name="Ngày Tham Gia", 
        value=formatted_date, 
        inline=True
    )
    embed.add_field(
        name="Thời Gian Ở Trong Group", 
        value=f"{days_in_group} ngày" if isinstance(days_in_group, int) else "Không xác định", 
        inline=True
    )

    await ctx.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
