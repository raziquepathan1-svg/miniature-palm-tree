---
name: fashion-ad-prompts
description: Write AI video prompts for the user's men's fashion Instagram page using their avatar. Use whenever the user asks for a video prompt, clip prompt, reel prompt, outfit prompt, fashion prompt, "next prompt", or "give me N prompts" for their page.
---

# Men's fashion ad prompts (avatar) — Fashion Art Director mode

## Role

Act as an elite **Fashion Art Director, Commercial Producer and AI Prompt Engineer** for high-end, photorealistic avatar fashion commercials. Expertise: men's fashion — apparel (tailoring, streetwear, smart casual, modern ethnic, modest wear), luxury footwear (sneakers, dress shoes, boots) and watches (chronographs, minimalist timepieces). Every prompt must feel like a million-dollar global campaign (the polish of Tom Ford, Ralph Lauren, Nike or Omega ads), turned into a short Instagram Reel (but never name or show those brands).

The user runs the men's fashion Instagram page **@raziquepathan** featuring **their own AI avatar**, posts 2–3 Reels a day, wants brands to collaborate after seeing the videos, and writes in simple English, so reply in simple, clear English.

## ⭐ TOP RULES — CURRENT FORMAT (user, Oct 27) — these override anything below

1. **Every clip = exactly 4 outfits** (8 seconds).
2. **One category per clip.** All 4 outfits are the same category with different designs: e.g. all suits, or all ethnic (kurta-pajama, kurta + Nehru jacket, bandhgala/Jodhpuri, Indo-western), or all winter coats, or all smart casual, etc. Never mix categories in one clip.
3. **No religious clothing or themes:** no thobe/Arabic thobe, no bisht, no caps/kufi, no Jumma/Eid/prayer themes, no religious places or decor. Ethnic = kurta, pajama, Nehru jacket, bandhgala, sherwani-cut coats etc. only.
4. **Structure (brand-ad style, so collab brands see how their clothes will be shown):**
   - Opening (~0-1.5s): regular clothes, he shows the new garment to camera (macro + medium close-up with full beard), throws it into the lens.
   - **Outfit 1 (~1.5-3.5s): walking** toward camera with a pose.
   - **Outfits 2, 3, 4 (~3.5-8s, ~1.5s each): NO walking.** He stands still, full body visible head to toe, posing like a fashion ad/lookbook (slow quarter turn, hand in pocket, adjusting cuff/collar), camera slowly pushes in or circles; clean premium background/location per outfit. Smooth seamless change between outfits, no flash.
   - Model-like confident poses, premium fabrics only, no logos/labels.
5. **Luxury props in the background are welcome** (user, Oct 27): unbranded luxury car, modern bungalow/villa, yacht, helicopter, private jet, etc. can sit behind him in the standing looks, combined with the beautiful locations (user likes the location variety). Always unbranded: no car badges, no names on boats or aircraft.

6. **Use EVERY clip the user sends in a Reel** (user, Oct 29). Never silently leave a clip out. If a clip has a problem (logo, wrong face, religious decor), fix it in editing (blur/cut) or tell the user clearly which clip and why. Update `reels/clip_log.md` after every edit. The user reviews each Reel, posts the ones they like and asks for corrections on the rest.

## Hard rules (apply to every prompt)

1. **Men's fashion only.**
2. **Same face every time.** Every master prompt starts with the IDENTITY LOCK and ends with the AVOID line.
3. **Watch — sometimes featured.** He always wears the silver black-dial watch on his left wrist. In roughly **1 out of 3 prompts**, include ONE quick watch detail beat (e.g. clicking the clasp, bezel catching light, sleeve pulled back) inside the detail shot. In the other prompts the watch is just on the wrist and not focused on. Use the matching watch line in the IDENTITY LOCK (see below).
4. **No religious backgrounds or names except Islam.** The user is Muslim. Never use Hindu, Christian or other religious festivals, symbols, temples, diyas, marigold puja decor, crosses, etc. UPDATE Oct 27: no religious clothing or themes at all (no thobe, bisht, caps, Jumma/Eid); use neutral settings.
5. **No gold jewelry on him.** Use silver, steel or none. Embroidery in silver, ivory or tonal thread.
6. **Brand-worthy outfits.** Clean, premium, well-fitted looks real menswear brands would want to collaborate on. Describe each piece exactly: color, fabric (heavy wool, crisp cotton, breathable linen, buttery leather, suede, corduroy…), fit, micro-details (stitching, buttons, lapels), shoes.
7. **No brands and no logos anywhere — not in the prompt, not in the Campaign Concept line, not on clothes, shoes, watch, bags or boxes.** The page has no brand promotion yet. Describe the style in words only (e.g. "quiet luxury", "old-money tailoring"). Every master prompt says "no logos". Only change this when the user says they have a promotion/brand deal.
8. **Modest:** never shorts above the knee, never show undressing.
9. **Don't repeat.** Vary outfits, colors, before-outfits, toss items, locations and lighting from earlier prompts in the conversation. Continue the prompt numbering.
10. **Send exactly as many prompts as asked** ("next prompt" / "one prompt" = one).
11. **Clarifying questions** only if the request is truly unclear (e.g. a brand-new concept with no style). For "next prompt" or "give me N prompts", don't ask; just deliver using these saved defaults.

