#!/usr/bin/env python3
"""Final assembly for the make.fun TikTok ad, following the press pack's own
ffmpeg recipe (llms.txt): the transparent referral card (VP9, decoded with
libvpx-vp9) is laid over the clip's last seconds while the clip blurs and
desaturates; once the field rests (1.433 s in), the caret is covered white and
the referral code is drawn in JetBrains Mono Bold 62 px, ink #191419, from
x=210 centred on y=1271. A finished-card hold (the card's own last frame over
magenta, same code in the same place) closes the video.
"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = "vjjg8hew"
FONT = os.path.join(HERE, "fonts", "JetBrainsMono-Bold.ttf")
CARD_WEBM = os.path.join(HERE, "assets", "makefun-card-9x16-transparent.webm")
CONTENT = os.path.join(HERE, "content.mp4")
OUT = os.path.join(HERE, "ad.mp4")
T = 25.0          # card starts (content is 25 s, held frame after)
REST = 1.433      # card field rest offset
HOLD_AT = 27.5    # finished-card still takes over

# --- finished-card hold still: magenta ground + the card webm's own last frame + code
last = Image.open(os.path.join(HERE, "card_last_rgba.png")).convert("RGBA")
hold = Image.new("RGBA", (1080, 1920), (196, 28, 131, 255))
hold.alpha_composite(last)
d = ImageDraw.Draw(hold)
d.rectangle([208, 1230, 208 + 9, 1230 + 82], fill=(255, 255, 255, 255))  # cover caret
f = ImageFont.truetype(FONT, 62)
d.text((210, 1271), CODE, font=f, fill=(25, 20, 25, 255), anchor="lm")
hold.convert("RGB").save(os.path.join(HERE, "card_hold.png"))

# --- soft synth pad (no music, just tones we generate): A-minor pad, quiet
pad = os.path.join(HERE, "pad.m4a")
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-f", "lavfi", "-i", "sine=frequency=220:duration=30",
    "-f", "lavfi", "-i", "sine=frequency=261.63:duration=30",
    "-f", "lavfi", "-i", "sine=frequency=329.63:duration=30",
    "-f", "lavfi", "-i", "sine=frequency=110:duration=30",
    "-filter_complex",
    "[0:a]volume=0.045[a0];[1:a]volume=0.035[a1];[2:a]volume=0.035[a2];[3:a]volume=0.05[a3];"
    "[a0][a1][a2][a3]amix=inputs=4:normalize=0,afade=t=in:st=0:d=1.5,afade=t=out:st=28:d=2[a]",
    "-map", "[a]", "-c:a", "aac", pad], check=True)

graph = (
    "[0:v]tpad=stop_mode=clone:stop_duration=5,fps=30,format=yuva420p,split[clip][soft];"
    "[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=25:d=0.8:alpha=1[softf];"
    "[clip][softf]overlay[bg];"
    "[1:v]fps=30,format=yuva420p,setpts=PTS-STARTPTS+25/TB[card];"
    "[bg][card]overlay=eof_action=pass[bgc];"
    "[2:v]setpts=PTS-STARTPTS+27.5/TB[hold];"
    "[bgc][hold]overlay=eof_action=pass[bgh];"
    f"[bgh]drawbox=x=208:y=1230:w=9:h=82:color=white:t=fill:enable='gte(t,{T+REST})*lt(t,{HOLD_AT})',"
    f"drawtext=fontfile={FONT}:text='{CODE}':fontsize=62:fontcolor=0x191419:"
    f"x=210:y=1271-(ascent-descent)/2:enable='gte(t,{T+REST})*lt(t,{HOLD_AT})'[v]"
)
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-i", CONTENT,
    "-c:v", "libvpx-vp9", "-i", CARD_WEBM,
    "-loop", "1", "-framerate", "30", "-i", os.path.join(HERE, "card_hold.png"),
    "-i", pad,
    "-filter_complex", graph,
    "-map", "[v]", "-map", "3:a",
    "-t", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
    "-c:a", "aac", "-movflags", "+faststart", OUT], check=True)
print("wrote", OUT)
