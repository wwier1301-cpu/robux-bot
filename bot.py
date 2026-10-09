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


# Thông tin cấu hình từ code của mày
TOKEN = "MTU1Nzk5MzI0Njg2MzY1NDkyMg.GUe8_3.9P5tUfpjjJLUqKgQiyS3JH_5dL5G9eN2E_6KuI" [cite: 7]
ROBLOX_API_KEY = "f9vYndjmbEqpZ1dyDRbI9Acj6xdDdtC3yMkRhRGpR7dY99i4ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaGRXUWlPaUpTYjJKc2IzaEpiblJsY201aGJDSXNJbWx6Y3lJNklrTnNiM1ZrUVhWMGFHVnVkR2xqWVhScGIyNVRaWEoyYVdObElpd2lZbUZ6WlVGd2FVdGxlU0k2SW1ZNWRsbHVaR3B0WWtWeGNGb3haSGxFVW1KSk9VRmphalo0WkVSa2RFTXplVTFyVW1oU1IzQlNOMlJaT1RscE5DSXNJbTkzYm1WeVNXUWlPaUl4TVRRME56STVNalkwTmlJc0ltVjRjQ0k2TVRjNU1UVXpOVFEwT1N3aWFXRjBJam94TnpreE5UTXhPRFE1TENKdVltWWlPakUzT1RFMU16RTRORGw5LllnQ0Fzdk5renNSX253dEJzOGZIcHJEaVRQYkdRRzAtakk1cGE0bXRFbjZtRmJETXZJajdYZmxTa0ZGTWVXMHZWeFU1WnhlVldxcFAxZ1dsemd5b1NNWWlkdmVWXzJUYXpsNWl3b3dMdTA3WkltLTlpRU9INFJyc1VQandUdDFNZ0tBSzJNU254RzVFX3c3MmNrMVc1UnNDZW04dzRpMFJaWEw0QXFqc0RpeDBybGhxV19aVHlnLUFuM2hXMFVHN2E5VmtDYw==" [cite: 7]
GROUP_ID = 32489651 [cite: 7]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Bot đã sẵn sàng đăng nhập dưới tên {bot.user}") [cite: 7]


@bot.command(name="checkjoin")
async def check_join(ctx, user_input: str):
  roblox_user_id = None
  if user_input.isdigit():
    roblox_user_id = int(user_input) [cite: 7]
  else:
    res = requests.post(
        "https://users.roblox.com/v1/usernames/users",
        json={"usernames": [user_input], "excludeBannedUsers": True},
    ) [cite: 7]
    if res.status_code == 200 and res.json().get("data"):
      roblox_user_id = res.json()["data"][0]["id"] [cite: 7]
    else:
      await ctx.send(f"❌ Không tìm thấy tài khoản Roblox: `{user_input}`!") [cite: 7]
      return

  url = f"https://apis.roblox.com/cloud/v2/groups/{GROUP_ID}/memberships?filter=user == 'users/{roblox_user_id}'" [cite: 7]
  headers = {"x-api-key": ROBLOX_API_KEY} [cite: 7]

  response = requests.get(url, headers=headers) [cite: 7]

  if response.status_code != 200:
    await ctx.send("❌ Lỗi kết nối tới Roblox API!") [cite: 7]
    return

  data = response.json() [cite: 7]
  memberships = data.get("groupMemberships", []) [cite: 7]

  if not memberships:
    await ctx.send(f"❌ Người dùng `{user_input}` chưa tham gia group!") [cite: 7]
    return

  create_time_str = memberships[0].get("createTime") [cite: 7]
  join_date = datetime.fromisoformat(create_time_str.replace("Z", "+00:00")) [cite: 7]
  now = datetime.now(timezone.utc) [cite: 7]

  days_in_group = (now - join_date).days [cite: 7]
  formatted_date = join_date.strftime("%d/%m/%Y") [cite: 7]

  embed = discord.Embed(
      title="Kết Quả Kiểm Tra Group Roblox",
      color=0x00FF00 if days_in_group >= 14 else 0xFF0000,
  ) [cite: 7]
  embed.add_field(
      name="Roblox User",
      value=f"{user_input} (ID: {roblox_user_id})",
      inline=False,
  ) [cite: 7]
  embed.add_field(name="Ngày Tham Gia", value=formatted_date, inline=True) [cite: 7]
  embed.add_field(
      name="Thời Gian Ở Trong Group", value=f"{days_in_group} ngày", inline=True
  ) [cite: 7]

  if days_in_group >= 14:
    embed.description = (
        "✅ **Đạt điều kiện:** Đã tham gia group trên 14 ngày."
    ) [cite: 7]
  else:
    embed.description = (
        "❌ **Chưa đạt điều kiện:** Chưa đủ 14 ngày tham gia group."
    ) [cite: 7]

  await ctx.send(embed=embed) [cite: 7]


# Khởi động cả Flask web server lẫn Bot Discord cùng lúc
if __name__ == "__main__":
  keep_alive()
  bot.run(TOKEN) [cite: 7]
