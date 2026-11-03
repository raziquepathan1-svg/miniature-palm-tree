# Islamic channel: Ali aur Dadu (style guide)

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
- No music. Subtitles are added in editing, never asked from Flow.
- A new story each time, never the same video with small changes.

## Uploading
Finished videos go in `upload_queue/<date>-<name>/` (video.mp4, meta.json, optional thumbnail.jpg) and are
uploaded scheduled by the "Islamic channel - upload videos" workflow. One-time login: `SETUP.md`.
