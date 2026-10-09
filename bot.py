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
    cookies = {
        ".ROBLOSECURITY": "f9vYndjmbEqpZ1dyDRbI9KpwR5Xk701DRwPsG7dVywgD1IbjZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SW1ZNWRsbHVaR3B0WWtWeGNGb3haSGxFVW1KSk9VdHdkMUkxV0dzM01ERkVVbmRRYzBjM1pGWjVkMmRFTVVsaWFpSXNJbTkzYm1WeVNXUWlPaUl4TVRRME56STVNalkwTmlJc0ltVjRjQ0k2TVRjNU1UVTNOekV3Tnl3aWFXRjBJam94TnpreE5UY3pOVEEzTENKdVltWWlPakUzT1RFMU56TTFNRGQ5LmlkaFpkTXVPYm1DVEE5MHh6c3R5SlVuYThja1lWWkJnTk9DZU9QeGN1REJpZlZ0ZE5jTEhQQ3N3RWRDTDBuWXhBVWU1UFViY0daZEp4ZzBVdzZNcG4tBjlKWWJha3JmWlRJZFlzSTJHQ1pVaUQ3ampaVTJoMzdtX19BMjZaSnVyYjMwNVBaOS1NMTNFYjFiMEFpWEZ0NU1xaUN1bHJodmRiOEhWLTRrWkpsMUZfTmlhajZLZTNBNHRiYUk1dkNoVE9tdUZXcm13clpTdnhLVThxUV9QRDljSXNKYjlYZUtjTDVOSzJ1JjllMVBEaTRZYnNBSHhIMEFIU1I1UnVPZk1zM240Vm9zbzBUQktTOGRmd05tY2xuZTRTLWtUUU16Zk9DcV9lVFJOTThNNVVHeUdFUFkzSW90bk9xSmU4QkgtUHVuTmRFZWp1WkI4MkNsR2NsRjJmZw=="
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, cookies=cookies, headers=headers)

    if response.status_code != 200:
        embed = discord.Embed(
            title="Kết Quả Kiểm Tra Group Roblox",
            color=0xFF0000,
            description="❌ **Chưa đạt điều kiện:** Không thể tải dữ liệu group của người dùng."
        )
        embed.add_field(name="Roblox User", value=f"{user_input} (ID: {roblox_user_id})", inline=False)
        embed.add_field(name="Ngày Tham Gia", value="Chưa tham gia", inline=True)
        embed.add_field(name="Thời Gian Ở Trong Group", value="0 ngày", inline=True)
        await ctx.send(embed=embed)
        return

    data = response.json()
    groups = data.get("data", [])

    # Đoạn này là phần bị thiếu trong ảnh của Tùng:
    target_group = None
    for g in groups:
        if str(g.get("group", {}).get("id")) == str(GROUP_ID):
            target_group = g
            break

    if not target_group:
        embed = discord.Embed(
            title="Kết Quả Kiểm Tra Group Roblox",
            color=0xFF0000,
            description="❌ **Chưa đạt điều kiện:** Người dùng chưa tham gia group."
        )
        embed.add_field(name="Roblox User", value=f"{user_input} (ID: {roblox_user_id})", inline=False)
        embed.add_field(name="Ngày Tham Gia", value="Chưa tham gia", inline=True)
        embed.add_field(name="Thời Gian Ở Trong Group", value="0 ngày", inline=True)
        await ctx.send(embed=embed)
        return

    created_str = target_group.get("joined")
    if not created_str:
        await ctx.send(f"❌ Không thể đọc được mốc thời gian tham gia group của `{user_input}` !")
        return

    join_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    days_in_group = (now - join_date).days
    formatted_date = join_date.strftime("%d/%m/%Y")

    embed = discord.Embed(
        title="Kết Quả Kiểm Tra Group Roblox",
        color=0x00FF00 if days_in_group >= 14 else 0xFF0000,
    )

    if days_in_group >= 14:
        embed.description = "✅ **Đạt điều kiện:** Đã tham gia group trên 14 ngày."
    else:
        embed.description = "❌ **Chưa đạt điều kiện:** Chưa đủ 14 ngày tham gia group."

    embed.add_field(name="Roblox User", value=f"{user_input} (ID: {roblox_user_id})", inline=False)
    embed.add_field(name="Ngày Tham Gia", value=formatted_date, inline=True)
    embed.add_field(name="Thời Gian Ở Trong Group", value=f"{days_in_group} ngày", inline=True)

    await ctx.send(embed=embed)
