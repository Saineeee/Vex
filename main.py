import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import motor.motor_asyncio
import httpx
import asyncio
import uvicorn
import os
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/"

# --- 1. INITIALIZE FASTAPI ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- 2. INITIALIZE DISCORD BOT ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class HybridBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.mongo_cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.mongo_cluster["DiscordBotDB"]

    async def setup_hook(self):
        # Load all cogs
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.advanced_logs")
        await self.load_extension("cogs.roles")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.temp_voice")
        await self.load_extension("cogs.stats")
        await self.load_extension("cogs.leveling")
        await self.load_extension("cogs.ai_tools")
        await self.load_extension("cogs.utility")

        # Make UI Views Persistent
        from cogs.tickets import TicketPanel, TicketControls
        from cogs.temp_voice import TempVCControls
        self.add_view(TicketPanel(self))
        self.add_view(TicketControls(self))
        self.add_view(TempVCControls(self))
        
        await self.tree.sync()
        print("Bot is online, views persistent, and slash commands synced!")

bot = HybridBot()

# --- 3. API DATA MODELS ---
class AuthRequest(BaseModel):
    code: str

class SettingsUpdate(BaseModel):
    guild_id: int
    log_channel_id: int = None
    auto_role_id: int = None
    lockdown_channel_id: int = None

# --- 4. API ENDPOINTS (DASHBOARD CONTROLS) ---
@app.get("/")
async def serve_dashboard():
    return FileResponse("dashboard.html")

@app.get("/api/config")
async def get_public_config():
    return {"client_id": CLIENT_ID}

@app.post("/api/auth/login")
async def verify_login(req: AuthRequest):
    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://discord.com/api/oauth2/token", data={
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code", "code": req.code, "redirect_uri": REDIRECT_URI
        })
        token_json = token_res.json()
        if "access_token" not in token_json: raise HTTPException(status_code=400, detail="Invalid code.")
            
        access_token = token_json["access_token"]
        user_res = await client.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"})
        guilds_res = await client.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"})
        
        admin_guilds = [{"id": g["id"], "name": g["name"], "icon": g.get("icon")} for g in guilds_res.json() if (int(g["permissions"]) & 0x8) == 0x8]
        return {"status": "success", "user": user_res.json(), "admin_guilds": admin_guilds}

@app.post("/api/settings/update")
async def api_update_settings(settings: SettingsUpdate):
    update_data = {}
    if settings.log_channel_id: update_data["log_channel_id"] = settings.log_channel_id
    if settings.auto_role_id: update_data["auto_role_id"] = settings.auto_role_id

    if settings.lockdown_channel_id:
        guild = bot.get_guild(settings.guild_id)
        if not guild: return {"status": "error", "detail": "Bot is not in this server."}
        channel = guild.get_channel(settings.lockdown_channel_id)
        if channel:
            await channel.set_permissions(guild.default_role, send_messages=False)
            await channel.send("🔒 **Channel locked via Web Dashboard.**")
            return {"status": "success", "message": "Channel Locked!"}

    if update_data:
        await bot.db["settings"].update_one(
            {"guild_id": settings.guild_id},
            {"$set": update_data},
            upsert=True
        )
        return {"status": "success", "message": "Settings saved to database."}
    
    return {"status": "ignored", "message": "No valid data provided."}

# --- 5. ASYNC RUNNER ---
async def main():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(bot.start(DISCORD_TOKEN), server.serve())

if __name__ == "__main__":
    asyncio.run(main())
