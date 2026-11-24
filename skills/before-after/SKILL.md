---
name: before-after
description: Make a Sagareus before/after video at your desk from a Video Production card in Asana. Three styles (Junk, Trashed, Reno), 30 seconds or less, the staff member's own voice reading a script Claude writes in Brittany's voice from the SOP on the card (Reno: from the card's note on the work), then hand it to Brittany on the board for Final Approval. Use on "/before-after <asana card link>", "make a before/after video", or "before and after for this card".
---

# Before/After Video (staff edition)

One Video Production card in, one finished vertical before/after video out, made on your own computer. You (the staff member) check the storyboard, record the voiceover, and approve the preview here in the chat; then the card goes to **Draft** with a **Final Approval** subtask for Brittany. She approves and moves it to **Approved**, and the automation schedules it to Instagram, Facebook, YouTube, LinkedIn and Google Business Profile. Nothing posts from your computer.

Talk to the staff member in plain words. They are not video editors or developers: run every command yourself, say in a sentence what you are doing, and show results (open the storyboard, the preview, the video). Never ask them to edit a file.

`$SKILL` below means this skill's folder (the "Base directory for this skill" shown when it loads); quote it, the path can have spaces. Videos are saved to `~/Documents/Sagareus Videos/<card name>/` (override with `SAGAVID_HOME`). HyperFrames runs as `npx --yes hyperframes@0.8.204` (written `hf`). The plugin root is two folders up from `$SKILL`; its `VOICE.md` is the voice rule.

## Styles

| Style (Asana Style field) | For | Look | Build |
|---|---|---|---|
| Junk | A move-out where belongings were left behind | Stickers and hand-drawn circles on the junk; the first half is junk only (nothing moves until the resident confirms in writing); then **the Sweep**, an Emerald squeegee bar that wipes each spot clean; deep clean flurry | `build_ba_junk.py` |
| Trashed | A move-out where the unit is trashed or unsafe | Striped Emerald and Off-White "Stop at the door" tape; before shots through a camera viewfinder with a photo count out of 10; photos stack into the owner email; then **the Roll-up**, an Emerald roll-up door that drops on the trash out and opens on the finished room; inspection clipboard | `build_ba_trashed.py` |
| Reno | A bigger repair or upgrade (flooring, mold remediation, kitchen or bath remodel) | Move-out / Repair / Rent ready tracker on top (never dates); move-out report photos as report cards; ink "Repair · not optional" and Emerald "Upgrade" marks on the work photos; then **the Plank lay**, the finished room laying in row by row; the same spot three ways | `build_ba_reno.py` |

Every style ends the same: "Safe. Clean. Working. Warm." one word at a time, then the **Rent Ready** stamp, then the Off-White Sagareus end card. Each build script's docstring holds its `episode.json` schema; read it before writing one. The approved samples (Junk 4703 Beach Dr SW, Trashed 8216 #1, Reno 14426 Beverly Park #2) are on the Outline guide "SagaVids -1".

## Rules (never break these)

- **The source is strict.** Junk and Trashed: the card must have the SOP link, and every step and claim in the script comes from that SOP or the footage. Reno: there must be 1 to 2 lines about what is happening in the video, and every claim comes from that note or the footage. **Missing from the card: ask for it in the chat** (step 1), then add the answer to the card. No video starts without it, and you never fill the gap yourself: never add a step, deadline, law, or claim the source doesn't have.
- **30 seconds or less, end card included.** About 60 to 65 spoken words. Cut lines, never speed up the voice.
- **Brittany's voice, the staff member's recording.** Write the script by `VOICE.md`. Never generate a voice (no text-to-speech, not even as a placeholder or timing guide). No recording yet: stop and ask for one.
- **Audience: property owners.** Say "resident", never "tenant". Jokes land on the mess, never on the people.
- **Never:** deposits, charges, deductions or what a move-out cost anyone; rent, fees, screening criteria; unit numbers, house numbers, street signs, license plates; mail, notices or other paperwork; residents' faces, children, family photos; staff names; dates that show a long turnover (or anything else that makes us look bad); legal advice (say "Washington's strict on this", never cite a statute).
- **Footage only has to illustrate the point:** the before and after can be from different dates. Don't flag that or whose items are in frame; the never-show list above still applies.
- **No alterations:** never edit a photo's content (rotating a sideways photo is fine and expected).
- **Brand:** Emerald `#0B4F42`, Off-White `#F5F0E8`, White, ink `#1a1a1a`, Inter. The build scripts already do this; never restyle.
- No em dashes and no emojis anywhere you write: on screen, in captions, in Asana.

## Steps

### 1. Read the card

The staff member pastes the Asana card link. Through the Asana connector read the card: name, description, custom fields (Video Type should be Before/After; Style is Junk, Trashed or Reno) and attachments.

- **Read linked tasks too.** If the card links another Asana task (a Turn Over, Move Out or maintenance task), read it and its comments and subtasks for context before asking anything: what was found, what was done, which rooms, repair or upgrade. Use only what the work was; never costs, quotes, who paid, owner or vendor names, or dates (they stay off screen and out of the script). Write the Reno note from it yourself and show it to the staff member to confirm.
- **Check what's there first.** If anything needed is still missing, ask for all of it in the chat in one message, in plain words, and wait for the answer. Don't tell them to go edit the card. Needed:
  - **Junk, Trashed:** the SOP link. Ask them to paste it ("Which SOP does this video show? Paste the Outline link."). If they don't know which one, ask what happened at the move-out and suggest the SOP that fits, then ask them to confirm. No SOP link, no video.
  - **Reno:** the note. Ask: was it a forced repair, an optional upgrade, or both (this picks the "Repair · not optional" or "Upgrade" mark); what was done, in which rooms; and for a repair, what was found (water damage, mold, a soft subfloor). Their answer is the note. No note, no video.
  - **Style** blank or **Video Type** not Before/After: ask which style (Junk, Trashed, Reno; one line on each from the Styles table).
  - **Media:** no before or no after footage on the card or behind its links: ask them to drag it into the chat or paste the link.
- **Write their answers onto the card** as a comment (the SOP link, or "Reno note: ...", and the style), signed `--- Claude Video Editor`, so Brittany sees the source at Final Approval. Set the Style field only if it was blank.
- **Move the card to In Progress** once you have the source: Video Status (`1219918573486131`) = In Progress (`1219918573486133`) and the **In Progress** section (`1219918704893858`). The board's columns are: New (plan and gather footage), In Progress (building with Claude), Draft (Final Approval), Approved (ready to ship), Shipped.
- **Get the media** into `~/Documents/Sagareus Videos/<card name>/source/`: Asana attachments by their download link; Google Drive links through Google Drive for desktop (find the file by name under `~/Library/CloudStorage/GoogleDrive-*/`, on Windows the `G:` drive) and copy it in. If a file can't be found, ask the staff member to drag it into the chat. Videos go in `source/clips/`, photos in `source/photos/` (or `during/` for Reno work photos), a move-out report PDF in `source/report/` (pull its photos with `pdfimages -j -p`; use only its photos, never its text).
- **Read the SOP** (Junk, Trashed) through the Outline connector if there is one; otherwise ask the staff member to paste the SOP text into the chat.

### 2. Questions, then the script

Ask only what you still need, once (skip anything step 1 already answered): what the main problem was, what was done, anything the footage can't show. This is the only time they're asked for facts.

Look at the footage: 1 frame per second contact sheets (`ffmpeg -i <clip> -vf "fps=1,scale=180:-2,tile=8x6" -frames:v 1 boards/<clip>-sheet.jpg`; one tile per second, read left to right) and full-size stills at the moments you might use. Find **matching angles** (the same spot filmed from the same place at move-out and at listing), the worst before shots, and anything from the never-show list (hands, the filmer's shadow, paperwork on doors, faces). Phone video is often HDR; the build handles it.

Write the script by `VOICE.md`: 6 to 9 short lines, about 60 to 65 words, her openers and "okay?", plain words, the source's steps in order, ending "Safe, clean, working, warm." and "Good to go. Rent ready." Mark lines that are nearly hers verbatim with ★.

### 3. Storyboard, then STOP for edits

Publish the storyboard as an Artifact they can comment on (Brittany, 2026-11-24), never as a local file: one card per beat with the still, the on-screen text (stickers, tape, marks, captions), and the script line under it, in the style's look (see the samples), with anything to confirm in a box at the top. Turn comments on: `capabilities: {"comments": {"composer_only": true}}`, each card marked `data-comment-target`, with a Comment button that calls `openComposer({element: card})`. Give them the link. Tell the staff member to check three things, as Brittany's process says, and to comment on any frame:

1. **Rotated images** (report and phone photos are often sideways or upside down: rotate the source file with ffmpeg, `ffmpeg -y -i in.jpg -vf transpose=1 out.jpg` for 90° clockwise, `transpose=2` counterclockwise, `transpose=1,transpose=1` for 180°; look at it after).
2. **Personal info** (names, unit or house numbers, plates, mail, notices, faces).
3. **Dates or anything that makes us look bad** (a long turnover, a mess blamed on someone).

Read their comments (ArtifactComments), apply them, republish to the same link, and resolve each thread you acted on. When they're happy, give them the script to record.

### 4. Recording

Recording tips: somewhere soft and quiet (a closet or a parked car), phone close, 3 seconds of silence first, a short pause between lines; flubbed a line, pause and say the whole line again; say a line their own way if it sounds stiff. They drag the recording into the chat.

```
python3 "$SKILL/scripts/voice.py" <folder> <recording>
```

It cleans the voice (ElevenLabs Voice Isolator), gets word timings (Scribe), and caps the pauses. Read the printed words: rerun with `--cut START-END` (raw-recording seconds) for every retake, stumble, or stray "hello", keeping the last clean take. If the voice runs over about 27 s, cut whole lines with `--cut` and add `--max-sent 0.3 --max-gap 0.22`. Reno only: insert short silences where the music should carry a moment (the plank lay, the same spot three ways), as in the sample (1.2 s and 1.6 s).

### 5. Build, music, preview

Write `episode.json` for the style (schema in the build script's docstring; the samples' episode.json files are the reference). Time things to the words. Then:

```
python3 "$SKILL/scripts/build_ba_<style>.py" <folder>
python3 "$SKILL/scripts/music.py" <folder> <total seconds> --style ba-<style>
python3 "$SKILL/scripts/build_ba_<style>.py" <folder>
cd <folder> && hf check
hf snapshot --at <the middle of every scene, every sticker and mark, every transition> --json
```

The first build writes the music sync point; `music.py` fits the style's track so its lift lands on this video's big moment (Trashed: the roll-up opening; Reno: the first plank row; Junk just trims to the end); the second build picks up the music. Fix every `check` error. Look at every snapshot yourself before showing anyone: stickers and circles on the right thing (the camera moves; nudge positions), text over busy spots, captions clashing with overlays, anything from the never-show list. Fix in episode.json and rebuild.

Then `hf preview` (opens in their browser): press play, tell me anything to change in plain words. Apply changes to episode.json and rebuild. Repeat until it's right.

### 6. Render and level

```
hf render -o ../raw.mp4
```

Level it to -14 LUFS with two passes (measure with `loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json`, then apply with the measured values and `linear=true`; video copied, AAC 192k, 48 kHz). Check the length is 30.0 s or less. Pull a 2-frames-per-second contact sheet and look at it, then `open` the MP4 so the staff member watches the final file. You cannot hear: say the sound was measured, not listened to. Ask: is this ready for Brittany?

### 7. Done: hand off to Brittany (Asana)

Only after the staff member says it's done.

1. **Drive:** copy the MP4 to the shared drive's Finals folder as `<YYYY-MM-DD> Before-After <Style> - <short title>.mp4` (`~/Library/CloudStorage/GoogleDrive-*/"Shared drives/Video Content/Finals"` on a Mac, the `G:` drive's `Shared drives\Video Content\Finals` on Windows). Get its link: on a Mac `xattr -p 'com.google.drivefs.item-id#S' "<file>"` gives the id for `https://drive.google.com/file/d/<id>/view`; otherwise ask the staff member to copy the link from Drive.
2. **The card** (the one from step 1, Video Production project `1219918573321945`), through the Asana connector: Video Type (`1219918701563115`) = Before/After (`1219918701563117`); Style (`1219938203421150`) = Junk `1220674551928577`, Trashed `1220674551928578`, or Reno `1220674551928590`; Video Status (`1219918573486131`) = Draft (`1219944386978126`); move it to the **Draft** section (`1219944273290688`); assign it to Brittany (`bb@sagareus.com`).
3. **Final Approval subtask** on the card, assigned to Brittany (`bb@sagareus.com`), with: the Drive link; the style, length and measured loudness; the script as recorded; the SOP link (or Reno note); made by `<staff member's name>`, approved by them on `<date>`; anything to confirm (a claim, a photo left out and why); and `--- Claude Video Editor` on its own last line.
4. If a field or section can't be set, say exactly which and leave it for Brittany. Never create or change Asana fields.

Tell the staff member it's with Brittany, with the card link. Done.

## Gotchas (from the samples)

- **HDR phone video:** the build re-encodes clips and forces standard (bt709) colour tags. If a render ever comes out with overlays missing and greyish colours, the clips still carry HDR tags (HyperFrames switches to HDR compositing and drops overlays): delete `assets/clips/` and rebuild.
- **Clips are cached** by their settings in episode.json; if you replace a source file with the same name (a rotated photo), delete that clip's `.mp4` and `.json` in `assets/clips/` so it's cut again.
- **The camera moves:** a sticker placed on a still drifts off its target. Use short, steady stretches, slow a clip with `"speed"`, or freeze it (`"freeze"`), and check snapshots.
- **Captions** run in the lower third (`caption_top` 1440); keep stickers, marks and the email card above it. A sentence-end missing its period (after a cut) merges two captions: fix the word's text in `tight.json`.
- **Words for anchors:** `"word"` is the first match after the scene starts; use `"word@seconds"` when a word repeats.
- **Music:** each style ships its own track; Trashed and Reno need the build's `assets/music/sync.json`, so build before `music.py`.
- **Report photos** from a move-out report PDF are small (740 px): show them as report cards (Reno), never full screen. Label them by section only ("Carpet"), never with counts you guessed.
- `hf render` complaining about Chrome: run `hf browser` (or `hf doctor`) and follow it.
- **Windows:** run Python as `py` (not `python3`, which can open the Microsoft Store), and `pdfimages` is usually missing: ask the staff member to save the report's photos and drag them in. Drive for desktop is the `G:` drive.
