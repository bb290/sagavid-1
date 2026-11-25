---
name: setup
description: Set up a Sagareus staff computer (Mac or Windows) for making videos, from inside Claude Code. Checks and installs the video tools (Homebrew on a Mac, Node, ffmpeg, Python, poppler, Chrome, Google Drive for desktop, the HyperFrames video engine), checks the Video Content shared drive and the Asana connector, and saves the ElevenLabs key privately through a pop-up so it never enters the chat. Safe to run again any time; it skips what is already done. Use on "/sagavid:setup", "set up my computer for videos", or when another sagavid skill says a tool or the key is missing.
---

# Sagavid setup (staff computer)

The staff member has the Claude app open on the **Code** tab, signed in with their Sagareus account, and has just installed this plugin. Do everything else for them here. They are not technical: run every command yourself, say in one plain sentence what you are doing and roughly how long it takes, and only ask them to do something you can't (type their computer password into a system window, click Install or Allow, sign in to Google, paste the key into a pop-up).

Go in order. **Check each step first and skip it if it's already done.** After each step, say "Done" or what went wrong in one line. If a step fails twice, stop, tell them which step and what it said, and ask them to send Brittany a screenshot of the chat.

## Never

- **Never ask for the ElevenLabs key in the chat, and never print it, echo it, or read the .env file back.** It only goes in through the pop-up in step 6. If they paste the key into the chat anyway, don't use it: tell them to let Brittany know so she can replace it, and carry on with the pop-up.
- Never ask them to type their computer password into the chat. It only goes into the system's own window (macOS Installer, "Allow changes" on Windows).
- Never change system settings, security settings, or anything outside what this page lists.

## Mac

1. **Command Line Tools.** `xcode-select -p`. If it fails, run `xcode-select --install`: a box pops up; tell them to click **Install**, accept, and wait (5 to 15 minutes). Wait until `xcode-select -p` works.
2. **Homebrew.** `/opt/homebrew/bin/brew --version || /usr/local/bin/brew --version`. If missing: Homebrew's official installer script needs a password in a terminal, which you can't type, so use its official macOS installer package instead. Get the newest installer package (currently `Homebrew.pkg`) from `https://api.github.com/repos/Homebrew/brew/releases/latest` (the asset whose name ends in `.pkg`), download it into a new empty folder under `~/Downloads/sagavid-setup/`, and `open` it. Tell them: "The Homebrew installer opened. Click Continue through it, and type your Mac password when it asks. Tell me when it says the installation was successful." Then make sure new shells find it: if `~/.zprofile` doesn't already have the line, append `eval "$(/opt/homebrew/bin/brew shellenv)"` (Intel Macs: `/usr/local/bin/brew`), and run it in your own shell before the next step.
3. **Video tools.** `brew install node ffmpeg python poppler` (5 to 10 minutes; skip any already installed). Check with `node --version`, `ffmpeg -version`, `python3 --version`, `pdfimages -v`.
4. **Chrome and Google Drive.** Chrome: if `/Applications/Google Chrome.app` is missing, `brew install --cask google-chrome`. Google Drive: if `/Applications/Google Drive.app` is missing, download `https://dl.google.com/drive-file-stream/GoogleDrive.dmg` into `~/Downloads/sagavid-setup/`, mount it with `hdiutil attach`, and `open` the installer package inside. Tell them to click through it and type their Mac password if asked. Then `open -a "Google Drive"` and ask them to sign in with their **Sagareus** Google account and tell you when it's done.
5. **The Video Content shared drive.** `ls ~/Library/CloudStorage/GoogleDrive-*/"Shared drives/"`. It must list **Video Content** with a **Finals** folder inside. Drive can take a minute after sign-in; check again before giving up. If it's still missing, they're not on the shared drive yet: tell them to ask Brittany to add them, and carry on (come back to it at the end).
6. **The ElevenLabs key.** If `~/.sagavid/.env` exists and has a line starting `ELEVENLABS_API_KEY=`, it's done (check with `grep -c '^ELEVENLABS_API_KEY=.' ~/.sagavid/.env`, which prints a count, not the key). If not, tell them: "Open 1Password, go to Property Access, search ElevenLabs, and copy the key. A box will pop up next; paste the key into it and click OK. Don't paste it here in the chat." Then run, as one command:

   ```
   mkdir -p ~/.sagavid && KEY=$(osascript -e 'text returned of (display dialog "Paste the ElevenLabs key from 1Password, then click OK." default answer "" with hidden answer with title "Sagareus video setup")') && [ -n "$KEY" ] && printf 'ELEVENLABS_API_KEY=%s\n' "$KEY" > ~/.sagavid/.env && chmod 600 ~/.sagavid/.env; unset KEY; grep -c '^ELEVENLABS_API_KEY=.' ~/.sagavid/.env
   ```

   `1` means it's saved. If they clicked Cancel or it prints `0` or an error, offer to try again.
