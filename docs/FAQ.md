<h1 align="center">VibeDrop · FAQ</h1>

<p align="center">
  🇬🇧 <b>English</b> · 🇮🇹 <a href="FAQ.it.md">Italiano</a> · 🇪🇸 <a href="FAQ.es.md">Español</a>
  <br>
  First install? The <a href="../README.md#-quick-start">Quick start</a> covers it in five steps
  (step-by-step beginner guide available <a href="GUIDA.md">in Italian</a>).
</p>

---

**Topics:**
[Install and launch](#install-and-launch) ·
[Downloads](#downloads) ·
[Telegram](#telegram) ·
[Settings and data](#settings-and-data)

---

## Install and launch

### Windows says "Windows protected your PC". Is it a virus?

No. Windows shows this screen for every new program that does not carry a
well-known signature yet. Click **More info**, then **Run anyway**. It only happens
the first time.

### My antivirus blocks or quarantines VibeDrop.exe

Some antivirus engines wrongly flag programs packaged with PyInstaller, the tool
used to build VibeDrop. Only download the app from the project's official
**Releases** page on GitHub and, if you trust it, add it to your antivirus
exceptions. You can also run VibeDrop from source (see the [README](../README.md)).

### I double-click VibeDrop and nothing happens

The first launch can take **10–20 seconds** while the program unpacks itself. Wait
without clicking again. If nothing has appeared after a minute, restart the
computer and try again.

### The app opens in my browser instead of its own window

VibeDrop uses a Windows component called **Microsoft Edge WebView2**. When it is
missing, the app opens the same interface in your browser and works the same way.
To get the window back, install the **WebView2 Runtime** from Microsoft (search for
*"WebView2 Runtime download"*, choose the **Evergreen Bootstrapper**) and reopen
VibeDrop. Windows 11 already includes it.

### The top bar says "ffmpeg not found"

ffmpeg is the program that converts audio to MP3 and it is **already bundled
inside `VibeDrop.exe`**: if you are using the executable from the releases page,
this message should never appear. If you do see it, you almost certainly have an
old copy — download `VibeDrop.exe` again from the
[latest release](https://github.com/Federico19-1/VibeDrop/releases/latest).

If you run VibeDrop from source instead, you need your own ffmpeg. The app looks
for it, in order:

1. inside the executable's own bundle;
2. in a **`bin`** folder next to the program;
3. in the **same folder** as the program;
4. among the programs installed system-wide (your *PATH*).

From a terminal, `winget install Gyan.FFmpeg` installs it system-wide; restart
the computer afterwards.

### Does it work on macOS or Linux?

`VibeDrop.exe` is Windows-only. On macOS and Linux you can run VibeDrop from source
with Python 3.11+ (see the [README](../README.md)) after installing ffmpeg
(`brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Ubuntu/Debian).

### The desktop icon is blank or looks wrong

Windows caches icons it has already seen. Restart the computer and the right icon
(a dark rounded square with five sky-blue bars) appears on its own.

---

## Downloads

### Which links can I paste?

Links to **single YouTube videos**:

- `https://www.youtube.com/watch?v=…`
- `https://youtu.be/…`
- `https://www.youtube.com/shorts/…`
- `https://www.youtube.com/live/…`
- `https://music.youtube.com/watch?v=…`

Paste as many as you like, **one per line**.
**Whole playlists** are not supported: when a link points to both a video and a
playlist, VibeDrop downloads just that video.

### "Unrecognised link"

What you pasted is not a video address. Open the video on YouTube, click the
address bar, copy with **Ctrl + C** and paste again.

### Where do my songs go?

Into the folder shown **at the bottom right** of the VibeDrop window, usually
**Music → VibeDrop** (`C:\Users\<you>\Music\VibeDrop`). Press **Open** next to a
finished song to jump straight to it.

### How do I change the download folder?

Either:

- click the path **at the bottom right**, type the new one and press **Enter**
  (**Esc** cancels), or
- go to **Settings → Destination folder** → **Save**.

If the folder does not exist, VibeDrop creates it.

### A song is stuck on "Error". What does the message mean?

| Message | What to do |
|---|---|
| *Video unavailable / Private video* | The video was removed, is private or is blocked in your country: it cannot be downloaded. |
| *Age-restricted video* / *YouTube asks you to sign in* | You need a `cookies.txt` file, see [below](#what-is-cookiestxt-and-how-do-i-make-one). |
| *Video reserved for channel members* | Only an account that is a member of the channel can get it (`cookies.txt`). |
| *YouTube refused the download (403)* | Wait a few minutes and press **Retry**. If it keeps happening, update yt-dlp. |
| *Too many requests to YouTube (429)* | You downloaded a lot in a short time: wait 10–15 minutes. |
| *The connection timed out* | Check your internet connection and press **Retry**. |
| *The MP3 file was not created* | The conversion failed: try again, and if it persists download `VibeDrop.exe` again from the latest release. |
| *Interrupted when the app was closed* | VibeDrop was closed mid-download: press **Retry**. |

### Downloads were working and suddenly they all fail

YouTube changes often, and the component that does the downloading, **yt-dlp**,
needs updating. Go to **Settings → Check for updates** (or click **Update** in the
*"yt-dlp needs an update"* strip at the top), wait for the confirmation, then
**close and reopen** VibeDrop.

### What is cookies.txt and how do I make one?

Some videos (age-restricted or members-only) are only visible to signed-in
accounts. `cookies.txt` lets VibeDrop talk to YouTube **as your account**.

1. In the browser where you are signed in to YouTube, install an extension that
   exports cookies in *Netscape* format, such as **"Get cookies.txt LOCALLY"**.
2. Open **youtube.com**, click the extension and export the cookies.
3. Rename the file to **`cookies.txt`**.
4. Press **⊞ Win + R**, type `%APPDATA%\VibeDrop`, press **Enter** and put the
   file in that folder.

> [!CAUTION]
> `cookies.txt` gives access to your YouTube/Google account. Never share it, and
> delete it when you no longer need it.

### Can I choose the quality?

Yes: **Settings → MP3 quality**, from **128** to **320 kbps**. 192 kbps is a good
balance; higher quality means bigger files.

### Can I download several songs at once?

Yes: paste several links, one per line, and press **Download**. VibeDrop downloads
them **one at a time**, in order.

---

## Telegram

### Do I need Telegram?

No. Without it, songs simply stay on your computer. Telegram is only for receiving
them on your phone as well.

### Where do I find my bot token (the "API key")?

**@BotFather** gives it to you when you create the bot. If you lost it:

1. open the chat with **BotFather** (the one with the blue check mark);
2. send `/mybots`;
3. tap your bot → **API Token**.

A token looks like `7012345678:AAHk3xQ-Zb9Lm2Pq8RsTuVwXyZ0aBcDeFgH`
(digits, a **colon**, then letters and digits).

### Find chat id says "No chat found"

Your bot only sees messages **sent to it**. Check that:

1. you are writing to **your bot**, not to **BotFather** (your bot has the username
   you picked, ending in *bot*);
2. you pressed **START** and then sent a message, e.g. *hi*;
3. the token in VibeDrop belongs to **that** bot — easy to mix up if you made more
   than one;
4. Telegram only keeps those messages for **24 hours**: if it has been longer, send
   *hi* again.

Then press **Find chat id** again.

### Find chat id still fails: how do I get the chat id by hand?

**Option 1 — in the browser** (nothing to install):

1. Send any message to your bot.
2. Open this address, replacing `YOUR_TOKEN` with your token:
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
   (the token goes right after `bot`, with no space or `/`).
3. Look for `"chat":{"id":` — the number after it is your **chat id**, e.g.
   `"chat":{"id":123456789`.
4. Paste it into the **Chat id** field in VibeDrop.

If the page only shows `{"ok":true,"result":[]}`, the bot has not received any
message: write to it again and reload the page.

**Option 2 — with a bot:** search Telegram for **@userinfobot** and press **START**.
It replies with your **Id**, which is also the chat id of your private chat with
your bot. (It is a third-party bot unrelated to VibeDrop; it only tells you your
number.)

### Test connection shows an error. What does it mean?

| Message | Cause and fix |
|---|---|
| *Invalid token* | The token was copied partially, with an extra space, or belongs to another bot. Copy it again from BotFather (`/mybots` → bot → **API Token**). |
| *Invalid chat id* | The chat id is wrong, or you never wrote to the bot. Send *hi* to the bot and use **Find chat id**. |
| *You blocked the bot* | Open the bot's chat in Telegram and press **Unblock** / **START**. |
| *The bot is not a member of that chat* | The chat id belongs to a group the bot is not in: add it to the group, or use your private chat. |
| *Telegram unreachable* | No internet, or the network (office, school, hotel) blocks Telegram. Try another network. |
| *Too many requests to Telegram* | Wait a minute and try again. |
| *The bot token and the chat id are both needed* | One of the two fields is empty. |

### The connection works but songs never reach my phone

- Did you press **Save** after **Test connection**? Without **Save** nothing is kept.
- Look at the song's row in VibeDrop: if it says *"Telegram failed"*, the message
  next to it explains why. You can try again with **Send again**.
- Make sure you are looking at **your bot's** chat in Telegram, not BotFather's.

### "Path only sent": why didn't I get the song?

Telegram does not let bots send files over **50 MB** (about 35 minutes at 192 kbps).
For bigger files the bot sends you the path where the file is saved on your
computer. For very long audio, lower the **MP3 quality**.

### Can I receive songs in a group?

Yes. Add your bot to the group, send a message in the group and press
**Find chat id**, then pick the group (its chat id is a negative number such as
`-1001234567890`).

### I accidentally shared my token. What now?

Anyone with the token can use your bot. Replace it right away:

1. open **BotFather** → send `/mybots` → pick the bot → **API Token** →
   **Revoke current token**;
2. paste the **new** token into **VibeDrop → Settings** and press **Save**.

The old token stops working immediately.

### Where is the token stored? Is it safe?

It stays **on your computer only**, in `settings.json` inside `%APPDATA%\VibeDrop`.
VibeDrop uses it solely to talk to Telegram. Do not send that file to anyone.

### How do I stop sending songs to Telegram?

**Settings** → clear **Telegram bot token** and **Chat id** → **Save**.

---

## Settings and data

### How do I change language or theme?

**Settings → Language** (English, Italiano, Español) and **Theme** (Light, Dark,
System) → **Save**.

### Text is too small or too large

Use the **−** and **+** buttons at the top, or **Ctrl + mouse wheel**,
**Ctrl + +** and **Ctrl + −**. **Ctrl + 0** goes back to 100%.

### Are my notes kept when I close the app?

Yes. Notes in the **Notes** panel are saved on your computer (in
`%APPDATA%\VibeDrop`) and are still there next time. You can keep up to 200; remove
them with **Delete**, or all at once with **Clear**.

### Does "Clear finished" delete my songs?

No. It only removes the rows from the list; the MP3 files stay in the folder.
**Delete** on a single song also removes just the row.

### What are "Details below downloads"?

The text shown under each finished song and used as the Telegram caption. Customise
it in **Settings** with `{title}`, `{duration}` and `{size}`.

### Where are settings, history and notes stored?

In `%APPDATA%\VibeDrop` on Windows (press **⊞ Win + R**, type `%APPDATA%\VibeDrop`,
**Enter**), `~/Library/Application Support/VibeDrop` on macOS and
`~/.config/VibeDrop` on Linux. Set the `MUSIC_EXTRACTOR_HOME` environment variable
to use a different folder.

### I want a fresh start

Close VibeDrop and delete the `%APPDATA%\VibeDrop` folder. The next launch behaves
like a new install. Songs you already downloaded are not touched.

### Is this legal?

VibeDrop is a tool for **personal use**. Only download content you have the right
to use, and respect copyright and YouTube's terms of service.

---

<p align="center">
  Didn't find your answer? Open an <b>Issue</b> on the project's GitHub page.
</p>
