"""SONG.ADP 解码假设试探:按 IMA ADPCM 四种立体声排布各解前 8 秒,报 L/R 相关与谱平坦度。"""
import numpy as np, struct, sys, librosa
STEP=[7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,55,60,66,73,80,88,97,107,118,130,143,157,173,190,209,230,253,279,307,337,371,408,449,494,544,598,658,724,796,876,963,1060,1166,1282,1411,1552,1707,1878,2066,2272,2499,2749,3024,3327,3660,4026,4428,4871,5358,5894,6484,7132,7845,8630,9493,10442,11487,12635,13899,15289,16818,18500,20350,22385,24623,27086,29794,32767]
IDX=[-1,-1,-1,-1,2,4,6,8]
def ima(nib):
    out=np.empty(len(nib),dtype=np.int16); pred=0; idx=0
    for i,n in enumerate(nib):
        st=STEP[idx]; d=st>>3
        if n&1: d+=st>>2
        if n&2: d+=st>>1
        if n&4: d+=st
        pred = pred-d if n&8 else pred+d
        pred=max(-32768,min(32767,pred)); idx=max(0,min(88,idx+IDX[n&7])); out[i]=pred
    return out
p=sys.argv[1]; b=open(p,'rb').read()
ln,rate,ch=struct.unpack_from('<III',b,4); OFF=int(sys.argv[2]) if len(sys.argv)>2 else 0  # 起始秒(跳过前奏静音)
data=np.frombuffer(b[16+rate*OFF:16+rate*(OFF+8)],dtype=np.uint8)  # 8 秒(每字节 2 样本, 双声道 ⇒ rate 字节/秒)
lo=data&15; hi=data>>4
layouts={'A:低L高R':(lo,hi),'B:高L低R':(hi,lo),
 'C:偶字节L奇字节R(低先)':(np.stack([data[0::2]&15,data[0::2]>>4],1).ravel(), np.stack([data[1::2]&15,data[1::2]>>4],1).ravel()),
 'D:偶字节L奇字节R(高先)':(np.stack([data[0::2]>>4,data[0::2]&15],1).ravel(), np.stack([data[1::2]>>4,data[1::2]&15],1).ravel())}
for k,(L,R) in layouts.items():
    l=ima(L).astype(np.float32)/32768; r=ima(R).astype(np.float32)/32768
    corr=float(np.corrcoef(l[rate*2:],r[rate*2:])[0,1]); fl=float(librosa.feature.spectral_flatness(y=l[rate*2:]).mean())
    print(f"{k}: L/R相关={corr:.3f} 谱平坦度={fl:.5f} RMS={20*np.log10(np.sqrt(np.mean(l**2))+1e-9):.1f}dBFS")
