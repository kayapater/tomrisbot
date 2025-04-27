import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import time
import certifi
import ssl
import aiohttp
import datetime
import platform
from database import Database
import random
from datetime import datetime, timedelta
from typing import Union
import json
import re
import io
import math
import urllib.parse
import traceback
import sonharf
from pytz import timezone as pytz_timezone, all_timezones

load_dotenv()

intents = discord.Intents.all() 
intents.message_content = True

class CustomBot(commands.Bot):
    async def setup_hook(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        self.http.connector = connector

bot = CustomBot(command_prefix="!", intents=intents)

db = Database()

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Bir hata oluştu: {event}")
    import traceback
    traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Komut hatası: {error}")

@bot.event
async def on_disconnect():
    print("Bot bağlantısı kesildi. Yeniden bağlanmaya çalışılıyor...")

@bot.event
async def on_connect():
    print("Bot Discord'a bağlandı!")

@bot.event
async def on_resume():
    print("Bot yeniden bağlandı!")

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("Bu komutu kullanmak için yönetici yetkisine sahip olmalısınız!", ephemeral=True)
        return False
    return app_commands.check(predicate)

TRANSLATIONS = {
    'tr': {
        'info': {
            'title': '🤖 Tomris Bot',
            'description': 'Sunucunuzu güvenle yönetmenize yardımcı olan, gelişmiş moderasyon özellikleri ve eğlenceli oyunlarıyla donatılmış çok yönlü bir Discord botu.',
            'server_count': 'Sunucu Sayısı',
            'user_count': 'Kullanıcı Sayısı',
            'command_count': 'Komut Sayısı',
            'features_title': '✨ Özellikler',
            'features': '🛡️ **Moderasyon Komutları**\n'
                       '• Gelişmiş sunucu yönetimi\n'
                       '• Kullanıcı yönetimi (ban, kick)\n'
                       '• Kanal yönetimi ve temizlik\n\n'
                       '🎮 **Eğlence ve Ekonomi**\n'
                       '• Günlük ödüller ve ekonomi sistemi\n'
                       '• Slot makinesi ve bahis oyunları\n'
                       '• Seviye sistemi ve ödüller',
            'developer': '👨‍💻 Geliştirici',
            'developer_info': '• **Vai**\n'
                            '• [X (Twitter) Profili](https://x.com/kayapater)\n'
                            '• Discord: kayapater\n'
                            '• [Web Sitesi](https://kayapater.com.tr)',
            'support': '🔗 Bağlantılar',
            'support_link': '• [Destek Sunucusu](https://discord.gg/2RTHvbfH3a)',
            'footer': 'Tomris Bot • Güvenli ve Güçlü Yönetim'
        },
        'commands': {
            'title': '📚 Tomris Bot Komutları',
            'description': 'İşte kullanabileceğiniz tüm komutlar:',
            'mod_title': '🛡️ Moderasyon Komutları',
            'mod_cmds': '• `/ban <kullanıcı>` - Kullanıcıyı yasakla\n'
                       '• `/unban <kullanıcı_id>` - Kullanıcının yasağını kaldır\n'
                       '• `/kick <kullanıcı>` - Kullanıcıyı at\n'
                       '• `/clear <miktar>` - Belirtilen sayıda mesajı sil\n'
                       '• `/lock` - Kanalı kilitle\n'
                       '• `/unlock` - Kanal kilidini kaldır',
            'economy_title': '💰 Ekonomi Komutları',
            'economy_cmds': '• `/daily` - Günlük ödülünü al\n'
                          '• `/balance` - Bakiyeni görüntüle',
            'games_title': '🎮 Oyun Komutları',
            'games_cmds': '• `/coinflip <miktar>` - Yazı tura at (2x kazanç)\n'
                           '• `/slots <miktar>` - Slot makinesi (1x-10x kazanç)\n'
                           '• `/blackjack <miktar>` - Blackjack oyna (2x kazanç)\n'
                           '• `/roulette <miktar> <bahis_türü> [sayı]` - Rulet oyna\n'
                           '  - Renk/çift-tek/yüksek-düşük: 2x kazanç\n'
                           '  - Sayı: 35x kazanç\n'
                           '• `/sonharf <işlem> [ilk_kelime]` - Son Harf Oyunu oyna',
            'level_title': '📊 Seviye Sistemi',
            'level_cmds': '• `/rank [kullanıcı]` - Seviye bilgilerini görüntüle\n'
                        '• `/levels` - Sunucunun seviye sıralamasını görüntüle',
            'utility_title': '🛠️ Yardımcı Komutlar',
            'utility_cmds': '• `/weather <şehir>` - Hava durumunu göster\n'
                          '• `/poll <soru> [seçenekler]` - Anket oluştur',
            'settings_title': '⚙️ Diğer Komutlar',
            'settings_cmds': '• `/profile [kullanıcı]` - Profilini görüntüle\n'
                           '• `/language <dil>` - Bot dilini değiştir (tr/en)\n'
                           '• `/timezone <zaman_dilimi>` - Zaman dilimini ayarla\n'
                           '• `/ping` - Bot gecikmesini ölç\n'
                           '• `/info` - Bot hakkında bilgi al\n'
                           '• `/commands` - Bu komut listesini görüntüle',
            'footer': 'Tomris Bot • Yardım ve Komutlar'
        },
        'level': {
            'rank_title': '📊 Seviye Bilgisi',
            'level': 'Seviye',
            'xp': 'XP',
            'rank': 'Sıralama',
            'progress': 'İlerleme',
            'next_level': 'Sonraki seviye',
            'leaderboard_title': '📊 Seviye Sıralaması',
            'no_data': 'Henüz seviye verisi bulunmuyor.'
        },
        'reminder': {
            'set_success': '⏰ Hatırlatıcı ayarlandı! **{time}** tarihinde sana hatırlatacağım.',
            'list_title': '⏰ Hatırlatıcıların',
            'no_reminders': 'Aktif hatırlatıcın bulunmuyor.',
            'delete_success': 'Hatırlatıcı başarıyla silindi.',
            'delete_fail': 'Hatırlatıcı bulunamadı veya sana ait değil.',
            'reminder_time': 'Hatırlatma Zamanı',
            'time_format_error': 'Geçersiz zaman formatı. Örnek: 1h, 30m, 1d, vb.'
        },
        'custom_cmd': {
            'added': '✅ `/{name}` komutu başarıyla eklendi.',
            'deleted': '✅ `/{name}` komutu başarıyla silindi.',
            'list_title': '📝 Özel Komutlar',
            'no_commands': 'Bu sunucuda özel komut bulunmuyor.',
            'not_found': 'Komut bulunamadı.',
            'already_exists': 'Bu isimde bir komut zaten var.'
        },
        'weather': {
            'title': '🌤️ {city} Hava Durumu',
            'temperature': 'Sıcaklık',
            'feels_like': 'Hissedilen',
            'humidity': 'Nem',
            'wind': 'Rüzgar',
            'pressure': 'Basınç',
            'not_found': 'Şehir bulunamadı.',
            'error': 'Hava durumu bilgisi alınamadı.'
        },
        'poll': {
            'title': '📊 Anket: {question}',
            'vote': 'Oy vermek için aşağıdaki reaksiyonları kullanın.',
            'created_by': 'Oluşturan: {user}',
            'no_options': 'En az 2 seçenek belirtmelisin.',
            'too_many_options': 'En fazla 10 seçenek belirtebilirsin.'
        },
        'son_harf': {
            'game_started': '🎉 Son Harf Oyunu başladı! İlk kelime: **{word}**',
            'game_info': '📝 Son Harf Oyunu\n\n'
                        '• Oyunun amacı: Son harfi önceki kelimenin son harfiyle başlayan bir kelime söylemek.\n'
                        '• Herkes sırayla kelime söyleyecek.\n'
                        '• Bir kelimeyi tekrar söyleyemezsin.\n'
                        '• Oyunu durdurmak için `/sonharf durdur` komutunu kullanabilirsin.\n\n'
                        'İlk kelime: **{word}**',
            'game_stopped': '🛑 Son Harf Oyunu durduruldu.',
            'not_active': '🚫 Son Harf Oyunu şu anda aktif değil.',
            'already_active': '🚫 Son Harf Oyunu zaten aktif.',
            'wrong_start_letter': '🚫 Yanlış başlangıç harfi! Önceki kelimenin son harfi **{word}** olmalı.',
            'word_used': '🚫 Bu kelime daha önce kullanıldı!',
            'same_user': '🚫 Aynı kullanıcı iki kere kelime söyleyemez!'
        }
    },
    'en': {
        'info': {
            'title': '🤖 Tomris Bot',
            'description': 'A versatile Discord bot equipped with advanced moderation features and fun games to help you manage your server safely.',
            'server_count': 'Server Count',
            'user_count': 'User Count',
            'command_count': 'Command Count',
            'features_title': '✨ Features',
            'features': '🛡️ **Moderation Commands**\n'
                       '• Advanced server management\n'
                       '• User management (ban, kick)\n'
                       '• Channel management and cleanup\n\n'
                       '🎮 **Fun and Economy**\n'
                       '• Daily rewards and economy system\n'
                       '• Slot machine and gambling games\n'
                       '• Level system and rewards',
            'developer': '👨‍💻 Developer',
            'developer_info': '• **Vai**\n'
                            '• [X (Twitter) Profile](https://x.com/kayapater)\n'
                            '• Discord: kayapater\n'
                            '• [Website](https://kayapater.com.tr)',
            'support': '🔗 Links',
            'support_link': '• [Support Server](https://discord.gg/2RTHvbfH3a)',
            'footer': 'Tomris Bot • Safe and Powerful Management'
        },
        'commands': {
            'title': '📚 Tomris Bot Commands',
            'description': 'Here are all the commands you can use:',
            'mod_title': '🛡️ Moderation Commands',
            'mod_cmds': '• `/ban <user>` - Ban a user\n'
                       '• `/unban <user_id>` - Unban a user\n'
                       '• `/kick <user>` - Kick a user\n'
                       '• `/clear <amount>` - Clear specified number of messages\n'
                       '• `/lock` - Lock the channel\n'
                       '• `/unlock` - Unlock the channel',
            'economy_title': '💰 Economy Commands',
            'economy_cmds': '• `/daily` - Claim your daily reward\n'
                          '• `/balance` - View your balance',
            'games_title': '🎮 Game Commands',
            'games_cmds': '• `/coinflip <amount>` - Flip a coin (2x win)\n'
                           '• `/slots <amount>` - Play slot machine (1x-10x win)\n'
                           '• `/blackjack <amount>` - Play blackjack (2x win)\n'
                           '• `/roulette <amount> <bet_type> [number]` - Play roulette\n'
                           '  - Color/even-odd/high-low: 2x win\n'
                           '  - Number: 35x win\n'
                           '• `/sonharf <action> [first_word]` - Play Word Chain Game',
            'level_title': '📊 Level System',
            'level_cmds': '• `/rank [user]` - View level information\n'
                        '• `/levels` - View server level leaderboard',
            'utility_title': '🛠️ Utility Commands',
            'utility_cmds': '• `/weather <city>` - Show weather information\n'
                          '• `/poll <question> [options]` - Create a poll',
            'settings_title': '⚙️ Other Commands',
            'settings_cmds': '• `/profile [user]` - View your profile\n'
                           '• `/language <lang>` - Change bot language (tr/en)\n'
                           '• `/timezone <timezone>` - Set your timezone\n'
                           '• `/ping` - Check bot latency\n'
                           '• `/info` - Get bot information\n'
                           '• `/commands` - View this command list',
            'footer': 'Tomris Bot • Help and Commands'
        },
        'level': {
            'rank_title': '📊 Level Information',
            'level': 'Level',
            'xp': 'XP',
            'rank': 'Rank',
            'progress': 'Progress',
            'next_level': 'Next level',
            'leaderboard_title': '📊 Level Leaderboard',
            'no_data': 'No level data found yet.'
        },
        'reminder': {
            'set_success': '⏰ Reminder set! I will remind you on **{time}**.',
            'list_title': '⏰ Your Reminders',
            'no_reminders': 'You have no active reminders.',
            'delete_success': 'Reminder successfully deleted.',
            'delete_fail': 'Reminder not found or does not belong to you.',
            'reminder_time': 'Reminder Time',
            'time_format_error': 'Invalid time format. Example: 1h, 30m, 1d, etc.'
        },
        'music': {
            'joined': '🎵 Joined the voice channel.',
            'not_in_voice': 'You need to be in a voice channel!',
            'added_to_queue': '**{song}** added to the queue.',
            'now_playing': '🎵 Now playing: **{song}**',
            'queue_title': '🎵 Music Queue',
            'queue_empty': 'The queue is empty.',
            'skipped': '⏭️ Song skipped.',
            'stopped': '⏹️ Music stopped.',
            'paused': '⏸️ Music paused.',
            'resumed': '▶️ Music resumed.',
            'not_playing': 'No music is currently playing.',
            'playlist_created': '✅ Playlist **{name}** created.',
            'playlist_exists': 'A playlist with this name already exists.',
            'playlist_added': '✅ Song **{song}** added to playlist **{playlist}**.',
            'playlist_loaded': '✅ Playlist **{name}** added to queue.',
            'playlist_deleted': '✅ Playlist **{name}** deleted.',
            'no_playlists': 'You have no playlists.',
            'playlists_title': '🎵 Your Playlists',
            'playlist_songs_title': '🎵 Playlist **{name}**'
        },
        'custom_cmd': {
            'added': '✅ Command `/{name}` successfully added.',
            'deleted': '✅ Command `/{name}` successfully deleted.',
            'list_title': '📝 Custom Commands',
            'no_commands': 'There are no custom commands in this server.',
            'not_found': 'Command not found.',
            'already_exists': 'A command with this name already exists.'
        },
        'weather': {
            'title': '🌤️ Weather in {city}',
            'temperature': 'Temperature',
            'feels_like': 'Feels like',
            'humidity': 'Humidity',
            'wind': 'Wind',
            'pressure': 'Pressure',
            'not_found': 'City not found.',
            'error': 'Could not get weather information.'
        },
        'poll': {
            'title': '📊 Poll: {question}',
            'vote': 'Use the reactions below to vote.',
            'created_by': 'Created by: {user}',
            'no_options': 'You must specify at least 2 options.',
            'too_many_options': 'You can specify at most 10 options.'
        },
        'son_harf': {
            'game_started': '🎉 Word Chain Game started! First word: **{word}**',
            'game_info': '📝 Word Chain Game\n\n'
                        '• The goal of the game is to say a word that starts with the last letter of the previous word.\n'
                        '• Everyone will say a word in turn.\n'
                        '• You cannot repeat a word.\n'
                        '• To stop the game, use the `/sonharf stop` command.\n\n'
                        'First word: **{word}**',
            'game_stopped': '🛑 Word Chain Game stopped.',
            'not_active': '🚫 Word Chain Game is not currently active.',
            'already_active': '🚫 Word Chain Game is already active.',
            'wrong_start_letter': '🚫 Wrong starting letter! The first letter must be the last letter of the previous word **{word}**.',
            'word_used': '🚫 This word has already been used!',
            'same_user': '🚫 The same user cannot say two words in a row!'
        }
    }
}

COMMON_TIMEZONES = [
    app_commands.Choice(name="İstanbul (Türkiye)", value="Europe/Istanbul"),
    app_commands.Choice(name="Londra (İngiltere)", value="Europe/London"),
    app_commands.Choice(name="Berlin (Almanya)", value="Europe/Berlin"),
    app_commands.Choice(name="Paris (Fransa)", value="Europe/Paris"),
    app_commands.Choice(name="Moskova (Rusya)", value="Europe/Moscow"),
    app_commands.Choice(name="Dubai (BAE)", value="Asia/Dubai"),
    app_commands.Choice(name="New York (ABD)", value="America/New_York"),
    app_commands.Choice(name="Los Angeles (ABD)", value="America/Los_Angeles"),
    app_commands.Choice(name="Tokyo (Japonya)", value="Asia/Tokyo"),
    app_commands.Choice(name="Sydney (Avustralya)", value="Australia/Sydney"),
    app_commands.Choice(name="UTC", value="UTC"),
]

@bot.tree.command(name="info", description="Bot information / Bot bilgileri")
async def info(interaction: discord.Interaction):

    lang = 'tr'  
    if interaction.guild:
        lang = db.get_server_language(interaction.guild.id)
    

    t = TRANSLATIONS[lang]['info']
    

    server_count = len(bot.guilds)
    user_count = len(set(bot.get_all_members()))
    command_count = len(bot.tree.get_commands())
    

    embed = discord.Embed(
        title=t['title'],
        description=t['description'],
        color=discord.Color.blue()
    )
    

    embed.add_field(name=t['server_count'], value=str(server_count), inline=True)
    embed.add_field(name=t['user_count'], value=str(user_count), inline=True)
    embed.add_field(name=t['command_count'], value=str(command_count), inline=True)

    embed.add_field(name=t['features_title'], value=t['features'], inline=False)

    embed.add_field(name=t['developer'], value=t['developer_info'], inline=False)

    embed.add_field(name=t['support'], value=t['support_link'], inline=False)
    

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    embed.set_footer(text=t['footer'])
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="commands", description="Komut listesi")
async def commands(interaction: discord.Interaction):
    lang = db.get_server_language(interaction.guild_id)
    texts = TRANSLATIONS[lang]['commands']
    
    embed = discord.Embed(
        title=texts['title'],
        description=texts['description'],
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name=texts['mod_title'],
        value=texts['mod_cmds'],
        inline=False
    )
    

    embed.add_field(
        name=texts['economy_title'],
        value=texts['economy_cmds'],
        inline=False
    )
    

    embed.add_field(
        name=texts['games_title'],
        value=texts['games_cmds'],
        inline=False
    )
    

    embed.add_field(
        name=texts['level_title'],
        value=texts['level_cmds'],
        inline=False
    )
    

    embed.add_field(
        name=texts['utility_title'],
        value=texts['utility_cmds'],
        inline=False
    )
    

    embed.add_field(
        name=texts['settings_title'],
        value=texts['settings_cmds'],
        inline=False
    )
    
    embed.set_footer(text=texts['footer'])
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="language", description="Bot dilini değiştirir")
@app_commands.describe(language="Dil seçeneği (tr/en)")
@app_commands.choices(language=[
    app_commands.Choice(name="Türkçe", value="tr"),
    app_commands.Choice(name="English", value="en")
])
async def language(interaction: discord.Interaction, language: str):
    if not interaction.user.guild_permissions.manage_guild:
        if language == "tr":
            await interaction.response.send_message("Bu komutu kullanmak için 'Sunucuyu Yönet' yetkisine sahip olmalısınız!", ephemeral=True)
        else:
            await interaction.response.send_message("You need 'Manage Server' permission to use this command!", ephemeral=True)
        return

    try:
        db.set_server_language(interaction.guild_id, language)
        
        if language == "tr":
            await interaction.response.send_message("✅ Bot dili Türkçe olarak ayarlandı!", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Bot language has been set to English!", ephemeral=True)
    except Exception as e:
        if language == "tr":
            await interaction.response.send_message(f"❌ Bir hata oluştu: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="ban", description="Bir kullanıcıyı yasaklar")
@app_commands.describe(
    user="Yasaklanacak kullanıcı",
    user_id="Yasaklanacak kullanıcının ID'si (isteğe bağlı)",
    reason="Yasaklama sebebi"
)
@is_admin()
async def ban(
    interaction: discord.Interaction, 
    user: discord.Member = None,
    user_id: str = None,
    reason: str = None
):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    if user is None and user_id is None:
        await interaction.response.send_message("Bir kullanıcı veya kullanıcı ID'si belirtmelisiniz!", ephemeral=True)
        return
    
    try:
      
        if user_id is not None:
            try:
                user_id = int(user_id)

                user = await bot.fetch_user(user_id)
            except ValueError:
                await interaction.response.send_message("Geçersiz kullanıcı ID'si!", ephemeral=True)
                return
            except discord.NotFound:
                await interaction.response.send_message("Bu ID'ye sahip bir kullanıcı bulunamadı!", ephemeral=True)
                return
        

        if isinstance(user, discord.Member) and user.id == interaction.guild.owner_id:
            await interaction.response.send_message("Sunucu sahibini yasaklayamazsınız!", ephemeral=True)
            return
        

        if not interaction.guild.me.top_role > user.top_role:
            await interaction.response.send_message("Bu kullanıcıyı yasaklayamam çünkü rolü benim rolümden yüksek veya eşit!", ephemeral=True)
            return
            
        if not interaction.user.top_role > user.top_role:
            await interaction.response.send_message("Bu kullanıcıyı yasaklayamazsınız çünkü rolü sizin rolünüzden yüksek veya eşit!", ephemeral=True)
            return
        

        await interaction.response.defer()
        
        try:

            await interaction.guild.ban(user, reason=f"{reason} (Yasaklayan: {interaction.user})")

            await interaction.followup.send(f"✅ {user.mention} sunucudan yasaklandı.")
        except discord.Forbidden:
            await interaction.followup.send("Bu kullanıcıyı yasaklamak için yetkim yok!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)
            
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@bot.tree.command(name="unban", description="Bir kullanıcının yasağını kaldırır")
@app_commands.describe(
    user_id="Yasağı kaldırılacak kullanıcının ID'si"
)
@is_admin()
async def unban(interaction: discord.Interaction, user_id: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    try:

        try:
            user_id = int(user_id)
            user = await bot.fetch_user(user_id)
        except ValueError:
            await interaction.response.send_message("Geçersiz kullanıcı ID'si!", ephemeral=True)
            return
        except discord.NotFound:
            await interaction.response.send_message("Bu ID'ye sahip bir kullanıcı bulunamadı!", ephemeral=True)
            return
        

        try:
            ban_entry = await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.response.send_message("Bu kullanıcı zaten yasaklı değil!", ephemeral=True)
            return
        

        await interaction.response.defer()
        
        try:

            await interaction.guild.unban(user, reason=f"Yasağı Kaldıran: {interaction.user}")

            await interaction.followup.send(f"✅ {user.mention} kullanıcısının yasağı kaldırıldı.")
        except discord.Forbidden:
            await interaction.followup.send("Bu kullanıcının yasağını kaldırmak için yetkim yok!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)
            
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@bot.tree.command(name="kick", description="Bir kullanıcıyı sunucudan atar")
@app_commands.describe(
    user="Atılacak kullanıcı",
    user_id="Atılacak kullanıcının ID'si (isteğe bağlı)",
    reason="Atılma sebebi"
)
@is_admin()
async def kick(
    interaction: discord.Interaction,
    user: discord.Member = None,
    user_id: str = None,
    reason: str = None
):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    if user is None and user_id is None:
        await interaction.response.send_message("Bir kullanıcı veya kullanıcı ID'si belirtmelisiniz!", ephemeral=True)
        return
    
    try:

        if user_id is not None:
            try:
                user_id = int(user_id)

                user = interaction.guild.get_member(user_id)
                if user is None:
                    await interaction.response.send_message("Bu ID'ye sahip kullanıcı sunucuda bulunamadı!", ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message("Geçersiz kullanıcı ID'si!", ephemeral=True)
                return
        

        if user.id == interaction.guild.owner_id:
            await interaction.response.send_message("Sunucu sahibini atamazsınız!", ephemeral=True)
            return
        

        if not interaction.guild.me.top_role > user.top_role:
            await interaction.response.send_message("Bu kullanıcıyı atamam çünkü rolü benim rolümden yüksek veya eşit!", ephemeral=True)
            return
        
        if not interaction.user.top_role > user.top_role:
            await interaction.response.send_message("Bu kullanıcıyı atamazsınız çünkü rolü sizin rolünüzden yüksek veya eşit!", ephemeral=True)
            return
        

        await interaction.response.defer()
        
        try:

            await user.kick(reason=f"{reason} (Atan: {interaction.user})")

            await interaction.followup.send(f"✅ {user.mention} sunucudan atıldı.")
        except discord.Forbidden:
            await interaction.followup.send("Bu kullanıcıyı atmak için yetkim yok!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)
            
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@bot.tree.command(name="clear", description="Belirtilen sayıda mesajı siler")
@app_commands.describe(amount="Silinecek mesaj sayısı (1-100)")
@is_admin()
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    if amount < 1 or amount > 100:
        await interaction.response.send_message("1 ile 100 arasında bir sayı belirtmelisiniz!", ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"{len(deleted)} mesaj silindi.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("Mesajları silmek için yetkim yok!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@bot.tree.command(name="lock", description="Kanalı kilitler")
@is_admin()
async def lock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("Kanal kilitlendi! 🔒")
    except discord.Forbidden:
        await interaction.response.send_message("Kanalı kilitlemek için yetkim yok!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)

@bot.tree.command(name="unlock", description="Kanalın kilidini açar")
@is_admin()
async def unlock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Bu komutu kullanmak için yetkiniz yok!", ephemeral=True)
        return
    
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message("Kanalın kilidi açıldı! 🔓")
    except discord.Forbidden:
        await interaction.response.send_message("Kanalın kilidini açmak için yetkim yok!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Bir hata oluştu: {str(e)}", ephemeral=True)


@bot.tree.command(name="daily", description="Günlük ödülünü al")
async def daily(interaction: discord.Interaction):
    user_data = db.get_user_economy(interaction.user.id)
    tz = user_data.get('timezone', 'Europe/Istanbul')
    if user_data['last_daily']:
        last_daily = datetime.fromisoformat(user_data['last_daily'])
        last_daily = to_user_timezone(last_daily, interaction.user.id)
        next_daily = last_daily + timedelta(days=1)
        now = to_user_timezone(datetime.utcnow(), interaction.user.id)
        if now < next_daily:
            remaining = next_daily - now
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await interaction.response.send_message(
                f"Günlük ödülünü zaten aldın! Yeniden alabilmek için {hours} saat {minutes} dakika beklemelisin.",
                ephemeral=True
            )
            return
    

    coins = random.randint(300, 500)
    db.update_coins(interaction.user.id, coins)
    db.update_last_daily(interaction.user.id)
    
    await interaction.response.send_message(
        f"🎉 Günlük ödülün: **{coins}** coin!",
        ephemeral=True
    )

@bot.tree.command(name="balance", description="Coin bakiyeni görüntüle")
async def balance(interaction: discord.Interaction):
    user_data = db.get_user_economy(interaction.user.id)
    
    await interaction.response.send_message(
        f"💰 Bakiyen: **{user_data['coins']}** coin",
        ephemeral=True
    )


@bot.tree.command(name="coinflip", description="Yazı tura at ve coin kazan")
@app_commands.describe(amount="Yatırmak istediğin coin miktarı")
async def coinflip(interaction: discord.Interaction, amount: int):
    if amount < 10:
        await interaction.response.send_message(
            "En az 10 coin yatırmalısın!",
            ephemeral=True
        )
        return
    
    user_data = db.get_user_economy(interaction.user.id)
    if user_data['coins'] < amount:
        await interaction.response.send_message(
            f"Yeterli coinin yok! Bakiyen: {user_data['coins']} coin",
            ephemeral=True
        )
        return
    

    db.update_coins(interaction.user.id, -amount)
    

    result = random.choice(["👑 YAZI", "🌟 TURA"])
    choice = random.choice(["👑 YAZI", "🌟 TURA"])
    
    if result == choice:  
        winnings = amount * 2
        db.update_coins(interaction.user.id, winnings)
        await interaction.response.send_message(
            f"🎲 **Yazı Tura**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n"
            f"Seçim: {choice}\n"
            f"Sonuç: {result}\n\n"
            f"🎉 Kazandı! **{winnings}** coin!"
        )
    else: 
        await interaction.response.send_message(
            f"🎲 **Yazı Tura**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n"
            f"Seçim: {choice}\n"
            f"Sonuç: {result}\n\n"
            f"😔 Kaybetti! **{amount}** coin kaybetti!"
        )

@bot.tree.command(name="slots", description="Slot makinesi oyna")
@app_commands.describe(amount="Yatırılacak coin miktarı")
async def slots(interaction: discord.Interaction, amount: int):
    if amount < 10:
        await interaction.response.send_message(
            "En az 10 coin yatırmalısın!",
            ephemeral=True
        )
        return
    
    user_data = db.get_user_economy(interaction.user.id)
    if user_data['coins'] < amount:
        await interaction.response.send_message(
            f"Yeterli coininiz yok! Bakiyeniz: {user_data['coins']} coin",
            ephemeral=True
        )
        return
    

    db.update_coins(interaction.user.id, -amount)
    

    symbols = {
        "💎": {"chance": 5, "multiplier": 10},
        "🎰": {"chance": 10, "multiplier": 5},
        "7️⃣": {"chance": 15, "multiplier": 3},
        "🍀": {"chance": 20, "multiplier": 2},
        "🎲": {"chance": 50, "multiplier": 1}
    }
    

    slots = []
    weights = [s["chance"] for s in symbols.values()]
    for _ in range(3):
        symbol = random.choices(list(symbols.keys()), weights=weights, k=1)[0]
        slots.append(symbol)
    

    if len(set(slots)) == 1:  
        symbol = slots[0]
        multiplier = symbols[symbol]["multiplier"]
        winnings = amount * multiplier
        db.update_coins(interaction.user.id, winnings)
        
        await interaction.response.send_message(
            f"🎰 **Slot Makinesi**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
            f"[ {' | '.join(slots)} ]\n\n"
            f"🎉 Jackpot! **{winnings}** coin kazandı!"
        )
    else:
        await interaction.response.send_message(
            f"🎰 **Slot Makinesi**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
            f"[ {' | '.join(slots)} ]\n\n"
            f"😔 **{amount}** coin kaybetti!"
        )

class BlackjackView(discord.ui.View):
    def __init__(self, player_id: int):
        super().__init__(timeout=30)
        self.player_id = player_id
        self.value = None
    
    @discord.ui.button(label="Hit 👊", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Bu oyun sizin değil!", ephemeral=True)
            return
        self.value = "hit"
        self.stop()
    
    @discord.ui.button(label="Stand 🛑", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Bu oyun sizin değil!", ephemeral=True)
            return
        self.value = "stand"
        self.stop()

@bot.tree.command(name="blackjack", description="Blackjack oyna")
@app_commands.describe(amount="Yatırmak istediğin coin miktarı")
async def blackjack(interaction: discord.Interaction, amount: int):

    user_data = db.get_user_economy(interaction.user.id)
    
    if amount <= 0:
        await interaction.response.send_message(
            "Geçerli bir bahis miktarı girin!",
            ephemeral=True
        )
        return
    
    if amount > user_data['coins']:
        await interaction.response.send_message(
            f"Yeterli coininiz yok! Bakiyeniz: {user_data['coins']} coin",
            ephemeral=True
        )
        return
    

    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4
    random.shuffle(cards)
    

    player_hand = [cards.pop(), cards.pop()]
    dealer_hand = [cards.pop(), "?"]
    dealer_hidden = cards.pop()
    
    def calculate_hand(hand):
        value = 0
        aces = 0
        
        for card in hand:
            if card == "?":
                continue
            elif card == "A":
                aces += 1
            elif card in ["J", "Q", "K"]:
                value += 10
            else:
                value += int(card)
        
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        
        return value
    
    view = BlackjackView(interaction.user.id)
    

    await interaction.response.send_message(
        f"🎲 **Blackjack**\n\n"
        f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
        f"Elin: {' '.join(player_hand)} ({calculate_hand(player_hand)})\n"
        f"Krupiyenin eli: {' '.join(dealer_hand)}",
        view=view
    )
    
    while calculate_hand(player_hand) < 21:
        await view.wait()
        if view.value is None:  
            await interaction.edit_original_response(
                content=f"🎲 **Blackjack**\n\n"
                        f"{interaction.user.mention}\n\n"
                        "⏰ Süre doldu! Oyun iptal edildi.",
                view=None
            )
            return
        
        if view.value == "hit":
      
            player_hand.append(cards.pop())
            
            if calculate_hand(player_hand) > 21:
                db.update_coins(interaction.user.id, -amount)
                await interaction.edit_original_response(
                    content=f"🎲 **Blackjack**\n\n"
                            f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                            f"Elin: {' '.join(player_hand)} ({calculate_hand(player_hand)})\n"
                            f"Krupiyenin eli: {dealer_hidden} {dealer_hand[1]} ({calculate_hand([dealer_hidden, dealer_hand[1]])})\n\n"
                            "💥 Bust! **Kaybettin!**",
                    view=None
                )
                return
            
            view = BlackjackView(interaction.user.id)
            await interaction.edit_original_response(
                content=f"🎲 **Blackjack**\n\n"
                        f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                        f"Elin: {' '.join(player_hand)} ({calculate_hand(player_hand)})\n"
                        f"Krupiyenin eli: {' '.join(dealer_hand)}",
                view=view
            )
        else:  
            break
    

    dealer_hand[1] = dealer_hidden
    await interaction.edit_original_response(
        content=f"🎲 **Blackjack**\n\n"
                f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                f"Elin: {' '.join(player_hand)} ({calculate_hand(player_hand)})\n"
                f"Krupiyenin eli: {' '.join(dealer_hand)} ({calculate_hand(dealer_hand)})"
    )
    

    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(cards.pop())
        await interaction.edit_original_response(
            content=f"🎲 **Blackjack**\n\n"
                    f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                    f"Elin: {' '.join(player_hand)} ({calculate_hand(player_hand)})\n"
                    f"Krupiyenin eli: {' '.join(dealer_hand)} ({calculate_hand(dealer_hand)})"
        )
        await asyncio.sleep(1)
    

    player_value = calculate_hand(player_hand)
    dealer_value = calculate_hand(dealer_hand)
    
    if dealer_value > 21:
        db.update_coins(interaction.user.id, amount)
        await interaction.edit_original_response(
            content=f"🎲 **Blackjack**\n\n"
                    f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                    f"Elin: {' '.join(player_hand)} ({player_value})\n"
                    f"Krupiyenin eli: {' '.join(dealer_hand)} ({dealer_value})\n\n"
                    f"🎉 Krupiyer bust! **{amount}** coin kazandın!"
        )
    elif player_value > dealer_value:
        db.update_coins(interaction.user.id, amount)
        await interaction.edit_original_response(
            content=f"🎲 **Blackjack**\n\n"
                    f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                    f"Elin: {' '.join(player_hand)} ({player_value})\n"
                    f"Krupiyenin eli: {' '.join(dealer_hand)} ({dealer_value})\n\n"
                    f"🎉 Kazandın! **{amount}** coin kazandın!"
        )
    elif player_value < dealer_value:
        db.update_coins(interaction.user.id, -amount)
        await interaction.edit_original_response(
            content=f"🎲 **Blackjack**\n\n"
                    f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                    f"Elin: {' '.join(player_hand)} ({player_value})\n"
                    f"Krupiyenin eli: {' '.join(dealer_hand)} ({dealer_value})\n\n"
                    "😔 Kaybettin!"
        )
    else:
        await interaction.edit_original_response(
            content=f"🎲 **Blackjack**\n\n"
                    f"{interaction.user.mention} bahis: **{amount}** coin\n\n"
                    f"Elin: {' '.join(player_hand)} ({player_value})\n"
                    f"Krupiyenin eli: {' '.join(dealer_hand)} ({dealer_value})\n\n"
                    "🤝 Berabere! Bahsini geri aldın."
        )

@bot.tree.command(name="roulette", description="Rulet oyna")
@app_commands.describe(
    amount="Yatırmak istediğin coin miktarı",
    bet_type="Bahis türü (red/black/even/odd/high/low/number)",
    number="Sayı seçimi (0-36, sadece number bahis türünde gerekli)"
)
async def roulette(interaction: discord.Interaction, amount: int, bet_type: str, number: int = None):
    if amount < 10:
        await interaction.response.send_message(
            "En az 10 coin yatırmalısın!",
            ephemeral=True
        )
        return
    
    user_data = db.get_user_economy(interaction.user.id)
    if user_data['coins'] < amount:
        await interaction.response.send_message(
            f"Yeterli coinin yok! Bakiyen: {user_data['coins']} coin",
            ephemeral=True
        )
        return
    

    valid_bets = ["red", "black", "even", "odd", "high", "low", "number"]
    if bet_type not in valid_bets:
        await interaction.response.send_message(
            f"Geçersiz bahis türü! Kullanılabilir türler: {', '.join(valid_bets)}",
            ephemeral=True
        )
        return
    
    if bet_type == "number" and (number is None or number < 0 or number > 36):
        await interaction.response.send_message(
            "Sayı bahisi için 0-36 arası bir sayı seçmelisin!",
            ephemeral=True
        )
        return
    

    db.update_coins(interaction.user.id, -amount)
    

    result = random.randint(0, 36)
    

    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    

    won = False
    multiplier = 0
    
    if bet_type == "red" and result in red_numbers:
        won = True
        multiplier = 2
    elif bet_type == "black" and result in black_numbers:
        won = True
        multiplier = 2
    elif bet_type == "even" and result != 0 and result % 2 == 0:
        won = True
        multiplier = 2
    elif bet_type == "odd" and result % 2 == 1:
        won = True
        multiplier = 2
    elif bet_type == "high" and result >= 19:
        won = True
        multiplier = 2
    elif bet_type == "low" and result >= 1 and result <= 18:
        won = True
        multiplier = 2
    elif bet_type == "number" and result == number:
        won = True
        multiplier = 35
    

    color = "🔴" if result in red_numbers else "⚫" if result in black_numbers else "🟢"
    if won:
        winnings = amount * multiplier
        db.update_coins(interaction.user.id, winnings)
        await interaction.response.send_message(
            f"🎲 **Rulet**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n"
            f"Bahis türü: {bet_type.upper()}{f' ({number})' if bet_type == 'number' else ''}\n"
            f"Sonuç: {color} {result}\n\n"
            f"🎉 Kazandı! **{winnings}** coin!"
        )
    else:
        await interaction.response.send_message(
            f"🎲 **Rulet**\n\n"
            f"{interaction.user.mention} bahis: **{amount}** coin\n"
            f"Bahis türü: {bet_type.upper()}{f' ({number})' if bet_type == 'number' else ''}\n"
            f"Sonuç: {color} {result}\n\n"
            f"😔 Kaybetti! **{amount}** coin kaybetti!"
        )


@bot.tree.command(name="ping", description="Bot latency / Bot gecikmesi")
async def ping(interaction: discord.Interaction):
    try:

        ws_latency = round(bot.latency * 1000)
        

        before = time.monotonic()
        await interaction.response.defer()
        after = time.monotonic()
        api_latency = round((after - before) * 1000)
        

        def get_status_emoji(ms):
            if ms <= 50:
                return "🟢"  
            elif ms <= 100:
                return "🟡"  
            else:
                return "🔴"  
        

        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.purple()
        )
        

        embed.add_field(
            name="WebSocket Gecikmesi",
            value=f"{get_status_emoji(ws_latency)} **{ws_latency}ms**",
            inline=True
        )
        embed.add_field(
            name="API Gecikmesi",
            value=f"{get_status_emoji(api_latency)} **{api_latency}ms**",
            inline=True
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Ping Error: {str(e)}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Ping hesaplanırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
                ephemeral=True
            )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Bu komutu çok sık kullanıyorsun! {error.retry_after:.2f} saniye sonra tekrar dene.",
                ephemeral=True
            )
            return
            
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Bu komutu kullanmak için yeterli yetkiye sahip değilsin!",
                ephemeral=True
            )
            return
        

        print(f"Uygulama komutu hatası: {str(error)}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
                ephemeral=True
            )
    except Exception as e:
        print(f"Hata yakalayıcı hatası: {str(e)}")

@bot.tree.command(name="profile", description="View user profile / Kullanıcı profilini görüntüle")
async def profile(interaction: discord.Interaction, user: discord.User = None):
    try:

        target_user = user if user else interaction.user
        user_data = db.get_user_economy(target_user.id)
        coins = user_data.get('coins', 0) if user_data else 0
        last_daily = user_data.get('last_daily', None) if user_data else None
        tz = user_data.get('timezone', 'Europe/Istanbul')
        embed = discord.Embed(
            title=f"👤 {target_user.name}'in Profili",
            color=discord.Color.purple()
        )
        embed.add_field(name="💰 Coin", value=str(coins), inline=True)
        if last_daily:
            try:
                last_daily_dt = datetime.fromisoformat(last_daily)
                last_daily_dt = to_user_timezone(last_daily_dt, target_user.id)
                last_daily_str = last_daily_dt.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                last_daily_str = "Bilinmiyor"
        else:
            last_daily_str = "Hiç kullanılmadı"
        embed.add_field(name="🎁 Son Daily", value=last_daily_str, inline=True)
        embed.add_field(name="🌍 Zaman Dilimi", value=tz, inline=True)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"Profile Error: {str(e)}")
        await interaction.response.send_message("Profil görüntülenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.", ephemeral=True)

@bot.tree.command(name="timezone", description="Set your timezone / Zaman dilimini ayarla")
@app_commands.describe(tz="Time zone (e.g. Europe/Istanbul)")
@app_commands.choices(tz=COMMON_TIMEZONES)
async def timezone(interaction: discord.Interaction, tz: str):
    if tz in [choice.value for choice in COMMON_TIMEZONES]:
        timezone_value = tz
    elif tz in all_timezones:
        timezone_value = tz
    else:
        await interaction.response.send_message(
            "Geçersiz zaman dilimi! Lütfen listeden seçin veya geçerli bir zaman dilimi girin (örn: Europe/Istanbul).", 
            ephemeral=True
        )
        return
    
    db.create_user_economy(interaction.user.id)
    db.set_user_timezone(interaction.user.id, timezone_value)
    await interaction.response.send_message(f"Zaman diliminiz başarıyla ayarlandı: {timezone_value}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot olarak giriş yapıldı: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print(f'Discord.py Sürümü: {discord.__version__}')
    print(f'Python Sürümü: {platform.python_version()}')
    
    try:
        print("Komutlar senkronize ediliyor...")
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi!")
    except Exception as e:
        print(f"Komut senkronizasyonunda hata: {e}")
    
    try:
        from sonharf import SonHarfCog
        await bot.add_cog(SonHarfCog(bot, db, TRANSLATIONS))
        print("Son Harf oyunu yüklendi!")
    except Exception as e:
        print(f"Son Harf oyunu yüklenirken hata: {e}")
    
    print('Bot hazır!')

@bot.event
async def on_message(message):

    if message.author.bot or not message.guild:
        return
    

    xp_amount = random.randint(5, 15)
    level_up, new_level = db.add_xp(message.author.id, message.guild.id, xp_amount)
    

    if level_up:
        lang = db.get_server_language(message.guild.id)
        t = TRANSLATIONS[lang]['level']
        
        embed = discord.Embed(
            title=f"🎉 {t['level']} {new_level}!",
            description=f"{message.author.mention} {t['level'].lower()} {new_level} oldu!",
            color=discord.Color.green()
        )
        
        await message.channel.send(embed=embed)
    

    await bot.process_commands(message)


@bot.tree.command(name="rank", description="View your or someone else's level / Seviye bilgilerini görüntüle")
async def rank(interaction: discord.Interaction, user: discord.User = None):

    target_user = user or interaction.user
    

    lang = 'tr'
    if interaction.guild:
        lang = db.get_server_language(interaction.guild.id)
    

    t = TRANSLATIONS[lang]['level']
    

    level_data = db.get_user_level(target_user.id, interaction.guild.id)
    

    xp_progress = level_data['xp'] % 100  
    progress_bar_length = 20
    filled_length = int(progress_bar_length * (xp_progress / 100))
    progress_bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    
    embed = discord.Embed(
        title=t['rank_title'],
        description=f"{target_user.mention}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name=t['level'], value=str(level_data['level']), inline=True)
    embed.add_field(name=t['xp'], value=f"{level_data['xp']}/{level_data['next_level_xp']}", inline=True)
    embed.add_field(name=t['progress'], value=f"{progress_bar} {xp_progress}%", inline=False)
    
    embed.set_thumbnail(url=target_user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="levels", description="View server level leaderboard / Sunucu seviye sıralamasını görüntüle")
async def levels(interaction: discord.Interaction):
    lang = 'tr'
    if interaction.guild:
        lang = db.get_server_language(interaction.guild.id)
    
    t = TRANSLATIONS[lang]['level']
    
    leaderboard = db.get_server_leaderboard(interaction.guild.id)
    
    if not leaderboard:
        await interaction.response.send_message(t['no_data'], ephemeral=True)
        return
    
    embed = discord.Embed(
        title=t['leaderboard_title'],
        color=discord.Color.gold()
    )
    
    description = ""
    for i, (user_id, xp, level) in enumerate(leaderboard, 1):
        user = interaction.guild.get_member(user_id)
        username = user.display_name if user else f"User {user_id}"
        description += f"**{i}.** {username} - {t['level']} {level} ({xp} XP)\n"
    
    embed.description = description
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="weather", description="Show weather information for a city / Bir şehrin hava durumunu göster")
async def weather(interaction: discord.Interaction, city: str):
    lang = 'tr'
    if interaction.guild:
        lang = db.get_server_language(interaction.guild.id)
    
    t = TRANSLATIONS[lang]['weather']
    
    api_key = os.getenv('WEATHER_API_KEY')
    
    if not api_key:
        await interaction.response.send_message("Hava durumu API anahtarı ayarlanmamış.", ephemeral=True)
        return
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang={lang[:2]}"
    
    try:
        async with bot.session.get(url) as response:
            if response.status != 200:
                await interaction.response.send_message(t['not_found'], ephemeral=True)
                return
            
            data = await response.json()
            
            weather_main = data['weather'][0]['main']
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            pressure = data['main']['pressure']
            
            icon_code = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            
            embed = discord.Embed(
                title=t['title'].format(city=data['name']),
                description=f"**{weather_main}** - {weather_desc}",
                color=discord.Color.blue()
            )
            
            embed.set_thumbnail(url=icon_url)
            
            embed.add_field(name=t['temperature'], value=f"{temp:.1f}°C", inline=True)
            embed.add_field(name=t['feels_like'], value=f"{feels_like:.1f}°C", inline=True)
            embed.add_field(name=t['humidity'], value=f"{humidity}%", inline=True)
            embed.add_field(name=t['wind'], value=f"{wind_speed} m/s", inline=True)
            embed.add_field(name=t['pressure'], value=f"{pressure} hPa", inline=True)
            
            await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        print(f"Hava durumu hatası: {e}")
        await interaction.response.send_message(t['error'], ephemeral=True)

class PollView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)  
        self.options = options
        self.votes = {i: 0 for i in range(len(options))}
        
        for i, option in enumerate(options):
            button = discord.ui.Button(
                label=f"{i+1}. {option}",
                custom_id=f"poll_{i}",
                style=discord.ButtonStyle.primary
            )
            button.callback = self.vote_callback
            self.add_item(button)
    
    async def vote_callback(self, interaction: discord.Interaction):
        option_index = int(interaction.data['custom_id'].split('_')[1])
        
        self.votes[option_index] += 1
        
        await interaction.response.send_message(f"Oyunuz kaydedildi: {self.options[option_index]}", ephemeral=True)

@bot.tree.command(name="poll", description="Create a poll / Anket oluştur")
@app_commands.describe(
    question="Poll question / Anket sorusu",
    options="Options separated by commas / Virgülle ayrılmış seçenekler"
)
async def poll(interaction: discord.Interaction, question: str, options: str):
    lang = 'tr'
    if interaction.guild:
        lang = db.get_server_language(interaction.guild.id)
    
    t = TRANSLATIONS[lang]['poll']
    
    option_list = [opt.strip() for opt in options.split(',') if opt.strip()]
    
    if len(option_list) < 2:
        await interaction.response.send_message(t['no_options'], ephemeral=True)
        return
    
    if len(option_list) > 10:
        await interaction.response.send_message(t['too_many_options'], ephemeral=True)
        return
    
    view = PollView(option_list)
    
    embed = discord.Embed(
        title=t['title'].format(question=question),
        description=t['vote'],
        color=discord.Color.blue()
    )
    
    for i, option in enumerate(option_list):
        embed.add_field(name=f"{i+1}. {option}", value="0 oy", inline=False)
    
    embed.set_footer(text=t['created_by'].format(user=interaction.user.display_name))
    
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı!")
    print(f"Bot {len(bot.guilds)} sunucuda aktif.")
    
    try:
        synced = await bot.tree.sync()
        print(f"Senkronize edilen komut sayısı: {len(synced)}")
    except Exception as e:
        print(f"Komut senkronizasyonunda hata: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if not message.guild:
        return
    
    await bot.process_commands(message)
    
    server_id = message.guild.id
    
    game_data = db.get_son_harf_game(server_id)
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
        error_msg = await message.channel.send(TRANSLATIONS[db.get_server_language(server_id)]['son_harf']['same_user'])
        await asyncio.sleep(3)
        await error_msg.delete()
        return
    
    if word[0] != current_word[-1]:
        await message.delete()
        error_msg = await message.channel.send(
            TRANSLATIONS[db.get_server_language(server_id)]['son_harf']['wrong_start_letter'].format(word=current_word)
        )
        await asyncio.sleep(3)
        await error_msg.delete()
        return
    
    used_words = game_data['used_words']
    if word in used_words:
        await message.delete()
        error_msg = await message.channel.send(TRANSLATIONS[db.get_server_language(server_id)]['son_harf']['word_used'])
        await asyncio.sleep(3)
        await error_msg.delete()
        return
    
    used_words.append(word)
    db.update_son_harf_game(server_id, word, message.author.id, used_words)
    
    await message.add_reaction('✅')

TURKISH_WORDS = [
    "araba", "balık", "ceviz", "deniz", "elma", "fare", "gemi", "harita", 
    "ışık", "kalem", "limon", "meyve", "nar", "orman", "pencere", "radyo", 
    "saat", "telefon", "uçak", "vazo", "yastık", "zaman", "çiçek", "şapka",
    "öğrenci", "üzüm", "ağaç", "bardak", "çanta", "defter", "ev", "fırın",
    "güneş", "halı", "ırmak", "jeton", "kitap", "lamba", "masa", "nehir",
    "otobüs", "para", "resim", "sandalye", "tabak", "uyku", "vatan", "yemek",
    "zemin", "çorap", "şeker", "ördek", "ütü", "ıhlamur", "ıspanak"
]

@bot.tree.command(name="sonharf", description="Son Harf Oyunu başlat veya durdur")
@app_commands.describe(
    action="İşlem (başlat/durdur/bilgi)",
    first_word="İlk kelime (sadece başlat işlemi için)"
)
@is_admin()
async def sonharf(
    interaction: discord.Interaction,
    action: str,
    first_word: str = None
):
    server_id = interaction.guild.id
    language = db.get_server_language(server_id)
    translations = TRANSLATIONS[language]['son_harf']
    
    if action.lower() == "başlat" or action.lower() == "start":
        game_data = db.get_son_harf_game(server_id)
        if game_data and game_data['active']:
            await interaction.response.send_message(translations['already_active'], ephemeral=True)
            return
        
        if not first_word:
            first_word = random.choice(TURKISH_WORDS)
        
        db.start_son_harf_game(server_id, interaction.channel_id, first_word)
        
        await interaction.response.send_message(
            translations['game_started'].format(word=first_word)
        )
        
        await interaction.channel.send(
            translations['game_info'].format(word=first_word)
        )
    
    elif action.lower() == "durdur" or action.lower() == "stop":
        game_data = db.get_son_harf_game(server_id)
        if not game_data or not game_data['active']:
            await interaction.response.send_message(translations['not_active'], ephemeral=True)
            return
        
        db.stop_son_harf_game(server_id)
        await interaction.response.send_message(translations['game_stopped'])
    
    elif action.lower() == "bilgi" or action.lower() == "info":
        game_data = db.get_son_harf_game(server_id)
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

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if not message.guild:
        return
    
    await bot.process_commands(message)

import pytz

def to_user_timezone(dt, user_id):
    user_tz = db.get_user_timezone(user_id)
    try:
        target_tz = pytz_timezone(user_tz)
    except Exception:
        target_tz = pytz_timezone('Europe/Istanbul')
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(target_tz)

if __name__ == "__main__":
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("Bot kapatılıyor...")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        traceback.print_exc()
