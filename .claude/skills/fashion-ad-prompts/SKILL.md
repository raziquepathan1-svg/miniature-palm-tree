---
name: fashion-ad-prompts
description: Write AI video prompts for the user's men's fashion Instagram page using their avatar. Use whenever the user asks for a video prompt, clip prompt, reel prompt, outfit prompt, fashion prompt, or "give me N prompts" for their page.
---

# Men's fashion ad-clip prompts (avatar)

The user runs a men's fashion Instagram page. Every video features **their own AI avatar** wearing outfits, styled like a **short premium clothing brand ad**. They post 2–3 Reels a day. They write in simple English, so reply in simple, clear English.

## Hard rules (apply to every prompt)

1. **Men's fashion only.**
2. **Cinematic multi-shot ad, not a single walking clip.** Every prompt has **3–4 shots**, about 12–15 seconds total, with timings. Mix actions and angles, for example:
   - Wide shot: walking / entering the scene (tracking camera)
   - Medium shot: sitting (bench, café, sofa, car, steps), relaxed pose
   - Detail close-ups: slow-motion fabric texture, collar, buttons, stitching, shoes
   - Hero shot: standing up, adjusting jacket/collar/cuffs, looking into camera (low angle)
   The clothes are the product. The shots must show the outfit clearly the way a brand ad does: fit, fabric, details, full look.
3. **Same face every time.** Every prompt starts with the IDENTITY LOCK block below and ends with the AVOID line.
4. **Watch on the wrist, never featured.** He always wears a watch on his left wrist, but no shot focuses on it, checks it or shows it off.
5. **No religious backgrounds or names except Islam.** The user is Muslim. Never use Hindu, Christian or other religious festivals, symbols, temples, diyas, marigold puja decor, crosses, etc. Islamic or neutral settings are fine (Eid, Jumma, Nikah, marble arches, lanterns, crescent moon), but most prompts should simply use neutral modern settings.
6. **No gold jewelry on him** (many Muslim men avoid it). Use silver, steel or none. Embroidery in silver, ivory or tonal thread.
7. **Brand-worthy outfits.** Pick clean, premium, well-fitted outfits that real menswear brands would want to collaborate on after seeing the page: smart casual, old money, quiet luxury, minimal streetwear, modern ethnic (kurta, pathani, Nehru jacket, sherwani), modest wear (thobe), formal tailoring, seasonal layering. Describe each piece exactly: color, fabric, fit, details, shoes. No visible brand logos or brand names in the prompt.
8. **Don't repeat.** Vary outfits, colors, locations and shot actions from earlier prompts in the conversation.
9. **Vertical 9:16, photorealistic, luxury commercial look** (cinematic color grading, shallow depth of field, smooth camera movement).

## IDENTITY LOCK block (paste at the start of every prompt)

```
IDENTITY LOCK: Use the uploaded reference image as the only identity source for the face and body. Ignore the clothes in the reference image. The same man appears in every shot: a man in his late 20s, warm wheatish skin, oval face with strong cheekbones, thick dark eyebrows, dark brown eyes, full dense black beard of medium length with a connected moustache, shoulder-length wavy dark brown-black hair parted near the middle and falling loosely around his face, tall muscular athletic build with broad shoulders and naturally hairy forearms. Keep face, beard, hair, skin tone and body exactly identical to the reference in all shots, from every camera angle.
He wears a silver watch with a black dial on his left wrist naturally. Do not focus on or show off the watch; it is just part of the outfit.
```

These details come from the user's avatar reference images. Use this block exactly as written; do not ask for the details again.

## Reference images (in `references/`)

| File | View | Use for |
|---|---|---|
| `01-front-original.jpg` | Front, navy scrubs, green background | Original avatar (clothes must be ignored) |
| `02-three-quarter-left.jpg` | ¾ view, black tee, grey background | Walking and side-angle shots |
| `03-three-quarter-right.jpg` | ¾ view (other side), black tee | Sitting and turning shots |
| `04-side-profile.jpg` | Side profile, black tee | Profile and tracking shots |
| `05-full-body-front.jpg` | Full body, black tee, grey jeans, white sneakers, silver watch on left wrist, smiling | Best main reference: body shape, height, watch |

When writing prompts, remind the user to upload **05 + 02 + 03** as character references (and 04 for profile-heavy shots). Never use 01 (scrubs) as a reference for fashion clips.

## The user's tool: Google Flow (Veo)

- The user makes videos in **Google Flow** with **Ingredients to Video**, which takes up to **3 reference images**: use 05 (full body), 02 (¾ left) and 03 (¾ right).
- Each Flow clip is about **8 seconds**, so a 15-second, 4-shot ad cannot be made in one generation. Write each ad as **2 Flow clips of 2 shots each** (Clip A = shots 1–2, Clip B = shots 3–4), each a separate copy-paste block with the full IDENTITY LOCK, the same outfit line and the AVOID line, so the user can generate them one by one with the same 3 ingredients.
- The user then joins the clips in Flow's Scenebuilder or in CapCut.

## AVOID line (paste at the end of every prompt)

```
Avoid: face changing between shots, different person, face morphing, changed beard or hair, distorted hands, extra fingers, blurry face, wrinkled or glitchy clothes, cartoon look, text or logos.
```

## Prompt template

```
[IDENTITY LOCK]
Outfit: <each piece: color, fabric, fit, details, shoes>.
Cinematic fashion ad, 4 shots, 15 seconds total:
Shot 1 (0-4s): Wide shot. <walking/entering, camera move, light>.
Shot 2 (4-8s): Medium shot. <sitting pose, small action, camera move>.
Shot 3 (8-11s): Detail close-ups. <slow-motion fabric, collar/buttons/stitching, shoes>.
Shot 4 (11-15s): <stands, adjusts outfit, looks into camera>. Low-angle hero shot.
Style: premium menswear brand commercial, <color grade/light>, shallow depth of field, smooth camera movement, vertical 9:16, photorealistic.
[AVOID LINE]
```

## Each prompt in the reply also gets

- A title (e.g. "Prompt 16: Quiet luxury ad (knit polo)"), continuing the numbering from earlier in the conversation.
- **Hook:** one short on-screen text line with 1 emoji.

## End of reply

Add short tips only if useful (e.g. if the tool can't do multi-shot, generate each shot separately with the same reference photo + identity lock + outfit line, then join them in CapCut/InShot and cut on the music beat). Offer one next step (captions + hashtags, or a CapCut editing plan).