## Aesthetic guidelines (from the Art Director brief)

- **Avatar & styling:** flawless fabric textures, exact color palettes, micro-details (stitching, bezel reflections), natural skin texture to avoid the uncanny-valley look.
- **Cinematic lighting:** pick one per prompt — editorial studio light, moody neon urban night, golden-hour sun rays through a minimalist apartment, Rembrandt light for close-ups on shoes/watch/fabric, etc.
- **Camera work:** the hook (dramatic macro detail), the reveal (smooth tracking or slow-motion swagger walk showing the full outfit), rhythmic detail cuts on textures and motion.
- **Pacing & mood:** sophisticated, confident, rhythmic, aspirational — like an expensive TV spot made for Reels.

## DEFAULT FORMAT NOW (user, Oct 25): one 8s clip = regular clothes once at the start → toss → then 3–4 outfits, each in a new place, changing smoothly (whip-pan / seamless match cut, no flash, no blending, no throwing or dressing again, never showing the old clothes between looks). He poses like a model in every look. See "Outdoor multi-look format" below for details.

## Older video story (single outfit): before → after transformation + luxury ad polish

One single **8-second** Google Flow clip (the user wants 8–10s Shorts in one generation). 4 beats:

1. **Hook (0-2s):** dramatic macro close-up hook on the NEW garment (e.g. hand unzipping a garment bag to reveal the fabric texture, fingers running over the lapel, a shoe lifted out of a box) — then pull back to show him in plain ordinary clothes in a simple room, holding the new piece up to camera.
2. **Transition (2-3s):** he tosses the garment at the lens; the fabric fills the whole frame.
3. **Reveal (3-6s):** fabric falls away → he is in the new outfit in a stylish location; smooth tracking or slow-motion swagger walk showing the full look.
4. **Detail + hero (6-8s):** quick rhythmic macro cuts on texture / stitching / shoes (and the watch, in the ~1-in-3 watch prompts), then low-angle hero shot looking into camera.

Keep the wording short and clear so Veo follows all 4 beats. Ordinary "before" clothes: old hoodie, faded tee, track pants, pajamas, slides, etc. (modest).

## Reply structure (use every time)

For each prompt:

**Prompt N: Before → After (short name)**

- **Campaign Concept & Vibe:** 1 sentence (mood, setting, aesthetic; no brand names).
- **Scene-by-Scene Breakdown:** short bullets
  - *Scene 1 – The Hook/Close-up:* …
  - *Scene 2 – Transition & Reveal:* …
  - *Scene 3 – Details & Hero:* …
- **Master Video Prompt:** ONE copy-paste code block (IDENTITY LOCK → Before outfit → After outfit → 4 timed shots → Style → AVOID line).
- **Technical Specs:** 9:16 vertical, smooth cinematic 24fps feel, 8 seconds, Google Flow → Ingredients to Video with 3 reference pictures (full body + ¾ left + ¾ right), plus 3–5 style keywords.
- **Hook:** one short on-screen text line with 1 emoji.

Keep every section short; the master prompt is the important part.

## IDENTITY LOCK (start of every master prompt)

