# Hidaya (Islamic channel, since 2014): Ali aur Dadu style guide

Fixed rules for every Ali aur Dadu cartoon Short. The look of Ali and Dadu comes from clip 3 of the
first Short ("Ali Bismillah bhool gaya", owner approved, 2 Nov 2026).

## Characters (never change)

Reference pictures (add one in Google Flow with "Frames to Video" / "Ingredients" for every clip):
- `characters/ali_and_dadu.jpg`: both together
- `characters/ali_closeup.jpg`: Ali's face
- `characters/dadu.jpg`: Dadu talking

Copy these two lines unchanged into every clip prompt:

```
ALI: cute 7-year-old boy, 3D Pixar style, big round brown eyes, short black hair, chubby rosy cheeks, plain white kurta, small white crochet prayer cap (kufi).
DADU: kind old grandfather, 3D Pixar style, white hair combed back, neat white beard, round thin gold glasses, cream kurta, dark charcoal-grey waistcoat, warm smile.
```

Voices: Google Flow's own voices, speaking Hindi-Urdu. Ali: cheerful child's voice. Dadu: soft, warm old man's voice.

## Backgrounds

One background for all the clips of a reel; the next reel may use another. Copy the same
background line into every clip of that reel.

| Reel topic idea | Background line |
|---|---|
| Food, Bismillah, Alhamdulillah | `Cozy South Asian living room, warm evening light, low round wooden table with roti and daal, floor cushions, patterned rug.` |
| Wudu, cleanliness | `Clean bright home bathroom area with a tap and a small stool, soft morning light, white and blue tiles.` |
| Salam, good manners | `Sunny small courtyard in front of a South Asian house, potted plants, a charpai, blue sky.` |
| Salah, Jumu'ah | `Peaceful masjid courtyard, white marble floor, green trees, soft golden afternoon light (no people praying in the front of the frame).` |
| Kindness to animals, nature | `Green garden with flowers, a small water bowl for birds, morning sunshine.` |
| Sleep duas, night | `Cozy child's bedroom at night, warm lamp light, moon outside the window.` |
| Sharing, honesty, school | `Simple school classroom, wooden desks, a green board, daylight from windows.` |
| Ramadan, Eid | `Living room decorated with lanterns and fairy lights, iftar dates and fruit on the table, evening.` |

## Prompt template (one clip = 8 seconds)

```
3D Pixar-style animated cartoon, vertical 9:16. [BACKGROUND LINE]
[ALI LINE]
[DADU LINE]
Action: [what they do in these 8 seconds].
[Who] says in [voice], in Hindi-Urdu: "[one short line]"
[Camera]. No music, only soft natural sounds. No text or subtitles on screen.
```

- At most 2 short spoken lines per clip (about 6 seconds of speech).
- 4 to 7 clips per Short; the last clip ends with Ali speaking to the viewer.

## Always
- Never show Prophets, Sahaba, angels or Allah. Ali and Dadu only *tell* about them.
- Every hadith or ayah in the description has its reference (sahih sources only).

## Hadith and Quran references (owner's rule, 3 Nov 2026)
Every set of clip prompts starts with a **Source** box, and the same goes in the video description:
- **Book and number**, numbered as on sunnah.com (for example *Sahih Muslim 54*), plus the other main book
  if it has it too (for example *Sahih Bukhari 5376, Sahih Muslim 2022*)
- **Narrator** (for example *Abu Hurairah (RA)*)
- **Grade**: sahih (or hasan, said plainly); no weak or fabricated hadith
- **The words**: short Arabic if well known, the Hindi-Urdu meaning, and an English line
- For the Quran: *Surah name, surah:ayah* (for example *Surah An-Nisa 4:86*)
- What Dadu says in a clip must match the source's meaning; a paraphrase is called "is ka matlab hai",
  never quoted as the exact words

Sources used so far:
| Video | Source |
|---|---|
| Ali Bismillah bhool gaya | Umar ibn Abi Salamah (RA): "Ya ghulam, sammi Allah, wa kul bi yaminik, wa kul mimma yalik" - Sahih Bukhari 5376, Sahih Muslim 2022 (sahih). Forgetting Bismillah: "Bismillahi awwalahu wa akhirahu" - Aisha (RA), Sunan Abu Dawud 3767, Jami at-Tirmidhi 1858 (sahih) |
| Ali aur Salam | Abu Hurairah (RA): "...Shall I not tell you something that, if you do it, you will love one another? Spread salam among yourselves" - Sahih Muslim 54 (sahih). Answering a greeting: Surah An-Nisa 4:86 |
- No music. Subtitles are added in editing, never asked from Flow.
- Masjid scenes: shoes come off at the door (shoe rack); nobody walks inside the masjid with shoes or slippers.
- A new story each time, never the same video with small changes.

## Uploading
Finished videos go in `upload_queue/<date>-<name>/` (video.mp4, meta.json, optional thumbnail.jpg) and are
uploaded scheduled by the "Islamic channel - upload videos" workflow. One-time login: `SETUP.md`.

## Family characters (added 5 Nov 2026)
Reference pictures: `characters/family.jpg` (all five together, owner approved 9 Nov 2026; the ONE picture to add in
Google Flow for every family reel), plus `characters/ammi.jpg`, `abbu.jpg`, `zara.jpg` for single-character close-ups.
Ali + Dadu only reels keep using `characters/ali_and_dadu.jpg`.
Owner's rule (9 Nov 2026): Ammi always in full, loose Islamic dress (khimar over chest + loose abaya); nothing fitted, chest never shown or shaped. Never change her clothes between clips.
Copy unchanged into prompts, like Ali and Dadu:
```
AMMI: kind young mother, 3D Pixar style, warm brown eyes, gentle smile, wearing a long light-blue khimar (Islamic head covering) that covers all her hair, neck and chest and falls loosely down to her waist, over a loose, plain, long navy-blue abaya with long sleeves down to her wrists and length down to her ankles; the dress is wide and loose, not fitted, no body shape visible, only her face and hands are visible.
ABBU: friendly father in his thirties, 3D Pixar style, short neat black beard, short black hair combed back, plain light-grey kurta and shalwar, white prayer cap only when going to the masjid.
ZARA: Ali's little sister, cute 4-year-old girl, 3D Pixar style, big round brown eyes, chubby rosy cheeks, black hair with a soft pink embroidered dupatta over her head, pink kameez with white shalwar, often holding a small brown teddy bear.
```

## Long videos (CoComelon style)
- Every week: the week's reels joined into one wide 16:9 video (intro card, "Kahani 1/2/3" cards, outro),
  vertical reels placed on a soft blurred background; the description lists every story's source.
- Every month: a 30+ minute compilation of all the month's stories.

## Owner's rule (10 Nov 2026): no approval step
When the owner's clips arrive, make the reel and upload it straight away (next free 5 PM India slot);
send the owner the finished video and the link, don't ask "upload?" first.

## How the owner sends clips (11 Nov 2026)
As comments with attached clips on GitHub issue #12 "Hidayah clips" (the comment button waits for uploads,
so nothing is lost). The upload page islamic_channel/inbox saved several empty commits from the phone; don't
send the owner there. A Drive folder is not possible (no Drive space).
