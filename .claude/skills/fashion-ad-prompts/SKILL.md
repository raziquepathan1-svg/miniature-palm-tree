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
IDENTITY LOCK: Use the uploaded reference image as the only identity source. The same man appears in every shot: [age], [skin tone], [face shape], [beard style], [hairstyle], [build]. Keep face, beard, hair, skin tone and body exactly identical to the reference in all shots, from every camera angle.
He wears a silver watch with a black dial on his left wrist naturally. Do not focus on or show off the watch; it is just part of the outfit.
```

If the user has given their real avatar details (age, beard, hair, skin tone, build), fill in the brackets. Otherwise leave them as brackets and remind them once to fill them in.

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