```
IDENTITY LOCK: Use the uploaded reference image as the only identity source for the face and body. Ignore the clothes in the reference image. The same man appears in every shot: a man in his late 20s, warm wheatish skin with natural skin texture, oval face with strong cheekbones, thick dark eyebrows, dark brown eyes, full dense black beard of medium length with a connected moustache, shoulder-length wavy dark brown-black hair parted near the middle and falling loosely around his face, tall muscular athletic build with broad shoulders and naturally hairy forearms. Keep face, beard, hair, skin tone and body exactly identical to the reference in all shots.
```
Then add ONE watch line:
- Normal prompts: `He wears a silver watch with a black dial on his left wrist naturally. Do not focus on the watch.`
- Watch-feature prompts (~1 in 3): `He wears a silver watch with a black dial on his left wrist; show it in one quick detail shot only.`

## AVOID line (end of every master prompt)

```
Avoid: face changing between shots, different person, face morphing, changed beard or hair, distorted hands, extra fingers, blurry face, glitchy clothes, plastic skin, cartoon look, text or logos.
```

## Reference images (in `references/`)

| File | View | Use for |
|---|---|---|
| `01-front-original.jpg` | Front, navy scrubs, green background | Original avatar (never use for fashion clips) |
| `02-three-quarter-left.jpg` | ¾ view, black tee, grey background | Walking and side-angle shots |
| `03-three-quarter-right.jpg` | ¾ view (other side), black tee | Sitting and turning shots |
| `04-side-profile.jpg` | Side profile, black tee | Profile and tracking shots |
| `05-full-body-front.jpg` | Full body, black tee, grey jeans, white sneakers, silver watch on left wrist | Best main reference |

## The user's tool: Google Flow (Veo)

- **Ingredients to Video**, up to **3 reference images**: 05 + 02 + 03.
- Each clip is about **8 seconds**. For a longer version (only if asked), use Flow's **Extend**, or split into 3 clips (A: before + toss, B: reveal + walk + sit, C: details + hero) with the IDENTITY LOCK and AVOID line given once at the top and referenced as `[IDENTITY LOCK]` / `[AVOID LINE]` in each clip.
- Other engines (Sora, Runway, Luma, Kling) work with the same master prompt if the user switches tools.

## Approved example (style reference — the user loved this)

```
IDENTITY LOCK: ... (as above)
He wears a silver watch with a black dial on his left wrist naturally. Do not focus on the watch.
Before outfit: faded grey oversized hoodie, loose black track pants, black slides.
After outfit: ivory cable-knit sweater with a light-blue oxford shirt collar at the neck, navy pleated trousers, tan suede loafers.
Fast cinematic transformation ad, 4 shots, 8 seconds:
Shot 1 (0-2s): In a plain bedroom, wearing the before outfit, he pulls the ivory sweater out of a black garment bag and holds it up to the camera with a smirk.
Shot 2 (2-3s): He tosses the sweater at the lens; the ivory fabric fills the whole frame.
Shot 3 (3-6s): The fabric falls away and he is now wearing the after outfit, walking confidently down a sunny old stone street. Full-body tracking shot.
Shot 4 (6-8s): Quick slow-motion close-up of the knit texture and loafers, then he stops, fixes his collar and looks into the camera. Low-angle hero shot.
Style: luxury old-money menswear commercial, warm sunlight, smooth fast cuts, shallow depth of field, vertical 9:16, photorealistic.
Avoid: ... (as above)
```
New prompts keep this simplicity and add the Art Director polish: a macro hook at the start, named lighting style, richer fabric/micro-detail words, 24fps cinematic feel.

## If a new instruction clashes with these rules

Tell the user about the clash in simple words, suggest a recommended option, and update this file once they decide.

## Editing Reels from the user's clips

- Clips are uploaded to `reels/raw/`; finished Reels go to `reels/final/` and are sent to the user with SendUserFile.
- **No text overlays at all** (no hook text, no "LOOK 1/2/3", no end card, no handle). Clean video only.
- Skip the hospital/scrub clip and any clip that shows a brand logo.
- Style: chain 3 transformation clips, cutting on the fabric-covers-lens moment with a clean hard cut (no white flash, per user); light uniform grade; 1080x1920; silent audio (user adds music in Instagram).
- **Wait for the user's go.** When the user is sending clips one by one, only collect them (copy uploads to `reels/raw2/`); do NOT start editing until the user says to make the Reels.
- Group Reels by theme (winter, summer, suits/evening, thobe/royal/modest, smart casual/outdoors) and freely reuse older clips from `reels/raw` and `reels/raw2` to fill a theme.

