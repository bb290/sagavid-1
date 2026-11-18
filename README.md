# sagavid

Sagareus video tools for staff (sagavid-1), packaged as a Claude Code plugin. Two video types, three styles each:

- **`/sagavid:before-after` + the Video Production card** makes a before/after video for owners, 30 seconds or less, in one of three styles (Junk, Trashed, Reno). Junk and Trashed need the SOP link on the card; Reno needs 1 to 2 lines on the card about what is happening in the video. Claude writes the script in Brittany's voice from that source (`VOICE.md`) and the staff member records it; never an AI voice. (The command is being finished; the three build scripts are in `skills/before-after/`.)
- **`/sagavid:listing-video <buildium link>`** makes a 20-to-25-second vertical listing video from a Buildium rental listing (photos plus any phone walkthrough), in one of three approved styles (Fast Tour, Auto-Slide, Editorial). The staff member approves the shot list and the cut in the chat, and Claude puts it on the Asana Video Production board in **Draft**, assigned to Brittany for Final Approval. All three work the same way: the staff member approves their own storyboard and cut, and the card lands in Draft for Brittany. When Brittany moves the card to **Approved**, it is scheduled to the five channels from her side. Nothing posts from a staff computer.

Staff guide with the Video Creation steps and all six samples: Outline, [SagaVids -1](https://sagareus.getoutline.com/doc/sagavids-1-MBhNsUEbSF). Setup is below.

## Setup (once per computer, about 20 minutes)

You need: a Mac (Windows works too; commands below), your Sagareus Claude account, Google Drive for desktop signed in with your Sagareus Google account (so the "Video Content" shared drive shows up), and access to this GitHub repo (ask Brittany).

1. **Install the Claude desktop app** from claude.ai/download and sign in with your Sagareus account. Open the **Code** tab.
2. **Connect Asana** in claude.ai: Settings, Connectors, Asana, Connect. (Claude uses it to put the video on the board.)
3. **Install the tools.** On a Mac open Terminal and paste, one line at a time:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install node ffmpeg python gh
   gh auth login
   npx --yes hyperframes@0.8.204 doctor
   ```
   On Windows, open PowerShell and run `winget install OpenJS.NodeJS Gyan.FFmpeg Python.Python.3.12 GitHub.cli`, then `gh auth login` and `npx --yes hyperframes@0.8.204 doctor`. Google Chrome must be installed. If `doctor` reports a missing browser, run `npx --yes hyperframes@0.8.204 browser` and follow what it says.
4. **ElevenLabs key** (for before/after videos: voice cleanup and transcripts). Brittany sends you the key privately. Never paste it into the Claude chat, Asana, email, or Slack. On a Mac, in Terminal:
   ```
   mkdir -p ~/.sagavid && read -rs "KEY?Paste the ElevenLabs key, then press Enter: " && echo "ELEVENLABS_API_KEY=$KEY" > ~/.sagavid/.env && chmod 600 ~/.sagavid/.env && unset KEY
   ```
   On Windows, in PowerShell:
   ```
   New-Item -ItemType Directory -Force "$HOME\.sagavid" | Out-Null; $k = Read-Host "Paste the ElevenLabs key"; "ELEVENLABS_API_KEY=$k" | Out-File -Encoding ascii "$HOME\.sagavid\.env"; Remove-Variable k
   ```
5. **Install the plugin.** In the Claude desktop app's Code tab, type:
   ```
   /plugin marketplace add bb290/sagavid-1
   /plugin install sagavid@sagavid
   ```
   Restart the Code session when it asks.

To get updates later: `/plugin marketplace update sagavid`.

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
