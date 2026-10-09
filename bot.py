from datetime import datetime, timezone
import os
import threading
import discord
from discord.ext import commands
from flask import Flask
import requests

# Khởi tạo Flask server để Render nhận diện dịch vụ web đang chạy 24/7
app = Flask("")


@app.route("/")
def home():
  return "Bot is running!"


def run():
  # Lấy cổng (port) từ môi trường của Render hoặc mặc định là 8080
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


def keep_alive():
  t = threading.Thread(target=run)
  t.start()


# Lấy thông tin bảo mật từ biến môi trường (Environment Variables) của Render
TOKEN = os.getenv("DISCORD_TOKEN")
ROBLOX_API_KEY = os.getenv("ROBLOX_API_KEY")
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

  url = f"https://apis.roblox.com/cloud/v2/groups/{GROUP_ID}/memberships?filter=user == 'users/{roblox_user_id}'"
  headers = {"x-api-key": ROBLOX_API_KEY}

  response = requests.get(url, headers=headers)

  if response.status_code != 200:
    await ctx.send("❌ Lỗi kết nối tới Roblox API!")
    return

  data = response.json()
  memberships = data.get("groupMemberships", [])

  if not memberships:
    await ctx.send(f"❌ Người dùng `{user_input}` chưa tham gia group!")
    return

  create_time_str = memberships[0].get("createTime")
  join_date = datetime.fromisoformat(create_time_str.replace("Z", "+00:00"))
  now = datetime.now(timezone.utc)

  days_in_group = (now - join_date).days
  formatted_date = join_date.strftime("%d/%m/%Y")

  embed = discord.Embed(
      title="Kết Quả Kiểm Tra Group Roblox",
      color=0x00FF00 if days_in_group >= 14 else 0xFF0000,
  )
  embed.add_field(
      name="Roblox User",
      value=f"{user_input} (ID: {roblox_user_id})",
      inline=False,
  )
  embed.add_field(name="Ngày Tham Gia", value=formatted_date, inline=True)
  embed.add_field(
      name="Thời Gian Ở Trong Group", value=f"{days_in_group} ngày", inline=True
  )

  if days_in_group >= 14:
    embed.description = (
        "✅ **Đạt điều kiện:** Đã tham gia group trên 14 ngày."
    )
  else:
    embed.description = (
        "❌ **Chưa đạt điều kiện:** Chưa đủ 14 ngày tham gia group."
    )

  await ctx.send(embed=embed)


# Khởi động cả Flask web server lẫn Bot Discord cùng lúc
if __name__ == "__main__":
  keep_alive()
  bot.run(TOKEN)
