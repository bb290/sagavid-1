---
name: listing-video
description: Make a Sagareus listing video at your desk. Paste a Buildium rental listing link (plus any walkthrough clips) and get a finished 20-to-25-second vertical video in one of three approved styles (Fast tour, Auto-slide, Editorial), then hand it to Brittany on the Asana Video Production board for Final Approval. Use on "/listing-video <buildium link>", "make a listing video for <address>", or "listing video for this unit".
---

# Listing Video (staff edition)

One Buildium listing in, one finished vertical listing video out, made on your own computer. You (the leasing agent) approve the shot list and the cut here in the chat; then the video goes onto the Asana **Video Production** board, assigned to Brittany for Final Approval. When Brittany moves it to **Approved**, it is scheduled to Instagram, Facebook, YouTube, LinkedIn and Google Business Profile. You never post anything yourself.

Talk to the staff member in plain words. They are not video editors or developers: run every command yourself, explain what you are doing in a sentence, and show them results (open the preview, open the video). Never ask them to edit a file.

The scripts live in this skill's folder (the "Base directory for this skill" shown when the skill loads). Below, `$SKILL` means that folder; quote it in commands, the path can have spaces. Videos are saved to `~/Documents/Sagareus Videos/<address>/` (override with the `SAGAVID_HOME` environment variable). HyperFrames runs as `npx --yes hyperframes@0.8.204` (written `hf` below).

## Styles

| Style | Asana Style field | Look | Build |
|---|---|---|---|
| listing1 | Fast Tour | 6 to 8 photos at 5 beats each, big stacked uppercase labels that enter differently on every slide, facts on the title only, upbeat house track | `build.py` |
| listing2 | Auto-Slide | One long Off-White canvas, a panel per room, photos as white-framed cards that cross the seams, Emerald callout pills, the camera holds 5 beats and swipes on the beat | `build_listing2.py` |
| listing3 | Editorial | Full-screen photos with a slow push-in and soft cross-fades, lower-third type on a soft dark-grey backing, a spaced Inter kicker over a Fraunces title in sentence case with an italic accent, Off-White end card, calm acoustic track | `build_listing3.py` |

Each build script's docstring holds the full `shots.json` schema with an example. Read it before writing shots.json.

**Which style:** if the Asana card for this listing already has a Style, use it. Otherwise look at the most recent Listing card on the board that has a Style and use the next one in the order Fast Tour, Auto-Slide, Editorial (never the same twice in a row). Tell the staff member which style and why; they can pick another.

## Rules (never break these)

- **Audience: prospective residents.** Resident voice, short and concrete.
- **Brand:** Emerald `#0B4F42`, Off-White `#F5F0E8`, White, ink `#1a1a1a`, Inter; Fraunces only for listing3 titles. No logo, no other colours. The build scripts already do this; never restyle.
- **Every label comes from the listing page or from the staff member.** What they confirm about the unit ("new fridge and dishwasher") goes in `shots.json` `notes` and counts as a fact. If the listing and the photos disagree, use the weaker claim (listing says "hardwood", floors are vinyl plank: say "vinyl plank floors" or "new floors") and tell them.
- **Never on screen:** rent, deposit, specials or rent credits, availability date, fees, screening criteria, utility costs, pet terms, lease terms, the agent's name, phone numbers, any URL. The video must stay accurate until the unit leases.
- **Fair Housing:** describe the home, never the ideal resident (no "perfect for families", "great for students", "young professionals").
- **No alterations to the property:** no sky replacement, staging, or object removal. Never use a listing photo that looks edited (a fire added to a fireplace, a blue sky when the walkthrough shows grey). Leave it out and tell the staff member.
- **Marketed cities only:** the 30 marketed cities plus Tacoma. `gather.py` stops on anything else; tell the staff member to check with Brittany.
- **Nothing private in frame:** license plates, mail, residents' faces, family photos. No children, ever.
- No em dashes and no emojis anywhere you write: on screen, in Asana.
- **Nothing posts from here.** This skill ends at the Asana hand-off.

## Steps

### 1. Gather

```
python3 "$SKILL/scripts/gather.py" <buildium listing url>
```

It prints the folder it made and writes `source/listing.json` (facts, description, amenities) and every photo as `source/photos/pNN.jpg`. Look at every photo yourself (read the files): what each room shows, which are exteriors, anything private or edited.

**Walkthrough clips (optional):** ask if there is a phone walkthrough. They can drag the files into the chat or give a Google Drive (desktop) path; copy them into `source/clips/`. Make a contact sheet to find steady stretches: `ffmpeg -i <clip> -vf "fps=1,scale=180:320,tile=9x3" -frames:v 1 boards/walk-sheet.jpg`, then look at it. Pick stretches without hands, arms, or the filmer in a mirror. Never use the clip's sound.

### 2. Shot list, then check with the staff member

Write `shots.json` in the listing folder for the chosen style (schema in the build script):

