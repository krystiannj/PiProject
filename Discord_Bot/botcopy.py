from dotenv import load_dotenv
import os
import psycopg2
import discord
from discord import app_commands
from playwright.async_api import async_playwright
from datetime import datetime


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

DASHBOARD_URL = (
    "http://10.42.0.246:3000/d/"
    "cad53688-a1f7-48fb-998f-f4400471656c/"
    "statistics-1-line"
    "?orgId=1&refresh=5s&from=now-5m&to=now"
)
def get_status():

    conn = psycopg2.connect(
        host= os.getenv("HOST"),
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ON (container_name)
            container_name,
            timestamp
        FROM system_stats
        WHERE container_name IN (
            'monitor1',
            'monitor2',
            'monitor3'
        )
        ORDER BY container_name, timestamp DESC
    """)
    status = cur.fetchall()

    cur.close()
    conn.close()

    return status

def get_backup():
    backup_dir = "/home/nomadai/pi_backups"

    files = [
        f for f in os.listdir(backup_dir)
        if f.endswith(".sql.gz")
    ]

    if not files:
        return None

    latest = max(
        files,
        key=lambda f: os.path.getmtime(
            os.path.join(backup_dir, f)
        )
    )

    path = os.path.join(backup_dir, latest)

    size_mb = round(
        os.path.getsize(path) / (1024 * 1024),
        2
    )

    modified = datetime.fromtimestamp(
        os.path.getmtime(path)
    )

    return latest, size_mb, modified
def get_storage():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT storage_usage, storage_free, storage_total, storage_used
        FROM system_stats
        ORDER by timestamp DESC
        LIMIT 1
    """)
    usage, free, total, used = cur.fetchone()

    cur.close()
    conn.close()

    return usage, free, total, used

def get_swap():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT swap_usage
        FROM system_stats
        ORDER by timestamp DESC
        LIMIT 1
    """)
    swap = cur.fetchone()[0]

    cur.close()
    conn.close()

    return swap

def get_memory():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT memory_usage
        FROM system_stats
        ORDER by timestamp DESC
        LIMIT 1
    """)
    memory = cur.fetchone()[0]

    cur.close()
    conn.close()

    return memory

def get_temperature():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT cpu_temperature
        FROM system_stats
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    temperature = cur.fetchone()[0]
    cur.close()
    conn.close()

    return temperature
def get_cpu():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT cpu_usage
        FROM system_stats
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    usage = cur.fetchone()[0]

    cur.close()
    conn.close()

    return usage
def get_honeypot():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT ip_address, timestamp
        FROM honeypot_logs
        ORDER BY timestamp DESC
        LIMIT 5
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data
def get_tophoney():

    conn = psycopg2.connect(
        host="10.42.0.246",
        database= os.getenv("DATABASE_NAME"),
        user= os.getenv("DATABASE_USER"),
        password= os.getenv("DATABASE_PASSWORD")
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT ip_address,
            COUNT(*)
        FROM honeypot_logs
        GROUP BY ip_address 
        ORDER BY COUNT(*) DESC
        LIMIT 5;
    """)

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="dashboard", description="Send Grafana dashboard")
async def dashboard(interaction: discord.Interaction):

    await interaction.response.defer()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            storage_state="/home/nomadai/Downloads/Discord_Bot/state.json",
            viewport={
                "width": 1920,
                "height": 1080
            }
        )

        page = await context.new_page()

        await page.goto(DASHBOARD_URL)

        await page.wait_for_load_state("networkidle")

        await page.screenshot(
            path="dashboard.png"
        )

        await browser.close()

    await interaction.followup.send(
        file=discord.File("dashboard.png")
    )
@client.tree.command(
    name="temperature",
    description="Show Raspberry Pi CPU temperature"
)
async def temperature(interaction: discord.Interaction):

    temperature_value = get_temperature()

    await interaction.response.send_message(
        f"Raspberry Pi Temperature:\n {temperature_value:.1f}C"
    )
@client.tree.command(
    name="cpu_usage",
    description="Show Raspberry Pi CPU Usage"
)
async def cpu_usage(interaction: discord.Interaction):

    usage_value = get_cpu()

    await interaction.response.send_message(
        f"Raspberry Pi CPU Usage:\n {usage_value:.1f}%"
    )
@client.tree.command(
    name="memory",
    description="Shows Memory Usage By %"
)
async def memory(interaction: discord.Interaction):

    memory_value = get_memory()

    await interaction.response.send_message(
        f"Raspberry Pi Memory Usage:\n {memory_value:.1f}%"
    )
@client.tree.command(
    name="swap",
    description="Shows Swap Usage By %"
)
async def swap(interaction: discord.Interaction):

    swap_value = get_swap()

    await interaction.response.send_message(
        f"Raspberry Pi Swap Usage:\n {swap_value:.1f}%"
    )
@client.tree.command(
    name="storage",
    description="Shows Storage Usage By %"
)
async def storage(interaction: discord.Interaction):

    usage, free, total, used = get_storage()

    await interaction.response.send_message(
        f"Raspberry Pi Storage Usage:\n{used}Gb/{total}Gb {usage}%\n{free}Mb Free"
    )
@client.tree.command(
    name="status",
    description="Shows container status"
)
async def status(interaction: discord.Interaction):

    await interaction.response.defer()

    from datetime import datetime, timezone

    data = get_status()

    message = "📦 Container Status\n\n"

    for container, timestamp in data:

        age = (
            datetime.now(timezone.utc) - timestamp
        ).total_seconds()

        if age < 60:
            state = "🟢 Online"
        else:
            state = "🔴 Offline"

        message += f"{container}: {state}\n"

    await interaction.followup.send(message)
@client.tree.command(
    name="health",
    description="Shows overall system health"
)
async def health(interaction: discord.Interaction):

    usage, free, total, used = get_storage()
    cpu = get_cpu()
    memory = get_memory()
    swap = get_swap()
    temperature = get_temperature()


    await interaction.response.send_message(
        f"CPU Usage: {cpu}%\nCPU Temperature: {temperature}C\nMemory Usage: {memory}%\nSwap Usage: {swap}%\nRaspberry Pi Storage Usage:\n{used}Gb/{total}Gb {usage}%\n{free}Mb Free"
    )
@client.tree.command(
    name="honeypot",
    description="Shows What IP's connected to the honeypot"
)
async def honeypot(interaction: discord.Interaction):

    data = get_honeypot()
    top = get_tophoney()

    message = "Honeypot Activity:\n"
    for ip, timestamp in data:
        message += f"{ip} At {timestamp}\n"
    
    message += f"Top Attackers:\n"
    for ip, count in top:
        message += f"{ip}: {count} attempts\n"
    await interaction.response.send_message(message)
@client.tree.command(
    name="backup",
    description="Shows backups with date and time and size"
)
async def backup(interaction: discord.Interaction):

    latest, size, modified = get_backup()

    message = "Backup:\n"
    message += f"Latest: {latest}\n"
    message += f"Size: {size}MB\n"
    message += f"Modified: {modified}\n"

    await interaction.response.send_message(message)


client.run(TOKEN)