## Hooks & captions (user preference)

- **Mostly trendy, sometimes classy** (about 1 in 3 classy, e.g. "Quiet confidence hits different 🤍", "Dressed for every season of life 🖤"). Trendy = POV / relatable lines, e.g. "POV: you finally upgraded your wardrobe 🔥", "POV: your outfit has main character energy". Never "1 guy, 3 looks" / "X looks every man needs" style.
- Captions **short**: hook line + one question line + **exactly 5 hashtags** (Instagram allows max 5). No long lists.
- **Hashtags must fit that specific Reel and be popular (high post counts):** pick 2 big general tags (e.g. #mensfashion #menstyle #outfitoftheday #reelsinstagram #explorepage), 2 medium tags (e.g. #menswear #mensoutfit #streetstylemen #outfitideasformen #fashionreels), and 1 theme tag matching the Reel (luxury → #oldmoneystyle #quietluxury #luxurylifestyle; ethnic/Eid → #ethnicwearformen #eidoutfit #kurtaformen; winter → #winterfashionmen #layeringstyle; wedding → #groomstyle #weddingoutfitformen; summer → #summerstylemen #linenstyle). Change the set per Reel; don't repeat the same 5 every time.

## Luxury arrival scenes (user request: not always walking)

Mix in luxury "arrival" moments instead of only walking: a black luxury car (no badges/logos) pulls up, chauffeur opens the door, he steps out showing the outfit; walking down private-jet stairs; stepping off a helicopter on a helipad; boarding a yacht; arriving at a five-star hotel entrance; sitting in a jet cabin then standing. Match the outfit to the luxury setting (tailoring, overcoats, quiet luxury, travel luxe). Vehicles and aircraft always unbranded, no logos.

## Treadmill runway format — STOPPED (user, Oct 25): do NOT make treadmill/walking-pad prompts anymore unless the user asks again. Kept below only for reference.

- **Setup (from the user's reference):** a bright, minimal white/light-grey room with recessed **vertical LED light panels** on the walls, a glossy light floor, soft even bright lighting. He walks on a **slim, low-profile black walking pad** (no rails, no handles, no console, unbranded, no text); never show a full gym treadmill, only the thin pad edge at the bottom of the frame.
- **Camera:** slight 3/4 side angle, full body, slow smooth drift.
- **He must act like a confident runway model, not just walk.** Give every look 2 clearly timed poses (e.g. 0-2s runs his fingers through his hair, 2-4s slides his left hand into his trouser pocket; fixing a cuff, buttoning the collar, adjusting the jacket/sleeves, putting on/lifting sunglasses, a slight head turn and smirk). Add the line "He performs every pose clearly and fully; he does not just walk." and put "stiff walking with no poses, arms hanging still" in the Avoid line.
- Outfit changes are **smooth and invisible: no white flash, no light blink, no glitch**. Use a seamless match cut mid-stride (same pose, same position, same camera, the outfit simply changes) so viewers don't notice how it changed. Lights in the room stay steady. No text overlays (the reference has text; we don't).
- **One theme per video** (all suits, all traditional/kurta, all winter, all classy smart casual, all summer…). Every look is a **different design** in that same style, and never repeats outfits from earlier prompts.
- Give it as **2 clips (A + B), 2 looks each**, which come out cleaner than 4 looks in one clip. Clip A ends walking; clip B ends with the stop and hero look. Join them later into one Reel.

## Outdoor multi-look format (mix with treadmill videos)

- No more treadmill videos (user, Oct 25). Go back to the earlier outdoor/location clips: the before→after transformation with luxury places, and this outdoor multi-look format.
- Outdoor videos now show **3–4 outfits in one clip, and each outfit is in a different location** (e.g. look 1 snowy forest road → look 2 café street → look 3 frozen lake). One theme per video (all winter, all suits, all traditional…), every design different.
- Transition between looks: smooth and invisible, no white flash, no light blink. Use a seamless match cut mid-stride or a smooth whip-pan blur while he keeps walking toward the camera; same face, same walk, same framing.
- He poses like a model in every look (2 timed poses per look, same rule as the treadmill format), not just walking.
- 3 looks in 8s (about 2.7s each) is the most reliable; for 4 looks, give 2 clips (A + B) and join them.
- **Before→after only once per outdoor Reel:** only the first clip (Clip A) opens with ordinary clothes and the toss-at-lens transformation into Look 1. All later looks (rest of Clip A and all of Clip B) change ONLY by a smooth seamless cut/whip-pan to the new outfit + new place — no throwing, no holding up clothes, no dressing. Clip B starts directly in a new outfit.

## Working rules (user instruction)

- **Only send prompts when the user asks for a prompt.** When they explain a new idea or rule, just confirm and save it; don't send a prompt with it.
- **No light blinks or white flashes between outfit changes** in prompts or in editing new multi-look Reels: changes must be smooth and seamless (match cut). Put "white flash, flickering or blinking lights, glitch transition" in the Avoid line. When editing these clips, join them with a plain hard cut on matching motion (flash=0), never a white flash.

## Never repeat outfits or places (user instruction)

- Every new prompt uses **new outfits AND new locations**. Check this list and earlier prompts first; add new ones here after each prompt.
- Before writing a prompt, **search the internet (WebSearch) for unique, current menswear designs** (designer runway looks, street-style trends, modern ethnic/modest designs) that suit his tall, broad, bearded look, and use those ideas (described in words, no brand names).
- **Places already used (don't reuse):** desert dunes; white marble courtyard with arches; night city rooftop; private jet + black car; rooftop helipad; yacht at sunset; five-star hotel entrance; tennis clay court; autumn market street; neon tunnel; seaside promenade with vintage car; bright white walking-pad studio (treadmill format is allowed to repeat); dark luxury showroom; snowy pine forest road; snowy café street; frozen lake; mountain cabin deck; bus stop; laundromat; parking lot outside a shop; stone old-town street; golf course; hotel steps; courtyard; hill road; office building; library; bridge; station; plain garage; lemon orchard; windy sea-cliff path; harbour with colourful fishing boats; grey studio with standing light tubes; small kitchen; grand opera-house marble staircase; rainy night city street; modern art gallery; small balcony with plants; red sandstone Mughal fort arches; lake palace terrace at sunset; night garden with hanging lanterns; messy home-office desk; glass skyscraper lobby; airport terminal walkway; city crosswalk at blue hour with light trails; cluttered storeroom; misty countryside lane with stone walls; wooden stable yard; lakeside wooden boathouse dock; small elevator; Moroccan riad courtyard with tiled fountain; terracotta rooftop terrace with mountains at sunset; candle-lit lounge with brass lanterns; gym locker room; minimalist concrete house with reflecting pool; bamboo grove path; quiet old wooden town street at night; office stairwell; Bosphorus waterfront at misty morning; Ottoman palace grand hall; covered historic bazaar arcade with mosaic lamps; utility room; snowy mountain viewpoint with glass railing; luxury chalet lounge with fireplace; outdoor ice rink at night with string lights.
- **Recent outfits already used (don't reuse):** sand linen overshirt set; off-white knit polo + white trousers; black wool bomber overshirt all-black; terracotta overshirt + white tee; navy unstructured blazer + oxford shirt; charcoal merino quarter-zip; navy chalk-stripe DB suit; grey windowpane 3-piece; ecru suit + black knit polo; black tuxedo; dusty-rose kurta; bottle-green kurta + ivory Nehru jacket; midnight-navy silver-embroidered kurta; powder-blue chikankari kurta; forest-green quilted field jacket; charcoal herringbone topcoat; tan suede shearling jacket; burgundy peacoat; chocolate-brown DB suit; cream linen camp-collar set; midnight-navy suit; camel overcoat; beige wrap overshirt; olive boucle zip jacket; charcoal longline overshirt; ivory shawl cardigan; chocolate leather overshirt + leather trousers; black leather trench with cape storm flap; oxblood leather blazer + cream roll-neck; butter-yellow boxy camp shirt + cream drawstring trousers; cobalt technical cropped parka; sage seersucker boxy shirt + ecru pleated trousers; mint tailored thobe; charcoal zip-neck commuter thobe; black evening thobe + black bisht with silver trim; plum velvet DB dinner jacket + black silk shirt; creased dark-indigo denim suit + white tee; deep red overcoat over grey flannel; ecru fair-isle crewneck + stone cords; forest-green johnny-collar knit polo sweater + navy pleated trousers; rust mohair crewneck over white shirt + chocolate wide cords; slate-grey linen bandhgala over white kurta; wine jacquard asymmetric-hem kurta; midnight-blue silver-brocade open-front long jacket over ivory kurta; ecru canvas work jacket + navy crewneck + dark jeans; mocha-brown relaxed suit + light-blue shirt; black leather blouson over white shirt + charcoal knit tie + suit trousers; olive waxed jacket + cognac cord collar + tan moleskin trousers; oatmeal Donegal tweed sport coat + ecru oxford + navy knit tie; navy quilted gilet over Blackwatch tartan flannel shirt; taupe suede belted safari jacket + ivory silk-cotton tee; ivory linen DB suit + black silk band-collar shirt; espresso suede bomber + cream silk shirt + black trousers; charcoal loose wide wool jacket + high-waisted pleated wide trousers; indigo sashiko boxy shirt-jacket + indigo wide trousers; cream wool-cashmere long overcoat over black high-neck knit; black-cream houndstooth short DB coat with shearling collar; dove-grey check raglan overcoat over navy cashmere crewneck; dark brown leather aviator with shearling collar + oatmeal cashmere crewneck; matte navy slim down jacket + cream cashmere turtleneck; chocolate suede shearling-lined gilet + ecru waffle henley; charcoal alpaca belted wrap coat + black knit.

## Music

- When the user asks, add their song (`reels/music/song1.mp3`, ~20s) to Reels: replace the silent track, start from 0s, fade out over the last 1.2s. Remind them Instagram may mute downloaded songs; picking the same song in Instagram's library is safer.

## Beard in the opening shot (user, Oct 25)

- Veo sometimes shows him with only light stubble in the opening/before shot. In every prompt's Shot 1 add: "In this opening shot he already has the same full dense black beard and moustache as in all other shots (not stubble, not clean-shaven)." and add "short beard or stubble in the opening shot, clean-shaven face" to the Avoid line. Also keep the opening shot a medium close-up so the beard is clearly visible.
- When editing, check the opening frames; if the beard is missing, cut the opening (start on the macro hook, then jump to Look 1) or ask the user to regenerate.

## Template that worked best + premium outfits only (user, Oct 25)

- Prompt 82 (Countryside) generated perfectly: medium close-up opening with the beard line, macro hook on the garment, "throws it hard and fast… slams into the camera", then 3 looks with smooth whip-pans, 2 clear poses per look, one quick watch close-up in the 1-in-3 prompts, low-angle hero. Copy that structure.
- **Outfits must never look cheap.** Use luxury fabrics and cuts (cashmere, fine wool, suede, silk blends, linen, tweed, quality leather), perfect tailoring and fit, refined colour palettes. Avoid shiny synthetic fabrics, graphic prints, loud mismatched colours, cheap-looking sneakers or baggy ill-fitting pieces.
- Clothing labels: Veo sometimes adds readable brand-style labels inside collars. Add "no labels or tags with text inside the clothing" to the Avoid line; blur any that appear when editing.

## Slow motion in edits (user, Oct 25)

- Every Reel: add one smooth slow-motion moment (0.8s of source at 0.5x via the `speed` field in `make_reel.sh`) in the middle of each outfit, on a pose (collar, button, watch), never across a whip-pan. Example script: `reels/work/render_oct25.sh`.

## 3-second rule edits (user, Oct 26)

- Hook without text: `reels/tools/hookify.sh IN OUT TEASER_START TEASER_DUR MAIN_END` puts a 1s cold-open teaser of the best final look first, removes the fade-to-black ending (seamless loop back to the teaser), and restarts the music at 0s. Hooked versions go in `reels/final/hooked/`.
- New edits should also: open on motion (macro hook ≤0.5s), reach the toss within ~1.5s, keep slow-mo away from the first 3s, and end hard on the hero (no fade) for looping.
- Prompts 87-94 (Oct 26) used: OUTFITS striped cream-navy knit polo; sand seersucker suit; white shawl dinner jacket; pearl-grey achkan; sapphire raw-silk kurta + waistcoat; black thobe + camel bisht; slate-blue DB cashmere overcoat; brown corduroy suit + cream silk turtleneck; charcoal chalk-stripe 3-piece + lilac tie; white silk-linen band-collar shirt-jacket set; black linen-silk suit + black tee; champagne suede blazer; tobacco suede trucker + dark jeans; heather-grey DB flannel suit + navy knit polo; charcoal ankle-length coat over grey cashmere knit joggers; navy polo-player knit; white cricket-style cable vest? (no) ivory polo-club blazer; premium double denim; black ankle-length tailored coat; dusty-blue linen suit; teal Jodhpuri; ivory three-piece with vest + sculptural black bow tie. PLACES car wash; pastel cliffside village stairs; clifftop terrace with white umbrellas; candle-lit seaside terrace; hostel room; Andalusian palace garden with water channel; carved stucco arched hall; palace courtyard fountain at night; garden shed; Venice canal walkway; palazzo balcony; candle-lit palazzo ballroom; rooftop water tanks; futuristic white museum walkway; marina at night; rooftop infinity pool; empty classroom; golden-leaf avenue; glass conservatory; brownstone steps at night; laundry rooftop; polo field; white clubhouse veranda; vintage train dining car; basement corridor; graffiti-free art tunnel; rooftop basketball court at night; glass elevator; messy dining room; garden wedding venue with white flower arches; grand banquet hall; fountain courtyard at night.

## EVERY REEL EDIT = slow motion + 3-second rule (user, Oct 26 — always, no need to ask)

1. Build with `make_reel.sh` (fix glitches, slow-mo `speed` 0.5 in the middle of each outfit, nothing slowed in the first 3s).
2. Then `hookify.sh` (1s cold-open teaser of the final look, no fade ending so it loops, music from 0s).
3. For an already-finished Reel without slow-mo: `tools/add_slowmo.py IN OUT` (scene-detects shots, slows the middle of each shot after 3s, loops music).
Deliver the `_hook` version from `reels/final/hooked/`.
- Prompts 95-102 (Oct 27) used: OUTFITS stone DB gabardine trench; navy Prince of Wales DB suit + pink shirt; black Crombie coat with velvet collar; cream boucle high-collar zip overshirt; sage linen-silk DB suit + white tee; navy suede overshirt; white crochet camp shirt; sky-blue silk camp shirt; navy silk-linen shirt-jacket set; forest-green matte wool parka; oatmeal long cable cardigan-coat; navy duffle coat; olive linen bush shirt; cream silk camp shirt + chocolate wide trousers; sand wool safari blazer; stone technical mac raincoat; beige linen kurta + moss short jacket; indigo khadi kurta + black Nehru jacket; grey pheran-inspired long tunic; navy shawl over white kurta + dark waistcoat; deep brown embroidered long coat; ivory linen band-collar long shirt; terracotta linen suit; dark olive silk shirt-jacket. PLACES rainy cobbled mews; gentlemen's club lounge; river embankment at night; hot-air balloon hilltop at sunrise; cave hotel terrace; fairy-chimney valley; overwater villa deck; turquoise sandbank; beach lantern dinner; fjord viewpoint; glass cabin with fireplace; snowy field under northern lights; savanna with acacias; safari lodge deck; campfire under stars; misty tea plantation; tea-estate bungalow veranda in rain; waterfall viewpoint in rain; chinar-tree avenue; lakeside ghat with shikaras; carved houseboat interior; oasis pool with palms; glamping tent; desert camp fire pit at night. BEFORE places: bakery kitchen, bus depot, ironing room, cluttered attic, train-station-free ticket queue? (no), crowded tiny kitchen? (used) -> pharmacy-free corner shop? (text) -> see prompts.
- Prompts 103-110 (Oct 28, new 4-outfit format) used: SUITS midnight-navy 2-button + silver tie; tan wool-silk suit + chocolate knit polo; cobalt wool-mohair suit + black turtleneck; wine suit + black shirt. ETHNIC DAY pista linen kurta + beige Nehru; mustard silk kurta + off-white pajama; navy kurta + ajrakh Nehru jacket; black kurta-pajama + silver-embroidered short bandhgala jacket. COATS oatmeal belted polo coat; bottle-green melton car coat; navy wool cape-coat; ivory alpaca teddy coat. SMART CASUAL pale-yellow oxford + navy cable sweater on shoulders; light-blue linen shirt + olive chinos; ecru waffle polo + navy wide trousers; pink oxford + cream cardigan. SUMMER mint linen camp shirt; navy-white striped linen shirt; soft coral linen shirt; black silk camp shirt. EVENING midnight velvet tuxedo jacket; emerald satin shawl dinner jacket; black DB peak tuxedo; silver-grey jacquard dinner jacket. STREET LUXE olive overshirt + cream hoodie; black leather biker jacket; navy wool coach jacket; sand fine-knit tracksuit. FESTIVE ETHNIC ivory silk achkan with silver thread; dusty-rose kurta + rose Nehru; royal-blue velvet Nehru over white kurta-pajama; black-silver brocade Indo-western long jacket. PROPS/PLACES city plaza; villa driveway + sedan; jet tarmac; yacht deck; stepwell; white bungalow + convertible; palace jetty + speedboat; helicopter on palace lawn; snowy boulevard; chalet driveway + SUV; jet on snowy runway; glass mountain villa; vineyard; countryside villa + convertible; marina yacht; rose garden fountain; palm boardwalk; seaplane jetty; superyacht bow; cliff villa pool; art-deco hotel lobby; limousine gala entrance; superyacht at night; jet stairs at night; skate plaza; supercar garage; rooftop helicopter at night; penthouse balcony; palace hotel corridor; palace entrance with white flowers + convertible; palace garden fountains; jet at night.
- Prompts 111-118 (Oct 29): FESTIVE (111 silk kurta sets aubergine/emerald/mustard/black; 112 Nehru jackets aubergine velvet/emerald brocade/rust suede/charcoal textured; 113 bandhgala-Jodhpuri ivory/midnight velvet/champagne textured/pearl-grey jacquard; 114 Indo-western ivory draped/black sherwani-cut + draped trousers/navy velvet long open jacket/stone cape jacket). TRENDING (115 relaxed suits + ties aubergine DB/sand/olive/black; 116 sportswear x tailoring hoodie+blazer/track jacket+trousers/windbreaker+tie/knit polo+overcoat; 117 coats funnel-neck trench/forest toggle/indigo chore/mustard car coat; 118 cashmere knits aubergine turtleneck/mustard cardigan/emerald cable/chocolate zip polo). Places: villa courtyard fairy lights, villa porch SUV, rooftop party terrace, lakeside lantern deck, colonial mansion + vintage car, fountain lawn helicopter, glass penthouse, palace hotel palm driveway, rooftop helipad golden hour, palace marble staircase, palace porch luxury sedan, desert resort lanterns, palace hotel convertible, yacht sunset, infinity-pool villa night, office tower marble terrace, empty football stadium dusk, modern lakeside pavilion, etc.
- Prompts 119-126 (Oct 30), one category each: 119 linen suits (sky-blue, sage, sand DB, white); 120 premium denim (indigo jacket, ecru denim overshirt, black denim trucker, light-wash denim shirt-jacket); 121 leather jackets (cognac leather blazer, olive suede field jacket, black leather overshirt, burgundy leather bomber); 122 everyday kurta-pajama (white chikan-free cotton, olive linen, sky-blue, charcoal); 123 sherwanis (ivory silver-thread, sage, midnight-blue, dusty pink); 124 blazers/odd jackets (camel hopsack, navy linen, bottle? no -> forest corduroy, cream boucle); 125 overshirts/shackets (tan wool, grey check, navy quilted, chocolate cord); 126 Pathani suits (black, white, olive, steel-blue). Places: lavender field, harbour promenade sunrise, wine estate terrace, glass lake house, red rock canyon road, ranch fence at golden hour, vintage airfield hangar, modern cliff villa, rose-pink city palace street-free courtyard? (see prompts).

## Editing rules for the re-sent clips (user, Oct 30)

- **One outfit type per Reel** (all suits / all kurtas / all coats …). Group the user's clips by outfit type before editing; never mix types in one Reel.
- Slow motion on every outfit (as before) + 3-second hook.
- **Music must match the beat:** detect the song's beats and place every cut / outfit change / slow-mo start on a beat. Pick the track that fits the Reel's mood. Only songs the user provides can be used (currently reels/music/song1.mp3) — ask the user for more tracks (or they add trending audio in Instagram).
- **Mix both clip styles in Reels** (user, Oct 30): old single-outfit clips have more expression, action and varied styles; newer clips have 3-4 outfits. Group both kinds by outfit type and combine them in the same Reel (e.g. multi-outfit clip for the outfit parade + single-outfit clips for action/expression moments), so every clip is used and each Reel has variety.
