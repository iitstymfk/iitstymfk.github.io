# Bakes the perk machine art into assets/tex/perk/. Needs Pillow, the SBS Tiny Texture Pack 3 metals (S path) and the Bungee/Oswald .woff fonts (FB/FO paths).
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps, ImageEnhance
import math, random, os
S='/mnt/user-data/uploads/d/iitsty breakfast club/assets/_claude_preview/perk/'
OUT='/home/claude/iitstymfk.github.io/zombies/assets/tex/perk/'; os.makedirs(OUT, exist_ok=True)
FB='/tmp/fonts/node_modules/@fontsource/bungee/files/bungee-latin-400-normal.woff'; FO='/tmp/fonts/node_modules/@fontsource/oswald/files/oswald-latin-700-normal.woff'
chip=Image.open(S+'Metal_11-512x512.png').convert('RGB'); rust=Image.open(S+'Metal_23-512x512.png').convert('RGB'); steel=Image.open(S+'Metal_01-512x512.png').convert('RGB'); rivet=Image.open(S+'Metal_21-512x512.png').convert('RGB'); grey=Image.open(S+'Metal_19-512x512.png').convert('RGB')
PERKS={'revive':('SECOND','WIND','#3aa0ff','cross'),'tough':('TOUGH','BREW','#ff3030','heart'),'rapid':('RAPID','FIRE','#ffd030','bolt'),'speed':('SPEED','MIX','#40ff70','cycle'),'stamina':('STAMINA','SHOT','#ff9a30','chev')}
def hexc(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
def tile(img,w,h):
    o=Image.new('RGB',(w,h))
    for y in range(0,h,img.height):
        for x in range(0,w,img.width): o.paste(img,(x,y))
    return o
def paint(col,w,h):
    # chipped paint: light areas of the chip texture take the colour, dark chips show rust
    base=tile(chip,w,h); L=ImageOps.grayscale(base)
    c=Image.new('RGB',(w,h),col); L2=ImageEnhance.Contrast(L.convert('RGB')).enhance(.35).convert('L'); shade=ImageEnhance.Brightness(Image.merge('RGB',(L2,L2,L2))).enhance(1.25)
    painted=ImageChops.multiply(c,shade)
    mask=L.filter(ImageFilter.GaussianBlur(1)).point(lambda v:255 if v>85 else int(v*2.6))
    r=tile(rust,w,h); out=Image.composite(painted,ImageEnhance.Brightness(r).enhance(.7),mask)
    return out
def grime(img,amt=.55):
    w,h=img.size; g=Image.new('L',(w,h),0); d=ImageDraw.Draw(g)
    for y in range(h): d.line([(0,y),(w,y)],fill=int(255*amt*max(0,(y/h-.55))/.45))
    for _ in range(40): x=random.randint(0,w); d.line([(x,random.randint(0,h)),(x+random.randint(-6,6),h)],fill=random.randint(40,120),width=random.randint(1,4))
    g=g.filter(ImageFilter.GaussianBlur(3)); dark=Image.new('RGB',(w,h),(18,12,8))
    return Image.composite(dark,img,g)
def scratches(img,n=60):
    d=ImageDraw.Draw(img); w,h=img.size
    for _ in range(n):
        x,y=random.randint(0,w),random.randint(0,h); a=random.uniform(0,6.28); l=random.randint(8,60)
        d.line([(x,y),(x+math.cos(a)*l,y+math.sin(a)*l)],fill=(200,195,185),width=1)
    return img
def icon(d,kind,cx,cy,r,col,width=0):
    if kind=='cross':
        t=r*.36; d.rectangle([cx-t,cy-r,cx+t,cy+r],fill=col); d.rectangle([cx-r,cy-t,cx+r,cy+t],fill=col)
    elif kind=='heart':
        s=r*.55; d.ellipse([cx-r,cy-r*.75,cx,cy+r*.15],fill=col); d.ellipse([cx,cy-r*.75,cx+r,cy+r*.15],fill=col); d.polygon([(cx-r*.97,cy-r*.15),(cx+r*.97,cy-r*.15),(cx,cy+r)],fill=col)
    elif kind=='bolt':
        d.polygon([(cx+r*.25,cy-r),(cx-r*.55,cy+r*.12),(cx-r*.02,cy+r*.12),(cx-r*.3,cy+r),(cx+r*.6,cy-r*.2),(cx+r*.05,cy-r*.2)],fill=col)
    elif kind=='cycle':
        w=int(r*.28)
        d.arc([cx-r,cy-r,cx+r,cy+r],200,340,fill=col,width=w); d.arc([cx-r,cy-r,cx+r,cy+r],20,160,fill=col,width=w)
        for ang,dirn in ((340,1),(160,1)):
            a=math.radians(ang); px,py=cx+math.cos(a)*r*.86,cy+math.sin(a)*r*.86; t=math.radians(ang+90)
            d.polygon([(px+math.cos(t)*r*.32,py+math.sin(t)*r*.32),(px+math.cos(a)*r*.35,py+math.sin(a)*r*.35),(px-math.cos(a)*r*.35,py-math.sin(a)*r*.35)],fill=col)
    elif kind=='chev':
        for k in (-.45,.25):
            x0=cx+k*r; d.polygon([(x0-r*.35,cy-r*.8),(x0+r*.05,cy-r*.8),(x0+r*.55,cy),(x0+r*.05,cy+r*.8),(x0-r*.35,cy+r*.8),(x0+r*.15,cy)],fill=col)
def outline_text(d,xy,t,font,fill,stroke=(15,8,6),sw=4,anchor='mm'):
    d.text(xy,t,font=font,fill=fill,stroke_width=sw,stroke_fill=stroke,anchor=anchor)
side_cache={}
for k,(a,b,hx,ic) in PERKS.items():
    col=hexc(hx); dark=tuple(int(c*.35) for c in col); light=tuple(min(255,int(c*.6+255*.4)) for c in col)
    W,H=512,1024
    F=paint(col,W,H); d=ImageDraw.Draw(F)
    # chrome border + pinstripes
    for i,c in enumerate([(210,210,215),(90,90,95)]): d.rectangle([6+i*4,6+i*4,W-7-i*4,H-7-i*4],outline=c,width=4)
    for x in (40,W-40): d.line([(x,60),(x,H-60)],fill=light,width=6)
    # name band
    band=Image.new('RGB',(W-80,170),dark); bd=ImageDraw.Draw(band); bd.rectangle([0,0,W-81,169],outline=(225,225,225),width=5)
    fb=ImageFont.truetype(FB,62 if len(a)<7 else 52); outline_text(bd,((W-80)//2,52),a,fb,(255,250,235)); outline_text(bd,((W-80)//2,122),b,ImageFont.truetype(FB,58),light)
    F.paste(band,(40,70))
    # emblem
    cx,cy,R=W//2,400,150
    d.ellipse([cx-R-14,cy-R-14,cx+R+14,cy+R+14],fill=(30,26,22)); d.ellipse([cx-R-8,cy-R-8,cx+R+8,cy+R+8],fill=(215,215,220)); d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(245,236,210))
    d.ellipse([cx-R+18,cy-R+18,cx+R-18,cy+R-18],outline=col,width=10)
    icon(d,ic,cx,cy,R*.55,dark)
    fo=ImageFont.truetype(FO,30); outline_text(d,(cx,cy+R+40),'IITSTY SODA CO.',fo,(245,236,210),sw=3)
    # window area (the 3D display case sits on it) + dispenser + kick plate
    d.rectangle([90,610,W-90,790],fill=(12,10,9)); d.rectangle([84,604,W-84,796],outline=(200,200,205),width=6)
    d.rectangle([130,870,W-130,940],fill=(8,6,5)); d.rectangle([124,864,W-124,946],outline=(160,160,165),width=5)
    outline_text(d,(cx,840),'DRINK UP · SURVIVE',ImageFont.truetype(FO,26),light,sw=2)
    F=scratches(grime(F)); F.save(OUT+f'{k}_front.jpg',quality=86)
    # emissive mask: name band + emblem + slogan glow
    E=Image.new('RGB',(W,H),(0,0,0)); e=ImageDraw.Draw(E)
    E.paste(ImageEnhance.Brightness(band).enhance(1.0),(40,70)); e.ellipse([cx-R,cy-R,cx+R,cy+R],fill=tuple(int(c*.55) for c in light)); icon(e,ic,cx,cy,R*.55,(0,0,0))
    E=E.filter(ImageFilter.GaussianBlur(1)); E.save(OUT+f'{k}_glow.jpg',quality=85)
    # side panel
    Sd=paint(col,512,1024); sd=ImageDraw.Draw(Sd)
    Sd.paste(tile(rivet,512,220).resize((512,220)),(0,804)); sd.line([(0,800),(512,800)],fill=(200,200,205),width=8)
    for x in (70,442): sd.rectangle([x-10,0,x+10,800],fill=(190,190,196))
    sd.ellipse([256-110,330-110,256+110,330+110],fill=(245,236,210)); sd.ellipse([256-110,330-110,256+110,330+110],outline=(40,30,25),width=8); icon(sd,ic,256,330,62,dark)
    outline_text(sd,(256,520),a,ImageFont.truetype(FB,54 if len(a)<7 else 46),(255,250,235)); outline_text(sd,(256,585),b,ImageFont.truetype(FB,50),light)
    Sd=scratches(grime(Sd,.6),40); Sd.save(OUT+f'{k}_side.jpg',quality=85)
    # marquee sign
    M=Image.new('RGB',(512,128),(20,14,12)); md=ImageDraw.Draw(M); md.rectangle([3,3,508,124],outline=(220,220,220),width=5)
    outline_text(md,(256,66),a+' '+b,ImageFont.truetype(FB,46 if len(a+b)<12 else 40),light,sw=3); M.save(OUT+f'{k}_marquee.jpg',quality=88)
# shared trims
ImageEnhance.Brightness(steel).enhance(1.0).save(OUT+'chrome.jpg',quality=85); rivet.save(OUT+'rivet.jpg',quality=85)
print(sorted(os.listdir(OUT)))
