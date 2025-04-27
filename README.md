# Tomris Bot

<div align="center">
  <img src="https://cdn.discordapp.com/avatars/1058409614992998501/97a155914f17653702bb54c12d8950cc.webp?size=100" alt="Tomris Bot Logo" width="100"/>
  <br>
  <b>Çok yönlü, Türkçe ve İngilizce destekli Discord botu</b>
  <br>
  <br>
</div>

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Komutlar](#-komutlar)
- [Zaman Dilimi Desteği](#-zaman-dilimi-desteği)
- [Oyunlar](#-oyunlar)
- [Destek](#-destek)
- [Lisans](#-lisans)

## ✨ Özellikler

Tomris Bot, sunucunuzu yönetmenize yardımcı olan, eğlenceli oyunlar ve kullanışlı özelliklerle donatılmış çok yönlü bir Discord botudur.

- **🛡️ Moderasyon**: Kullanıcıları yasaklama, atma, mesaj silme ve kanal kilitleme gibi temel moderasyon özellikleri
- **💰 Ekonomi Sistemi**: Günlük ödüller ve bakiye takibi
- **🎮 Eğlenceli Oyunlar**: Yazı tura, slot makinesi, blackjack, rulet ve Son Harf oyunu
- **📊 Seviye Sistemi**: Aktif kullanıcıları ödüllendiren seviye sistemi
- **🌍 Çoklu Dil Desteği**: Türkçe ve İngilizce dil seçenekleri
- **🕒 Kişiselleştirilmiş Zaman Dilimi**: Kullanıcıların kendi zaman dilimlerini ayarlama imkanı
- **📊 Anketler**: Kolay anket oluşturma

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya daha yüksek
- pip (Python paket yöneticisi)
- Discord Bot Token

### Adımlar

1. Repoyu klonlayın:
```bash
git clone https://github.com/kullaniciadi/tomris-bot.git
cd tomris-bot
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. `.env` dosyasına Discord token'ınızı ekleyin:
```
DISCORD_TOKEN=your_discord_token_here
```

4. Botu çalıştırın:
```bash
python bot.py
```


## 📝 Komutlar

### 🛡️ Moderasyon Komutları
- `/ban <kullanıcı>` - Kullanıcıyı yasakla
- `/unban <kullanıcı_id>` - Kullanıcının yasağını kaldır
- `/kick <kullanıcı>` - Kullanıcıyı at
- `/clear <miktar>` - Belirtilen sayıda mesajı sil
- `/lock` - Kanalı kilitle
- `/unlock` - Kanal kilidini kaldır

### 💰 Ekonomi Komutları
- `/daily` - Günlük ödülünü al
- `/balance` - Bakiyeni görüntüle

### 🎮 Oyun Komutları
- `/coinflip <miktar>` - Yazı tura at (2x kazanç)
- `/slots <miktar>` - Slot makinesi (1x-10x kazanç)
- `/blackjack <miktar>` - Blackjack oyna (2x kazanç)
- `/roulette <miktar> <bahis_türü> [sayı]` - Rulet oyna
  - Renk/çift-tek/yüksek-düşük: 2x kazanç
  - Sayı: 35x kazanç
- `/sonharf <işlem> [ilk_kelime]` - Son Harf Oyunu oyna

### 📊 Seviye Sistemi
- `/rank [kullanıcı]` - Seviye bilgilerini görüntüle
- `/levels` - Sunucunun seviye sıralamasını görüntüle

### 🛠️ Yardımcı Komutlar
- `/weather <şehir>` - Hava durumunu göster
- `/poll <soru> [seçenekler]` - Anket oluştur

### ⚙️ Diğer Komutlar
- `/profile [kullanıcı]` - Profilini görüntüle
- `/language <dil>` - Bot dilini değiştir (tr/en)
- `/timezone <zaman_dilimi>` - Zaman dilimini ayarla
- `/ping` - Bot gecikmesini ölç
- `/info` - Bot hakkında bilgi al
- `/commands` - Komut listesini görüntüle

## 🕒 Zaman Dilimi Desteği

Tomris Bot, kullanıcıların kendi zaman dilimlerini ayarlamalarına olanak tanır. Bu sayede günlük ödüller ve diğer zaman bazlı özellikler kullanıcının kendi zaman dilimine göre çalışır.

Zaman diliminizi ayarlamak için:
```
/timezone <zaman_dilimi>
```

Komutunu kullanabilirsiniz. Bot size yaygın zaman dilimlerinden bir liste sunar veya kendi zaman diliminizi manuel olarak girebilirsiniz.

## 🎮 Oyunlar

### Son Harf Oyunu

Son Harf, kullanıcıların sırayla bir önceki kelimenin son harfiyle başlayan kelimeler söylediği eğlenceli bir kelime oyunudur.

Oyunu başlatmak için:
```
/sonharf başlat [ilk_kelime]
```

Oyunu durdurmak için:
```
/sonharf durdur
```

Oyun hakkında bilgi almak için:
```
/sonharf bilgi
```

### Kumar Oyunları

Bot, çeşitli kumar oyunları sunar:

- **Yazı Tura**: Basit bir yazı-tura oyunu. Doğru tahmin ederseniz bahsinizin 2 katını kazanırsınız.
- **Slot Makinesi**: Şansınıza bağlı olarak bahsinizin 1x-10x katını kazanabilirsiniz.
- **Blackjack**: Klasik kart oyunu. Kazanırsanız bahsinizin 2 katını alırsınız.
- **Rulet**: Farklı bahis türleriyle oynayabileceğiniz rulet oyunu.

## 🔗 Destek

Sorunlar, öneriler veya katkılar için:
- [GitHub Issues](https://github.com/kullaniciadi/tomris-bot/issues)
- [Discord Destek Sunucusu](https://discord.gg/2RTHvbfH3a)

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<div align="center">
  <b>Tomris Bot</b> • Güvenli ve Güçlü Yönetim
  <br>
  Geliştirici: <a href="https://kayapater.com.tr">Vai</a>
</div>
