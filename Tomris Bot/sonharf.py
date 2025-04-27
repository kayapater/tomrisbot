import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import json

TURKISH_WORDS = [
    "araba", "balık", "ceviz", "deniz", "elma", "fare", "gemi", "harita", 
    "ışık", "kalem", "limon", "meyve", "nar", "orman", "pencere", "radyo", 
    "saat", "telefon", "uçak", "vazo", "yastık", "zaman", "çiçek", "şapka",
    "öğrenci", "üzüm", "ağaç", "bardak", "çanta", "defter", "ev", "fırın",
    "güneş", "halı", "ırmak", "jeton", "kitap", "lamba", "masa", "nehir",
    "otobüs", "para", "resim", "sandalye", "tabak", "uyku", "vatan", "yemek",
    "zemin", "çorap", "şeker", "ördek", "ütü", "ıhlamur", "ıspanak"
]

class SonHarfCog(commands.Cog):
    def __init__(self, bot, db, translations):
        self.bot = bot
        self.db = db
        self.translations = translations
        
    def is_admin():
        async def predicate(interaction: discord.Interaction):
            if interaction.user.guild_permissions.administrator:
                return True
            await interaction.response.send_message("Bu komutu kullanmak için yönetici yetkisine sahip olmalısınız!", ephemeral=True)
            return False
        return app_commands.check(predicate)
    
    @app_commands.command(name="sonharf", description="Son Harf Oyunu başlat veya durdur")
    @app_commands.describe(
        action="İşlem (başlat/durdur/bilgi)",
        kelimegir="İlk kelime (sadece başlat işlemi için)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Başlat", value="baslat"),
        app_commands.Choice(name="Durdur", value="durdur"),
        app_commands.Choice(name="Bilgi", value="bilgi")
    ])
    @is_admin()
    async def sonharf(self, interaction: discord.Interaction, action: str, kelimegir: str = None):
        server_id = interaction.guild.id
        language = self.db.get_server_language(server_id)
        translations = self.translations[language]['son_harf']
        
        if action.lower() == "başlat" or action.lower() == "start" or action.lower() == "baslat":
            game_data = self.db.get_son_harf_game(server_id)
            if game_data and game_data['active']:
                await interaction.response.send_message(translations['already_active'], ephemeral=True)
                return
            
            if not kelimegir:
                first_word = random.choice(TURKISH_WORDS)
            else:
                first_word = kelimegir
            
            self.db.start_son_harf_game(server_id, interaction.channel_id, first_word)
            
            await interaction.response.send_message(
                translations['game_started'].format(word=first_word)
            )
            
            await interaction.channel.send(
                translations['game_info'].format(word=first_word)
            )
        
        elif action.lower() == "durdur" or action.lower() == "stop" or action.lower() == "dur":
            game_data = self.db.get_son_harf_game(server_id)
            if not game_data or not game_data['active']:
                await interaction.response.send_message(translations['not_active'], ephemeral=True)
                return
            
            self.db.stop_son_harf_game(server_id)
            await interaction.response.send_message(translations['game_stopped'])
        
        elif action.lower() == "bilgi" or action.lower() == "info" or action.lower() == "bilgi":
            game_data = self.db.get_son_harf_game(server_id)
            if not game_data or not game_data['active']:
                await interaction.response.send_message(translations['not_active'], ephemeral=True)
                return
            
            await interaction.response.send_message(
                translations['game_info'].format(word=game_data['current_word'])
            )
        
        else:
            await interaction.response.send_message(
                "Geçersiz işlem. Kullanım: `/sonharf başlat [ilk_kelime]`, `/sonharf durdur` veya `/sonharf bilgi`",
                ephemeral=True
            )
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        server_id = message.guild.id
        
        game_data = self.db.get_son_harf_game(server_id)
        if not game_data or not game_data['active']:
            return
        
        if message.channel.id != game_data['channel_id']:
            return
        
        word = message.content.strip().lower()
        
        if ' ' in word:
            return
        
        if not all(c.isalpha() or c in 'çğıöşüÇĞİÖŞÜ' for c in word):
            return
        
        current_word = game_data['current_word'].lower()
        
        if message.author.id == game_data['last_user_id']:
            await message.delete()
            error_msg = await message.channel.send(self.translations[self.db.get_server_language(server_id)]['son_harf']['same_user'])
            await asyncio.sleep(3)
            await error_msg.delete()
            return
        
        if word[0] != current_word[-1]:
            await message.delete()
            error_msg = await message.channel.send(
                self.translations[self.db.get_server_language(server_id)]['son_harf']['wrong_start_letter'].format(word=current_word)
            )
            await asyncio.sleep(3)
            await error_msg.delete()
            return
        
        used_words = game_data['used_words']
        if word in used_words:
            await message.delete()
            error_msg = await message.channel.send(self.translations[self.db.get_server_language(server_id)]['son_harf']['word_used'])
            await asyncio.sleep(3)
            await error_msg.delete()
            return
        
        used_words.append(word)
        self.db.update_son_harf_game(server_id, word, message.author.id, used_words)
        
        await message.add_reaction('✅')

async def setup(bot, db, translations):
    await bot.add_cog(SonHarfCog(bot, db, translations))
