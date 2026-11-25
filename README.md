# sagavid

Sagareus video tools for staff (sagavid-1), packaged as a Claude Code plugin. Two video types, three styles each:

- **`/sagavid:setup`** sets up a staff Mac or PC from inside Claude Code (run it once after installing the plugin; safe to rerun).
- **`/sagavid:before-after` + the Video Production card** makes a before/after video for owners (Claude asks for the card first, or makes one), 30 seconds or less, in one of three styles (Junk, Trashed, Reno). Junk and Trashed need the SOP link on the card; Reno needs 1 to 2 lines on the card about what is happening in the video. Claude writes the script in Brittany's voice from that source (`VOICE.md`) and the staff member records it; never an AI voice. Full steps in `skills/before-after/SKILL.md`.
- **`/sagavid:listing-video <buildium link>`** makes a 20-to-25-second vertical listing video from a Buildium rental listing (photos plus any phone walkthrough), in one of three approved styles (Fast Tour, Auto-Slide, Editorial). The staff member approves the storyboard (a claude.ai Artifact they comment on) and the cut. Every video has a card on the Asana Video Production board: Claude asks for it first, makes one if there isn't one, and comments on it at each checkpoint so the board shows where every video is. When the staff member is happy, Claude moves the card to **Draft**, assigned to Brittany for Final Approval. All three work the same way: the staff member approves their own storyboard and cut, and the card lands in Draft for Brittany. When Brittany moves the card to **Approved**, it is scheduled to the five channels from her side. Nothing posts from a staff computer.

