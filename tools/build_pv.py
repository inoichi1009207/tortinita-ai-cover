"""PV 草稿(无歌词层):1080p30,开场/收尾用游戏 OP 实拍,中段 8 场景 = 背景 CG + 朵朵立绘(翅膀叠底),场景间 1s 交叉淡;音频 = goodbye_torta_final_v2.mp3。
歌词层留待时间轴到手后用 overlay enable=between(t,a,b) 叠加。"""
import subprocess, os
from PIL import Image
W,H=1920,1080
os.makedirs('pv/scenes',exist_ok=True)
def scene(bg, sprite, out, scale=2.4, x_from_right=170, y_off=60, wings=None, wing_pos=(0.32,0.30), mirror=False):
    b=Image.open(f'pv/assets/bg/{bg}.png').convert('RGB').resize((W,H),Image.LANCZOS).convert('RGBA')
    sp=Image.open(f'pv/assets/sprites/{sprite}.png').convert('RGBA')
    if mirror: sp=sp.transpose(Image.FLIP_LEFT_RIGHT)
    layer=Image.new('RGBA',sp.size,(0,0,0,0))
    if wings:
        wg=Image.open(f'pv/assets/sprites/{wings}.png').convert('RGBA'); layer.alpha_composite(wg,(int(sp.width*wing_pos[0]),int(sp.height*wing_pos[1])))
    layer.alpha_composite(sp)
    layer=layer.resize((int(sp.width*scale),int(sp.height*scale)),Image.LANCZOS)
    b.alpha_composite(layer,(W-layer.width-x_from_right, H-layer.height+y_off))
    b.convert('RGB').save(out,quality=95)
# 朵鲁妲 = 红裙扎发的那位(srchr010–019/122/139–143/149–151);带音符的 127–130 是芙铃(Phorni),之前选错
scenes=[ # (背景, 立绘, 时长秒)
 ('srbg184','srchr122',22),('srbg026','srchr013',26),('srbg054','srchr019',22),('srbg305','srchr151',26),
 ('srbg165','srchr014',22),('srbg284','srchr143',26),('srbg354','srchr141',24),('srbg024','srchr149',26)]
paths=[]
for i,(bg,sp,d) in enumerate(scenes):
    p=f'pv/scenes/s{i:02d}.jpg'; scene(bg,sp,p,scale=2.25,x_from_right=140,y_off=0,wings=None); paths.append((p,d))
OP=r'D:/znsy/交响乐之雨/交响乐之雨/SROP.MPG'
TOTAL=218.86; XF=1.0
intro=12.0; outro=TOTAL-intro-sum(d for _,d in paths)+XF*(len(paths)+1)  # 让总长对齐音频
cmd=['ffmpeg','-y','-loglevel','error','-ss','5','-t',str(intro+XF),'-i',OP]
for p,d in paths: cmd+=['-loop','1','-t',str(d+XF),'-i',p]
cmd+=['-ss','60','-t',str(outro+XF),'-i',OP,'-i','goodbye_torta_final_v2.mp3']
n=len(paths)+2
fc=[f'[0:v]crop=640:360:0:60,scale={W}:{H},fps=30,setsar=1,format=yuv420p[v0]']
for i in range(1,n-1): fc.append(f'[{i}:v]scale={W}:{H},fps=30,setsar=1,format=yuv420p[v{i}]')
fc.append(f'[{n-1}:v]crop=640:360:0:60,scale={W}:{H},fps=30,setsar=1,format=yuv420p[v{n-1}]')
durs=[intro+XF]+[d+XF for _,d in paths]+[outro+XF]
prev='v0'; off=0.0
for i in range(1,n):
    off+=durs[i-1]-XF; fc.append(f'[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]'); prev=f'x{i}'
fc.append(f'[{prev}]fade=t=in:st=0:d=1.5,fade=t=out:st={TOTAL-2.5:.2f}:d=2.5[vout]')
cmd+=['-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{n}:a','-c:v','libx264','-pix_fmt','yuv420p','-profile:v','high','-preset','medium','-crf','20','-movflags','+faststart','-c:a','aac','-b:a','256k','-shortest','pv/draft_pv_nolyrics.mp4']
print('outro',round(outro,2)); r=subprocess.run(cmd); print('ffmpeg exit',r.returncode)
