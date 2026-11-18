# sagavid

Sagareus video tools for staff (sagavid-1), packaged as a Claude Code plugin. Two video types, three styles each:

- **`/sagavid:before-after` + the Video Production card** makes a before/after video for owners, 30 seconds or less, in one of three styles (Junk, Trashed, Reno). Junk and Trashed need the SOP link on the card; Reno needs 1 to 2 lines on the card about what is happening in the video. Claude writes the script in Brittany's voice from that source (`VOICE.md`) and the staff member records it; never an AI voice. Full steps in `skills/before-after/SKILL.md`.
- **`/sagavid:listing-video <buildium link>`** makes a 20-to-25-second vertical listing video from a Buildium rental listing (photos plus any phone walkthrough), in one of three approved styles (Fast Tour, Auto-Slide, Editorial). The staff member approves the shot list and the cut in the chat, and Claude puts it on the Asana Video Production board in **Draft**, assigned to Brittany for Final Approval. All three work the same way: the staff member approves their own storyboard and cut, and the card lands in Draft for Brittany. When Brittany moves the card to **Approved**, it is scheduled to the five channels from her side. Nothing posts from a staff computer.

Staff guide with the Video Creation steps and all six samples: Outline, [SagaVids -1](https://sagareus.getoutline.com/doc/sagavids-1-MBhNsUEbSF). Setup (Mac and Windows, step by step) is below.

## Setup (once per computer, about 30 minutes)

You only do this once. After that, making a video is just typing a command in Claude.

### Before you start, have these ready

1. **Your Sagareus Claude login** (the account you use at claude.ai). Ask Brittany if you don't have one.
2. **The ElevenLabs key link** from Brittany. It arrives as a one-time link: open it only when you get to that step, because it disappears after one view.
3. **Your Sagareus Google login** (for Google Drive).

Then follow **either** the Mac steps **or** the Windows steps below, not both.

> **About the Terminal (Mac) and PowerShell (Windows):** they are a window where you paste a line of text and press a key to run it. You don't need to understand the text. For every line below: copy it, paste it into the window, press **Return** (Mac) or **Enter** (Windows), then **wait until the window is ready for the next line** (you see a blinking cursor at the start of a new line). Some lines take a few minutes. If something goes wrong, take a screenshot of the window and send it to Brittany.

---

## Mac setup

### Step 1. Install the Claude app

1. Go to **claude.ai/download** in your browser and download the Mac app.
2. Open the downloaded file and drag **Claude** into your **Applications** folder.
3. Open Claude and sign in with your Sagareus account.
4. At the top of the Claude window, click **Code**. You should see a chat box. Leave Claude open.

### Step 2. Connect Asana to Claude

1. In Claude, click your name (bottom left), then **Settings**.
2. Click **Connectors**.
3. Find **Asana** and click **Connect**. Sign in to Asana with your Sagareus account and click **Allow**.

### Step 3. Install Google Chrome and Google Drive

1. If you don't have Google Chrome, download it from **google.com/chrome** and install it.
2. Download **Google Drive for desktop** from **google.com/drive/download** and install it.
3. Sign in to Google Drive with your **Sagareus** Google account.
4. Open **Finder**. In the left sidebar under **Locations**, click **Google Drive**, then **Shared drives**. You should see **Video Content**. If you don't, ask Brittany to add you.

### Step 4. Open Terminal

1. Press **Command + Space** on your keyboard. A search bar appears.
2. Type **Terminal** and press **Return**. A small window with text opens. This is the Terminal.

To paste into Terminal, press **Command + V**.

### Step 5. Install Homebrew (a tool installer)

1. Copy this whole line, paste it into Terminal, and press **Return**:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. It asks for your **Mac password** (the one you use to log in to your Mac). Type it and press **Return**. **Nothing appears while you type**; that is normal.
3. It says "Press RETURN to continue". Press **Return**.
4. If a box pops up asking to install **Command Line Developer Tools**, click **Install** and wait for it to finish.
5. Wait. This takes 5 to 15 minutes. It is done when you see **Installation successful!**
6. Paste these three lines **one at a time**, pressing **Return** after each:
   ```
   echo >> ~/.zprofile
   ```
   ```
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   ```
   ```
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```
   On an older Intel Mac, the last line may print `no such file or directory`. That's fine; go on.
7. Check it worked: paste this and press **Return**:
   ```
   brew --version
   ```
   You should see something like `Homebrew 4.x.x`. If you see `command not found`, close Terminal, open it again (Step 4), and try `brew --version` once more.

### Step 6. Install the video tools

1. Paste this and press **Return**:
   ```
   brew install node ffmpeg python poppler
   ```
2. Wait. This takes 5 to 10 minutes and prints a lot of text. It is done when the cursor is back at the start of a new line.

### Step 7. Set up the video engine

1. Paste this and press **Return**:
   ```
   npx --yes hyperframes@0.8.204 doctor
   ```
2. Read the last lines. If it says a **browser is missing**, paste this and press **Return**:
   ```
   npx --yes hyperframes@0.8.204 browser
   ```

### Step 8. Save the ElevenLabs key

The key lets Claude clean up your voice recording. It is saved privately on your computer.

1. Open the one-time link from Brittany and **copy the key** (a long string of letters and numbers).
2. In Terminal, paste this whole line and press **Return**:
   ```
   mkdir -p ~/.sagavid && read -rs "KEY?Paste the ElevenLabs key, then press Return: " && echo "ELEVENLABS_API_KEY=$KEY" > ~/.sagavid/.env && chmod 600 ~/.sagavid/.env && unset KEY
   ```
3. It says **Paste the ElevenLabs key**. Press **Command + V**, then **Return**. **Nothing appears when you paste**; that is normal.
4. Check it saved: paste this and press **Return**:
   ```
   ls -a ~/.sagavid
   ```
   You should see `.env` in the list. If you see `No such file or directory`, repeat this step.

> Never paste the key anywhere else: not in the Claude chat, Asana, email, Slack, or a text.

You can close Terminal now.

### Step 9. Install the Sagareus video plugin in Claude

1. Go back to the Claude app, **Code** tab.
2. In the chat box, type this and press **Return**:
   ```
   /plugin marketplace add bb290/sagavid-1
   ```
3. Then type this and press **Return**:
   ```
   /plugin install sagavid@sagavid
   ```
4. If Claude asks you to restart, quit Claude (**Command + Q**) and open it again.

### Step 10. Check it works

In the Claude **Code** tab, type `/sagavid:before-after` and press **Return**. Claude should ask for the Asana card link. You're set up. You can stop there; the Video Creation steps above take it from here.

---

## Windows setup

### Step 1. Install the Claude app

1. Go to **claude.ai/download** in your browser and download the Windows app.
2. Open the downloaded file and follow the installer.
3. Open Claude and sign in with your Sagareus account.
4. At the top of the Claude window, click **Code**. You should see a chat box. Leave Claude open.

### Step 2. Connect Asana to Claude

1. In Claude, click your name (bottom left), then **Settings**.
2. Click **Connectors**.
3. Find **Asana** and click **Connect**. Sign in to Asana with your Sagareus account and click **Allow**.

### Step 3. Install Google Chrome and Google Drive

1. If you don't have Google Chrome, download it from **google.com/chrome** and install it.
2. Download **Google Drive for desktop** from **google.com/drive/download** and install it.
3. Sign in to Google Drive with your **Sagareus** Google account.
4. Open **File Explorer**. Click **Google Drive (G:)** in the left sidebar, then **Shared drives**. You should see **Video Content**. If you don't, ask Brittany to add you.

### Step 4. Open PowerShell

1. Click the **Start** button (Windows logo, bottom left or center).
2. Type **PowerShell**.
3. Click **Windows PowerShell**. A blue or black window with text opens. This is PowerShell.

To paste into PowerShell, **right-click** inside the window (or press **Ctrl + V**).

### Step 5. Install the video tools

1. Paste this line and press **Enter**:
   ```
   winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements
   ```
2. Wait until it says **Successfully installed**. If a box asks "Do you want to allow this app to make changes?", click **Yes**.
3. Do the same with this line:
   ```
   winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
   ```
4. And this line:
   ```
   winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
   ```
5. **Close PowerShell and open it again** (Step 4). This lets it find the new tools.
6. Check they worked: paste each line and press **Enter**. Each one should print a version number, not an error.
   ```
   node --version
   ```
   ```
   ffmpeg -version
   ```
   ```
   py --version
   ```

If PowerShell says `winget is not recognized`, open the **Microsoft Store**, search for **App Installer**, click **Get** or **Update**, then start Step 5 again.

### Step 6. Set up the video engine

1. Paste this and press **Enter**:
   ```
   npx --yes hyperframes@0.8.204 doctor
   ```
2. Read the last lines. If it says a **browser is missing**, paste this and press **Enter**:
   ```
   npx --yes hyperframes@0.8.204 browser
   ```

### Step 7. Save the ElevenLabs key

The key lets Claude clean up your voice recording. It is saved privately on your computer.

1. Open the one-time link from Brittany and **copy the key** (a long string of letters and numbers).
2. In PowerShell, paste this whole line and press **Enter**:
   ```
   New-Item -ItemType Directory -Force "$HOME\.sagavid" | Out-Null; $s = Read-Host "Paste the ElevenLabs key, then press Enter" -AsSecureString; $k = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)); "ELEVENLABS_API_KEY=$k" | Out-File -Encoding ascii "$HOME\.sagavid\.env"; Remove-Variable k, s
   ```
3. It says **Paste the ElevenLabs key**. Right-click to paste (you'll see stars instead of the key), then press **Enter**.
4. Check it saved: paste this and press **Enter**:
   ```
   Test-Path "$HOME\.sagavid\.env"
   ```
   It should say **True**. If it says **False**, repeat this step.

> Never paste the key anywhere else: not in the Claude chat, Asana, email, Slack, or a text.

You can close PowerShell now.

### Step 8. Install the Sagareus video plugin in Claude

1. Go back to the Claude app, **Code** tab.
2. In the chat box, type this and press **Enter**:
   ```
   /plugin marketplace add bb290/sagavid-1
   ```
3. Then type this and press **Enter**:
   ```
   /plugin install sagavid@sagavid
   ```
4. If Claude asks you to restart, close Claude completely and open it again.

### Step 9. Check it works

In the Claude **Code** tab, type `/sagavid:before-after` and press **Enter**. Claude should ask for the Asana card link. You're set up.

> **Windows only:** pulling photos out of a move-out report PDF (Reno videos) uses a tool that isn't installed on Windows. If Claude says it can't read the PDF's photos, open the PDF, save the photos you want, and drag them into the chat.

---

## Getting updates

When Brittany says there's an update, type this in the Claude **Code** tab and press **Return** or **Enter**:
```
/plugin marketplace update sagavid
```
Restart Claude if it asks.

## If something goes wrong

| What you see | What to do |
|---|---|
| `command not found: brew` (Mac) | Close Terminal, open it again, and try again. If it still fails, redo Step 5, part 6. |
| `winget is not recognized` (Windows) | Install **App Installer** from the Microsoft Store, then redo Step 5. |
| Claude says **No ElevenLabs key** | Redo the "Save the ElevenLabs key" step. |
| Claude says it **can't find the Video Content shared drive** | Open Google Drive for desktop, make sure you're signed in with your Sagareus account, and check that **Video Content** shows under Shared drives. |
| The video won't render, or Claude mentions **Chrome** | Run the "Set up the video engine" step again. |
| Anything else | Take a screenshot of the window and send it to Brittany. |

## Making a video

Type `/sagavid:listing-video` or `/sagavid:before-after` in the Code tab; Claude walks you through the rest (the full steps are in the Outline guide). The listing video:

1. Open the Code tab and type `/sagavid:listing-video` followed by the Buildium listing link. If you have a phone walkthrough, drag the clips into the chat.
2. Claude pulls the listing and the photos, picks the style, and shows you the slide list. Correct anything that is wrong ("the floors are new", "skip the bathroom photo").
3. Claude opens a preview in your browser. Press play and say what to change in plain words. Repeat until you like it.
4. Claude makes the final video and opens it. Watch it once more and say it is ready.
5. Claude saves it to the shared drive (Video Content, Finals) and puts it on the Video Production board, assigned to Brittany with a Final Approval subtask. That is it: Brittany takes it from there.

Your videos are kept in `Documents/Sagareus Videos/` on your computer.

## What the video never shows

Rent, deposit, specials, availability date, fees, screening criteria, utility costs, pet terms, lease terms, your name or number, any website. Nothing private (license plates, mail, people, children). No edited photos. Claude enforces all of this; if it flags something, it is on purpose.

## For maintainers

- `lib/sagavid.py`: shared paths (videos folder, the Video Content shared drive via Drive for desktop) and the ElevenLabs calls (key from `ELEVENLABS_API_KEY` or `~/.sagavid/.env`, passed to curl on stdin so it never shows on a command line).
- `skills/before-after/`: the Junk, Trashed and Reno before/after builds (`build_ba_junk.py`, `build_ba_trashed.py`, `build_ba_reno.py`), voice, captions and music scripts, each style's own track, sfx and fonts. Scripts come from the SOP the staff member links (Reno: the card's note on the work); no positions file ships with the plugin.
- Layout: `.claude-plugin/` (plugin and marketplace manifests), `skills/listing-video/` (SKILL.md, `scripts/`, `assets/fonts` Fraunces SIL OFL, `assets/music` the two approved tracks, `template/` the HyperFrames project files).
- The source of truth for the scripts is this repo. Brittany's own `/saga-listing-video` in the Sagareus workspace generates new music with ElevenLabs and writes to `content/listing-videos/`; the staff copy uses the music library and `~/Documents/Sagareus Videos/` instead. Keep script fixes in sync.
- Bump `version` in `.claude-plugin/plugin.json` when you change anything, so staff get the update.