7. **Video engine.** `npx --yes hyperframes@0.8.204 doctor`. If it says a browser is missing, run `npx --yes hyperframes@0.8.204 browser`, then `doctor` again.

## Windows

Claude Code on Windows runs commands in PowerShell or Git Bash; use PowerShell for these steps (`powershell -NoProfile -Command "..."` from Git Bash). If `winget` isn't found, ask them to open the **Microsoft Store**, search **App Installer**, click **Get** or **Update**, and tell you when it's done.

1. **Video tools.** For each of `OpenJS.NodeJS.LTS`, `Gyan.FFmpeg`, `Python.Python.3.12`, `Google.Chrome`, `Google.GoogleDrive`: check with `winget list --id <id> -e`, and if missing, `winget install --id <id> -e --accept-package-agreements --accept-source-agreements`. When a box asks "Do you want to allow this app to make changes?", tell them to click **Yes**. New tools aren't on the PATH of an already-open shell: refresh it in your own commands (`$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`), and tell them to quit and reopen Claude at the end. Check with `node --version`, `ffmpeg -version`, `py --version` (use `py`, never `python3`, which can open the Microsoft Store). poppler isn't installed on Windows; that only matters for move-out report PDFs (they save the photos from the PDF and drag them in).
2. **Google Drive.** Start Google Drive and ask them to sign in with their **Sagareus** Google account. Then check `G:\Shared drives\Video Content\Finals` exists. If not, the same as the Mac's step 5.
3. **The ElevenLabs key.** If `$HOME\.sagavid\.env` has a line starting `ELEVENLABS_API_KEY=`, it's done (`(Select-String -Path "$HOME\.sagavid\.env" -Pattern '^ELEVENLABS_API_KEY=.').Count`). If not, give the same 1Password instruction as the Mac's step 6, then run in Windows PowerShell (`powershell.exe`, so the box pops up as a window):

   ```
   New-Item -ItemType Directory -Force "$HOME\.sagavid" | Out-Null; $c = Get-Credential -UserName "ElevenLabs" -Message "Paste the ElevenLabs key from 1Password into the Password box, then click OK."; if ($c) { "ELEVENLABS_API_KEY=" + $c.GetNetworkCredential().Password | Out-File -Encoding ascii "$HOME\.sagavid\.env" }; Remove-Variable c -ErrorAction SilentlyContinue; (Select-String -Path "$HOME\.sagavid\.env" -Pattern '^ELEVENLABS_API_KEY=.').Count
   ```

   `1` means it's saved.
4. **Video engine.** The same as the Mac's step 7.

## Both: the Asana connector

Check that the Asana connector works by reading the Video Production project (`1219918573321945`): its name and sections. If there are no Asana tools or it fails, tell them: "In Claude, click your name (bottom left), then Settings, then Connectors. Find Asana, click Connect, sign in with your Sagareus account, and click Allow. Then tell me and I'll check again."

## Finish

Delete `~/Downloads/sagavid-setup/` if you made it (on a Mac, `hdiutil detach` the Drive installer first). Then give a short checklist, one line each: Homebrew (Mac), video tools, Chrome, Google Drive and the Video Content shared drive, the ElevenLabs key (say "saved", never the key), the video engine, Asana. Anything not done: what they need to do, or "ask Brittany to add you to the Video Content shared drive". If you installed anything on Windows, tell them to quit Claude completely and open it again.

When everything is done, say: "You're set up. To make a video, type `/sagavid:listing-video` or `/sagavid:before-after` here. Claude will ask which Asana card it's for, or make one."
