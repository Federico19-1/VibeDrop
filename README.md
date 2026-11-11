<p align="center">
  <img src="assets/vibedrop.png" width="104" alt="VibeDrop logo">
</p>

<h1 align="center">VibeDrop</h1>

<p align="center">
  <b>YouTube to MP3, on your PC — and straight to your phone.</b><br>
  Paste a link, get a clean MP3. Optionally delivered to your own Telegram chat.
</p>

<p align="center">
  <img alt="Windows 10 | 11" src="https://img.shields.io/badge/Windows-10%20%7C%2011-5ab9fc?style=flat-square&logo=windows&logoColor=white&labelColor=0a0d14">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-5ab9fc?style=flat-square&logo=python&logoColor=white&labelColor=0a0d14">
  <img alt="Powered by yt-dlp" src="https://img.shields.io/badge/powered%20by-yt--dlp-5ab9fc?style=flat-square&labelColor=0a0d14">
  <img alt="Languages: EN, IT, ES" src="https://img.shields.io/badge/UI-EN%20%7C%20IT%20%7C%20ES-5ab9fc?style=flat-square&labelColor=0a0d14">
</p>

<p align="center">
  <a href="https://github.com/YOUR_USERNAME/VibeDrop/releases/latest"><b>⬇️ Download</b></a> ·
  <a href="#-quick-start"><b>Quick start</b></a> ·
  <a href="#-send-to-telegram"><b>Telegram setup</b></a> ·
  <a href="docs/FAQ.md"><b>FAQ</b></a> ·
  <a href="docs/GUIDA.md"><b>🇮🇹 Guida</b></a>
</p>

<br>


<p align="center">
  <img src="docs/images/vibedrop.png" width="860" alt="VibeDrop main window">
</p>

<br>

## ✨ Why VibeDrop

Most "YouTube to MP3" sites are full of pop-ups, fake buttons and trackers.
VibeDrop is a small desktop app that does the one job **locally on your computer**:
no website in the middle, no account, no ads.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🎧 Paste, press, done</h3>
      Paste one link or fifty — videos, Shorts, <code>youtu.be</code>, live and YouTube Music links.
      A tidy queue downloads them one by one with live progress.
    </td>
    <td width="50%" valign="top">
      <h3>📱 Straight to your phone</h3>
      Connect your own Telegram bot once and every finished MP3 lands in your chat,
      ready to play. Finding the chat id is a single click.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🎚️ Quality you choose</h3>
      128, 192, 256 or 320 kbps MP3, converted by FFmpeg.
      Open the file or play it right from the queue.
    </td>
    <td width="50%" valign="top">
      <h3>📝 Notes built in</h3>
      Jot down the songs you want to grab later and tick them off as you go.
      Hide the panel if you don't need it.
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🔒 Local-first and private</h3>
      Settings, history and your bot token never leave your computer.
      The only servers involved are YouTube and, if you want, Telegram.
    </td>
    <td width="50%" valign="top">
      <h3>🔄 Stays working</h3>
      VibeDrop checks for new versions of yt-dlp and updates it with one click
      when YouTube changes something.
    </td>
  </tr>
</table>

Plus: **English, Italiano, Español** · light, dark and system themes · zoom
controls · a built-in guide · a layout that adapts from full screen down to a
small window.

## 🚀 Quick start

> **Never installed a program by hand?** Follow the illustrated
> [step-by-step guide (Italian)](docs/GUIDA.md): it assumes no prior experience.

