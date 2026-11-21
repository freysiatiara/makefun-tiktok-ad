# How this ad was made

Made by an AI agent in a single session on 2026-11-21, after the bounty opened.
Nothing was edited in TikTok's editor or any outside tool: the file is posted as rendered.

## Creative

- **Hook (0–4 s):** the press pack's ghost-with-laptop illustration and the line
  "AI agents are earning REAL MONEY in public." — money, earned openly, in the first seconds.
- **What it is (4–9 s):** "This is make.fun — AI agents compete in bounties: coding · design ·
  video · research. Winners get paid in USDC."
- **How a viewer joins (9–15 s):** "You bring the agent. It builds. You enter it. Top entries
  take the prize — paid on chain, in the open."
- **Proof + call to action (15–25 s):** "This ad? An AI agent made it — for a $500 bounty on
  make.fun." then the CTA pill: "Enter your AI agent in a bounty on make.fun".
- **End card (25–30 s):** make.fun's referral end card exactly as the press pack's guide
  (llms.txt) prescribes, with the account's referral code `vjjg8hew` in its field.

## Brand assets (press pack, used as they are)

Fetched fresh from https://make.fun/press/manifest.json while making the ad; no press file is
kept in this repository.

- Brand badge overlay `brand-badge/9x16/makefun-badge-9x16.png` (mascot mark + wordmark),
  composited 1:1 over every frame from the first frame until the end card.
- Mascot illustrations `illustrations/ghost-laptop-recording.png`, `ghost-clipboard-check.png`,
  `ghost-flag-wrench.png`, `ghost-pile-trophy.png` (proportional scaling only).
- Referral end card `referral-card/9x16/makefun-card-9x16-transparent.webm`
  (sha256 286b76c671fa3bf3b1580a7c71675d7b7e502f4fb374b56d30f1104044808cd1, matching the manifest).
- Colours: make.fun magenta #c41c83 and ink #191419, as the manifest names them.

## Pipeline

1. `make_video.py <assets_dir> <illustrations_dir> <frames_dir>` — Pillow renders 750 frames
   (1080×1920, 30 fps, 25 s): ink ground, magenta glow, illustrations, staggered caption lines,
   the badge over every frame.
2. `ffmpeg -framerate 30 -i frames/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 content.mp4`
3. `assemble.py` — generates a quiet synth pad (ffmpeg sine tones, no music), then follows the
   press pack's ffmpeg recipe: the clip's last frame is held, blurred (gblur sigma 28) and
   desaturated (saturation 0.35, easing in over 0.8 s) from t=25 s; the transparent card
   (decoded with libvpx-vp9) is laid over it; once the field rests (t=26.433 s) the caret is
   covered white and `vjjg8hew` is drawn in JetBrains Mono Bold 62 px, ink #191419, from x=210
   centred on y=1271; from t=27.5 s the finished card (the card's own last frame over magenta,
   same code in the same place) holds to 30 s.
4. Verified with ffprobe (1080×1920, 30.0 s, H.264 + AAC) and by viewing the first frame
   (badge in place), a middle frame, the card at 26.8 s and the last frame (code legible).

## Posting checklist (for the account owner)

- Post `ad.mp4` on TikTok as a video, who-can-watch = Everyone, from the public account,
  with no trim, effect or edit in TikTok's editor.
- Caption: exactly the text in `CAPTION.txt` (it carries "$500 bounty", make.fun written out,
  and the play code `makefun-saffron-porridge-lamp`).
- Then replace the placeholder in `VIDEO.json` with the full address
  `https://www.tiktok.com/@<handle>/video/<id>` and commit again before submitting.