Staff guide with the Video Creation steps, the styles and all six samples: Outline, [SagaVids -1](https://sagareus.getoutline.com/doc/sagavids-1-MBhNsUEbSF). Setup: Outline, [Set Up // SagaVids-1](https://sagareus.getoutline.com/doc/set-up-sagavids-1-czcUMAeUic). The Setup and Making a video sections below match those two pages; change them together.

## Setup (once per computer, about 30 minutes, mostly waiting)

You only do this once. You do all of it in the Claude app: install Claude, connect Asana, add the video plugin, then type one command and Claude sets up the rest of your computer for you. After that, making a video is just typing a command in Claude.

Works the same on a Mac or a Windows computer.

### Before you start, have these ready


1. **Your Sagareus Claude login** (the account you use at claude.ai). Ask Brittany if you don't have one.
2. **1Password**, so you can copy the ElevenLabs API key: Property Access → search **ElevenLabs**.
3. **Your Sagareus Google login** (for Google Drive).
4. **Your computer password** (the one you use to log in to your Mac or PC). Your computer asks for it in its own window while Claude installs things.


> Claude will **never** ask you to type your computer password or the ElevenLabs key into the chat. The password only goes into your computer's own window, and the key only goes into the pop-up box Claude opens in Step 4. If you ever paste the key into the chat by mistake, tell Brittany so she can replace it.


---

### Step 1. Install the Claude app


1. Go to **claude.ai/download** in your browser and download the app for your computer (Mac or Windows).
2. Install it:
   * **Mac:** open the downloaded file and drag **Claude** into your **Applications** folder.
   * **Windows:** open the downloaded file and follow the installer.
3. Open Claude and sign in with your Sagareus account.
4. At the top of the Claude window, click **Code**. You should see a chat box. This is where you do everything from now on.

### Step 2. Connect Asana


1. In Claude, click your name (bottom left), then **Settings**.
2. Click **Connectors**.
3. Find **Asana** and click **Connect**. Sign in to Asana with your Sagareus account and click **Allow**.

### Step 3. Add the Sagareus video plugin


1. Go back to the **Code** tab.
2. In the chat box, type this and press **Return** (Mac) or **Enter** (Windows):

   ```
   /plugin marketplace add bb290/sagavid-1
   ```
3. Then type this and press **Return** or **Enter**:

   ```
   /plugin install sagavid@sagavid
   ```
4. Quit Claude completely and open it again (Mac: **Command + Q**; Windows: close the window, then right-click Claude in the bottom-right tray and click **Quit** if it's there). Open the **Code** tab again.

### Step 4. Let Claude set up your computer

In the **Code** tab, type this and press **Return** or **Enter**:

```
/sagavid:setup
```

Claude checks your computer and installs only what's missing: the video tools, Google Chrome, Google Drive for desktop, and the video engine. It tells you what it's doing at each step. Some steps take 5 to 15 minutes; leave Claude open while it works.

If Claude asks for permission to run a command, click **Allow**.

**When Claude asks for your help, it's one of these:**

| What pops up | What to do |
|--------------|------------|
| **Mac:** a box asking to install **Command Line Developer Tools** | Click **Install**, then **Agree**, and wait until it finishes. |
| **Mac:** the **Homebrew** installer | Click **Continue** through it. When it asks, type your Mac password in the installer window (not in the chat). Tell Claude when it says the installation was successful. |
| **Windows:** "Do you want to allow this app to make changes to your device?" | Click **Yes**. |
| **Google Drive** sign-in | Sign in with your **Sagareus** Google account, then tell Claude you're done. |
| A box titled **Sagareus video setup** (Mac) or a **password box** (Windows) | Open 1Password, go to **Property Access**, search **ElevenLabs**, and copy the key. Paste it into the box and click **OK**. Nothing shows when you paste; that's normal. |
| **Asana** isn't connected | Redo Step 2, then tell Claude. |

When it's finished, Claude shows a checklist. Everything should say done. If it says you're not on the **Video Content** shared drive, ask Brittany to add you, then type `/sagavid:setup` again (it skips everything that's already done).

On Windows, if Claude installed anything, quit Claude completely and open it again.

### Step 5. You're set up

To make a video, type `/sagavid:listing-video` or `/sagavid:before-after` in the **Code** tab. Claude asks which Asana card the video is for: paste the card link, or say **new** and Claude makes one. The rest is in [SagaVids -1](https://sagareus.getoutline.com/doc/sagavids-1-MBhNsUEbSF).


---

### Getting updates

When Brittany says there's an update, type this in the **Code** tab and press **Return** or **Enter**:

```
/plugin marketplace update sagavid
```

Restart Claude if it asks.

### If something goes wrong

You can run `/sagavid:setup` again at any time. It checks everything and fixes what's missing.

| What you see | What to do |
|--------------|------------|
| `/sagavid:setup` isn't recognized | Redo Step 3, and make sure you quit and reopened Claude. |
| Claude says **No ElevenLabs key** | Type `/sagavid:setup` again; Claude opens the key box again. |
| Claude says it **can't find the Video Content shared drive** | Open Google Drive for desktop and check you're signed in with your Sagareus account. If **Video Content** still doesn't show under Shared drives, ask Brittany to add you. |
| The video won't render, or Claude mentions **Chrome** | Type `/sagavid:setup` again. |
| Anything else | Take a screenshot of the Claude window and send it to Brittany. |

## Making a video

Everything happens in the Claude app's **Code** tab. Not set up yet? See Setup above.


1. **Type the command**: `/sagavid:listing-video` + the Buildium link, or `/sagavid:before-after`.
2. **Pick the Asana card.** Paste the card link from the Video Production board, or say **new** and Claude makes one. Every video has a card, and Claude keeps it up to date (In Progress, a short comment at each checkpoint, then Draft) so the board always shows where each video is.
3. **Give Claude the material.** Drag files into the chat or paste Drive links (if it's already on the card, Claude takes it from there).
   1. For a listing:
      1. All 3 styles: Buildium listing link + walk thru video
   2. For a before/after:
      1. Junk and Trashed styles: move-out video(s) or photo(s), listing walkthrough video and/or photos, and the link to the relevant SOP
      2. Reno style: before/during/after videos and/or photos; 1-2 sentences about whats happening
4. **Answer Claude's questions**
   1. This is the only time you're asked for facts, so answer from what you know: what the floors are, what's new, which photos are staged or edited.
   2. For a before/after, Claude writes the voiceover script from the SOP; you read it and record it, then drag the recording into the chat.
5. **Make edits on the storyboard.** Claude sends a link; comment on any frame, or say "approved" in the chat.
   1. Rotated images
   2. Double check for personal info
   3. Remove dates that show a long turn over (or anything else that makes us look bad)
6. **Watch the preview**
   1. Prompt any last changes
7. **Tell Claude it's Done.**
   1. Claude saves the video to Video Content / Finals and moves the card to **Draft** on the Video Production board with a **Final Approval** subtask for Brittany F.
   2. She approves & moves to Approved
   3. Automation pulls approved videos +schedules it to post to Instagram, Facebook, YouTube, LinkedIn, and Google Business Profile, and moves the card to **Shipped**.

Your videos are kept in `Documents/Sagareus Videos/` on your computer.

## What the video never shows

Rent, deposit, specials, availability date, fees, screening criteria, utility costs, pet terms, lease terms, your name or number, any website. Nothing private (license plates, mail, people, children). No edited photos. Claude enforces all of this; if it flags something, it is on purpose.

## For maintainers

- `lib/sagavid.py`: shared paths (videos folder, the Video Content shared drive via Drive for desktop) and the ElevenLabs calls (key from `ELEVENLABS_API_KEY` or `~/.sagavid/.env`, passed to curl on stdin so it never shows on a command line).
- `skills/setup/`: `/sagavid:setup`, which sets up a staff Mac or PC from inside Claude Code (Homebrew from its .pkg on a Mac, winget on Windows, Chrome, Drive, HyperFrames, the ElevenLabs key through a hidden pop-up so it never enters the chat). The Outline page Set Up // SagaVids-1 mirrors the Setup section above.
- `skills/before-after/`: the Junk, Trashed and Reno before/after builds (`build_ba_junk.py`, `build_ba_trashed.py`, `build_ba_reno.py`), voice, captions and music scripts, each style's own track, sfx and fonts. Scripts come from the SOP the staff member links (Reno: the card's note on the work); no positions file ships with the plugin.
- Layout: `.claude-plugin/` (plugin and marketplace manifests), `skills/listing-video/` (SKILL.md, `scripts/`, `assets/fonts` Fraunces SIL OFL, `assets/music` the two approved tracks, `template/` the HyperFrames project files).
- This repo is the one video flow for everyone, Brittany included (2026-11-25): there is no separate copy of these skills to keep in sync.
- Bump `version` in `.claude-plugin/plugin.json` when you change anything, so staff get the update.