1. **Download** `VibeDrop.exe` from the
   [latest release](https://github.com/YOUR_USERNAME/VibeDrop/releases/latest)
   and put it in a folder of its own, e.g. `Documents\VibeDrop`.
2. **Get FFmpeg** (it does the MP3 conversion): download
   [ffmpeg-release-essentials.zip](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip),
   open it, go into `bin` and copy **`ffmpeg.exe`** next to `VibeDrop.exe`.

   ```
   📁 VibeDrop
   ├── VibeDrop.exe
   └── ffmpeg.exe
   ```

3. **Open** `VibeDrop.exe`. If Windows shows *"Windows protected your PC"*, click
   **More info → Run anyway** (only the first time).
4. Check that the top bar says **ffmpeg ready**.
5. **Paste** a YouTube link and press **Download** (or `Ctrl + Enter`).
   Your MP3 appears in `Music\VibeDrop`.

## 📲 Send to Telegram

Optional, about three minutes, done once.

| | Step |
|:-:|---|
| 1 | In Telegram, open **[@BotFather](https://t.me/BotFather)** (blue check mark) and send `/newbot`. |
| 2 | Pick a display name, then a username that ends in `bot` (e.g. `my_music_2026_bot`). |
| 3 | Copy the **token** BotFather replies with — it looks like `7012345678:AAH…`. |
| 4 | In VibeDrop open **Settings** and paste it into **Telegram bot token**. |
| 5 | Open **your new bot**, press **Start** and send it any message. |
| 6 | Back in VibeDrop press **Find chat id**, then **Test connection**, then **Save**. |

The bot greets you with *"Connection works"*, and from then on every MP3 is
delivered automatically. Files over Telegram's 50 MB bot limit are kept on the
PC and only their path is sent.

> [!CAUTION]
> Treat the bot token like a password. If it leaks, revoke it in BotFather
> (`/mybots` → your bot → **API Token** → **Revoke**) and paste the new one.

Stuck? The FAQ covers every error message and three ways to find your chat id:
🇬🇧 [English](docs/FAQ.md) · 🇮🇹 [Italiano](docs/FAQ.it.md) · 🇪🇸 [Español](docs/FAQ.es.md)

## 📚 Documentation

| | |
|---|---|
| 🇮🇹 **[Guida passo passo](docs/GUIDA.md)** | Installation and first use for complete beginners, Telegram bot included |
| ❓ **FAQ** — [English](docs/FAQ.md) · [Italiano](docs/FAQ.it.md) · [Español](docs/FAQ.es.md) | Troubleshooting, errors, Telegram, cookies, data and privacy |

## 🛠️ Run from source

Works on Windows, macOS and Linux. You need **Python 3.11+** and **FFmpeg**
(on your `PATH`, or `ffmpeg.exe` in a `bin/` folder next to the project).

```powershell
git clone https://github.com/YOUR_USERNAME/VibeDrop.git
cd VibeDrop
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt   # macOS/Linux: .venv/bin/python
.venv\Scripts\python run.py
```

The desktop window opens on its own. Without a system webview, the same interface
opens in your browser.

| Command | What it does |
|---|---|
| `python run.py` | Starts the app in its own window |
| `python run.py --serve` | Starts only the local server and prints its URL |
| `python run.py --port 9000` | Uses a different local port (default `8756`) |

### Build the Windows executable

```powershell
.venv\Scripts\python -m pip install pyinstaller
.venv\Scripts\python build.py
```

The result is a single file, `dist\VibeDrop.exe`. Put `ffmpeg.exe` in `bin\` before
building to bundle it inside the executable.
To regenerate the app icon after editing the mark, run `python assets/make_icon.py`.

## 🗂️ Project structure

```
VibeDrop/
├── run.py              # entry point
├── build.py            # one-file Windows build (PyInstaller)
├── app/                # local server and download pipeline
│   ├── main.py         #   window + server startup
│   ├── server.py       #   JSON API and static files
│   ├── jobs.py         #   download queue
│   ├── downloader.py   #   yt-dlp + FFmpeg → MP3
│   ├── telegram.py     #   delivery to your bot
│   ├── updates.py      #   yt-dlp update checks
│   ├── notes.py        #   notes panel storage
│   └── config.py       #   settings and data folder
├── ui/                 # the interface (HTML, CSS, JS, fonts)
├── assets/             # icon (.ico, .svg, .png) and its generator
└── docs/               # beginner guide and FAQ (EN · IT · ES)
```

## 🔐 Privacy and data

Everything VibeDrop stores lives in one folder on your computer:

| OS | Location |
|---|---|
| Windows | `%APPDATA%\VibeDrop` |
| macOS | `~/Library/Application Support/VibeDrop` |
| Linux | `~/.config/VibeDrop` |

Set `MUSIC_EXTRACTOR_HOME` to use another folder (handy for portable setups and
tests). The Telegram token and chat id can also come from the `TELEGRAM_TOKEN` and
`TELEGRAM_CHAT_ID` environment variables.

## ⚖️ Responsible use

VibeDrop is meant for **personal use**. Only download audio you have the right to
use, and respect copyright and YouTube's Terms of Service.

## 🙏 Built with

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the download engine
- [FFmpeg](https://ffmpeg.org) — audio conversion
- [pywebview](https://pywebview.flowrl.com) — the native desktop window
- [Albert Sans](https://fonts.google.com/specimen/Albert+Sans) and
  [DM Mono](https://fonts.google.com/specimen/DM+Mono) — typography

<p align="center">
  <sub>Made with ♪ for people who just want their music.</sub>
</p>
