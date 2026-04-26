import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Header
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

# IMPORTANT FOR PRODUCTION: When you deploy to Railway and get a custom domain 
# (e.g., https://my-bot.up.railway.app/), change this variable to match it!
# You will also need to add the new URL to your Discord Developer Portal Redirects.
REDIRECT_URI = "https://web-production-3a50e.up.railway.app/" 

# --- 1. INITIALIZE FASTAPI ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- 2. INITIALIZE DISCORD BOT ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class HybridBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # Initialize database connection
        self.mongo_cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.mongo_cluster["DiscordBotDB"]

    async def setup_hook(self):
        # Load all functional cogs
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.advanced_logs")
        await self.load_extension("cogs.roles")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.temp_voice")
        await self.load_extension("cogs.stats")
        await self.load_extension("cogs.leveling")
        await self.load_extension("cogs.ai_tools")
        await self.load_extension("cogs.utility")

        # Make UI Views Persistent (Buttons work after restart)
        from cogs.tickets import TicketPanel, TicketControls
        from cogs.temp_voice import TempVCControls
        self.add_view(TicketPanel(self))
        self.add_view(TicketControls(self))
        self.add_view(TempVCControls(self))
        
        # Sync slash commands to Discord
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
    """Serves the main HTML dashboard."""
    return FileResponse("dashboard.html")

@app.get("/api/config")
async def get_public_config():
    """Provides the frontend with the public Client ID safely."""
    return {"client_id": CLIENT_ID}

@app.post("/api/auth/login")
async def verify_login(req: AuthRequest):
    """Handles the OAuth2 login flow with Discord."""
    async with httpx.AsyncClient() as client:
        # 1. Exchange the code for an Access Token
        token_res = await client.post("https://discord.com/api/oauth2/token", data={
            "client_id": CLIENT_ID, 
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code", 
            "code": req.code, 
            "redirect_uri": REDIRECT_URI
        })
        token_json = token_res.json()
        if "access_token" not in token_json: 
            raise HTTPException(status_code=400, detail="Invalid code.")
            
        access_token = token_json["access_token"]
        
        # 2. Fetch User Profile
        user_res = await client.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"})
        
        # 3. Fetch User's Servers
        guilds_res = await client.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"})
        
        # 4. Filter for servers where the user is an Administrator (0x8)
        admin_guilds = [
            {"id": g["id"], "name": g["name"], "icon": g.get("icon")} 
            for g in guilds_res.json() 
            if (int(g["permissions"]) & 0x8) == 0x8
        ]
        
        return {"status": "success", "user": user_res.json(), "admin_guilds": admin_guilds, "access_token": access_token}

@app.post("/api/settings/update")
async def api_update_settings(settings: SettingsUpdate, authorization: str = Header(None)):
    """Handles updates sent from the web dashboard."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    access_token = authorization.split("Bearer ")[1]

    async with httpx.AsyncClient() as client:
        guilds_res = await client.get("https://discord.com/api/users/@me/guilds", headers={"Authorization": f"Bearer {access_token}"})
        if guilds_res.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_guilds = guilds_res.json()
        target_guild = next((g for g in user_guilds if int(g["id"]) == settings.guild_id), None)

        if not target_guild or (int(target_guild["permissions"]) & 0x8) != 0x8:
            raise HTTPException(status_code=403, detail="Forbidden: You must be an administrator of this server.")

    update_data = {}
    if settings.log_channel_id: update_data["log_channel_id"] = settings.log_channel_id
    if settings.auto_role_id: update_data["auto_role_id"] = settings.auto_role_id

    # Handle immediate actions (like Lockdown)
    if settings.lockdown_channel_id:
        guild = bot.get_guild(settings.guild_id)
        if not guild: 
            return {"status": "error", "detail": "Bot is not in this server."}
        
        channel = guild.get_channel(settings.lockdown_channel_id)
        if channel:
            await channel.set_permissions(guild.default_role, send_messages=False)
            await channel.send("🔒 **Channel locked via Web Dashboard.**")
            return {"status": "success", "message": "Channel Locked!"}

    # Handle database saves
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
    # Automatically grabs Railway's assigned port, or defaults to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    
    # Host MUST be 0.0.0.0 for Railway to expose the web server to the internet
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the Discord bot and the Web API concurrently
    await asyncio.gather(bot.start(DISCORD_TOKEN), server.serve())

if __name__ == "__main__":
    asyncio.run(main())
