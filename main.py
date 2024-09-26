import discord
import yaml
import sqlite3
import rich
import datetime
import pytz


def Config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


class Today:
    def __init__(self):
        self.today = ""


bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    rich.print(f"[green]Logged in as {bot.user}[/green]")


@bot.event
async def on_message(message):
    # 每位用戶在新的一天傳送的第一個訊息就會被標記為"已簽到"
    # 台灣時區
    # 紀錄每天有哪些用戶簽到在 database/days.db 用 sqlite
    # 資料庫格式像是 table 名稱: 2024_09_24
    # user.id | 2024/09/24 00:00:01
    if message.author.bot:
        return

    # 連接資料庫
    conn = sqlite3.connect("database/days.db")
    cursor = conn.cursor()

    # 將日期格式化為 "2024-09-24"，並使用雙引號來包裹表名
    today = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d")
    cursor.execute(
        f'CREATE TABLE IF NOT EXISTS "{today}" (user_id INTEGER PRIMARY KEY, time TEXT)'
    )
    conn.commit()

    # 查詢該 user_id 是否已簽到，並插入資料
    cursor.execute(f'SELECT * FROM "{today}" WHERE user_id = {message.author.id}')
    if not cursor.fetchone():
        cursor.execute(
            f'INSERT INTO "{today}" (user_id, time) VALUES ({message.author.id}, "{datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y/%m/%d %H:%M:%S")}")'
        )
        conn.commit()

        # 檢查這位用戶是今天第幾位簽到的
        # 如果是第一位簽到的給他特別獎勵
        cursor.execute(f'SELECT * FROM "{today}"')
        data = cursor.fetchall()
        if len(data) == 1:
            # 紀錄首位簽到者到 database/first.db
            # table 名稱為 "user_id"
            conn_first = sqlite3.connect("database/first.db")
            cursor_first = conn_first.cursor()
            cursor_first.execute(
                f'CREATE TABLE IF NOT EXISTS "{message.author.id}" (day INTEGER PRIMARY KEY)'
            )
            conn_first.commit()
            # 新增一條資料在 table {user_id}
            # "2024/09/25" 為 day
            cursor_first.execute(
                f'INSERT INTO "{message.author.id}" (day) VALUES ("{datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y/%m/%d")}")'
            )
            conn_first.commit()
            await message.add_reaction("<:owner:1288358940110884976>")

        # 給予該訊息 reaction
        await message.add_reaction("<:green_dot:1288058134551593000>")

    # 使用 database/users.db 記錄一位用戶簽到過的天數
    # table 名稱: {user_id}
    # 2024/09/23
    # 2024/09/24

    # 連線資料庫
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    user_id = message.author.id
    today = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y/%m/%d")
    # 使用雙引號包裹 user_id 作為表名
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{user_id}" (date TEXT PRIMARY KEY)')
    cursor.execute(f'SELECT * FROM "{user_id}" WHERE date = "{today}"')
    if not cursor.fetchone():
        cursor.execute(f'INSERT INTO "{user_id}" (date) VALUES ("{today}")')
        conn.commit()


@bot.slash_command(name="簽到天數", description="查看您簽到過的天數")
async def 簽到天數(ctx):
    # 連接資料庫
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    # 調取資料
    user_id = ctx.author.id
    # 使用單引號來確保 SQL 語法正確
    try:
        cursor.execute(f"SELECT * FROM '{user_id}'")
        data = cursor.fetchall()
    except:
        embed = discord.Embed(title="你還沒有簽到過", color=discord.Colour.red())
        embed.set_thumbnail(url="https://cdn3.emoji.gg/emojis/4934-error.png")
        return

    # 計算簽到天數
    days = len(data)

    # 計算連續簽到天數
    continuous_days = 1
    for i in range(1, len(data)):
        # 判斷是否為連續簽到
        if (
            datetime.datetime.strptime(data[i][0], "%Y/%m/%d")
            - datetime.datetime.strptime(data[i - 1][0], "%Y/%m/%d")
        ).days == 1:
            continuous_days += 1
        else:
            break

    # 計算頭香天數
    # 從 database/first.db 取得資料
    conn_first = sqlite3.connect("database/first.db")
    cursor_first = conn_first.cursor()
    # 如果 user_id 不在裡面就創建一條
    cursor_first.execute(
        f'CREATE TABLE IF NOT EXISTS "{user_id}" (date TEXT PRIMARY KEY)'
    )
    conn_first.commit()
    cursor_first.execute(f"SELECT * FROM '{user_id}'")
    first_data = cursor_first.fetchall()
    first_days = len(first_data)

    # 回復訊息
    embed = discord.Embed(title="簽到數據", color=discord.Colour.green())
    embed.description = f"> 總簽到天數: {days}\n> 連續簽到天數: {continuous_days}\n\n> 頭香次數: {first_days}"
    embed.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.respond(embed=embed)

    # 關閉資料庫連接
    conn.close()


if "__main__" == __name__:
    bot.run(Config()["Token"])