- **Cover / title** (from frame 0, it is the cover): front exterior or the best room, "For rent", the neighbourhood and city, and "N bed · N bath · N sq ft".
- **6 to 8 rooms and features** in walking order: entry, living, kitchen, bath, bedrooms, then building features (laundry, parking, storage, deck, a park nearby). Labels short: 2 words per line where possible.
- **End card:** "Schedule your tour today." and "Managed by Sagareus Property Management." Nothing else.
- Photo pans `x0` to `x1` (0 = left edge, 1 = right edge): point them at what the label names.

Then show the staff member a plain list: each slide's photo (by room), its words, and anything you are unsure of (a claim the photos can't prove, a photo you left out and why). Ask them to confirm or correct. Their confirmations go in `notes`.

### 3. Music

Total beats: add up every scene's beats (listing1: 4 + 5 per shot + 7; listing3: cover + 6 per shot + 7; listing2: every hold plus one beat per swipe).

```
python3 "$SKILL/scripts/music.py" <folder> <total beats>
```

It uses the approved house track for Fast Tour and Auto-Slide and the approved acoustic track for Editorial, and cuts it on the beat. It stops if the video is longer than the track (about 28 s): drop a shot.

### 4. Build, look, preview

```
python3 "$SKILL/scripts/build_listing3.py" <folder>     (or build.py / build_listing2.py)
cd <folder> && hf check
hf snapshot --at <the middle of every scene> --json
```

Fix every `check` error. Look at every snapshot yourself before showing anyone: text over a busy background, a pan that drifts onto a window with a street, a car, or a person, a pan that misses what the label names. Fix in shots.json and rebuild.

Then open the preview for the staff member: `hf preview` (it opens in their browser). Say: press play; tell me anything to change in plain words. Apply their changes to shots.json and rebuild (never edit the files the preview shows; a rebuild overwrites them). Repeat until they say it is good.

### 5. Render and level

```
hf render -o ../raw.mp4
cd .. && ffmpeg -y -i raw.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k <folder>.mp4 && rm raw.mp4
ffmpeg -i <folder>.mp4 -af ebur128 -f null - 2>&1 | tail -12
```

It should measure about -14 LUFS. Pull a 2-frames-per-second contact sheet (`ffmpeg -i <folder>.mp4 -vf "fps=2,scale=180:320,tile=10x5" -frames:v 1 boards/render-sheet.jpg`) and look at it. Then `open <folder>.mp4` so the staff member watches the final file. You cannot hear: say the sound was measured, not listened to. Ask: is this ready for Brittany?

### 6. Hand off to Brittany (Asana)

Only after the staff member says it is ready.

1. **Drive:** copy the MP4 to the shared drive's Finals folder as `<YYYY-MM-DD> Listing <street address> <City> (<Style>).mp4`. Find the folder with Google Drive for desktop: `ls ~/Library/CloudStorage/GoogleDrive-*/"Shared drives/Video Content/Finals"` on a Mac (on Windows, the `G:` drive's `Shared drives\Video Content\Finals`). Get the file's link: wait a few seconds for it to sync, then on a Mac `xattr -p 'com.google.drivefs.item-id#S' "<file>"` gives the id for `https://drive.google.com/file/d/<id>/view`. If that fails, ask the staff member to right-click the file in Drive, copy the link, and paste it.
2. **The card** on the Video Production board (Asana project `1219918573321945`), through the Asana connector:
   - Look for an existing card for this address (search the project's tasks for the street number and name). Use it if there is one; otherwise create one named `Listing - <address>, <City>` in the project.
   - Set the custom fields: Video Type (`1219918701563115`) = Listing (`1219918701563116`); Style (`1219938203421150`) = Fast Tour `1219938203421151`, Auto-Slide `1219938203421152`, or Editorial `1219938203421153`; Video Status (`1219918573486131`) = Draft (`1219944386978126`).
   - Move it to the **Draft** section (`1219944273290688`).
   - Assign the card to Brittany (`bb@sagareus.com`).
3. **Final Approval subtask** on the card, assigned to Brittany (`bb@sagareus.com`), with a description:
   - The Drive link and the Buildium listing link
   - Style, length, measured loudness
   - Made by `<staff member's name>`, approved by them on `<date>`
   - Anything to confirm (a claim, a photo left out and why, a listing detail that looks wrong)
   - `--- Claude Video Editor` on its own last line
4. If you could not set a field or section, say exactly which one and leave it for Brittany; never create or change Asana fields.

Tell the staff member it is with Brittany, with the card link. Done.

## Gotchas

- Buildium sometimes includes a small duplicate exterior; the build scripts refuse photos under 1200 px on the short side. Use another photo.
- Longer holds mean slower pans that reach further than you expect: check the last frame of every pan in a snapshot.
- Residents' belongings in shared spaces (detergent in a laundry room): ask the staff member.
- Label fonts shrink to fit the longest line; keep lines to about 10 characters for the big look (listing1).
- `gather.py` without Pillow skips the photo contact sheet; read the photos directly instead.
- If `hf render` complains about Chrome, run `hf browser` (or `hf doctor`) and follow what it says.
