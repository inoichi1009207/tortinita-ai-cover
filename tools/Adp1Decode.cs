// Hypatia/Kogado ADP1 → WAV(移植自 GARbro ArcFormats/Hypatia/AudioADP.cs 的解码逻辑;低半字节=声道1,高半字节=声道2)
using System; using System.IO;
class Adp { int prev=0, q=0;
 static readonly ushort[] Q={0x10,0x11,0x13,0x15,0x17,0x19,0x1C,0x1F,0x22,0x25,0x29,0x2D,0x32,0x37,0x3C,0x42,0x49,0x50,0x58,0x61,0x6B,0x76,0x82,0x8F,0x9D,0xAD,0xBE,0xD1,0xE6,0xFD,0x117,0x133,0x151,0x173,0x198,0x1C1,0x1EE,0x220,0x256,0x292,0x2D4,0x31C,0x36C,0x3C3,0x424,0x48E,0x502,0x583,0x610};
 static readonly short[] S={2,6,10,14,18,22,26,30,-2,-6,-10,-14,-18,-22,-26,-30};
 static readonly sbyte[] I={-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8};
 public short Dec(int src){ src&=0xF; int s=S[src]*Q[q]+prev; if(s<-32768)s=-32768; else if(s>32767)s=32767; prev=s; q+=I[src]; if(q<0)q=0; else if(q>48)q=48; return (short)s; } }
class P { static void Main(string[] a){
 byte[] b=File.ReadAllBytes(a[0]); int samples=BitConverter.ToInt32(b,4); uint rate=BitConverter.ToUInt32(b,8); ushort ch=BitConverter.ToUInt16(b,12);
 samples*=ch; byte[] o=new byte[2*samples]; var f=new Adp(); var s2= ch>1? new Adp(): f; int dst=0, pos=16;
 while(samples>0 && pos<b.Length){ int v=b[pos++]; short x=f.Dec(v); o[dst]=(byte)x; o[dst+1]=(byte)(x>>8); if(--samples==0)break; dst+=2; x=s2.Dec(v>>4); o[dst]=(byte)x; o[dst+1]=(byte)(x>>8); dst+=2; --samples; }
 using(var w=new BinaryWriter(File.Create(a[1]))){ w.Write(new[]{'R','I','F','F'}); w.Write(36+o.Length); w.Write(new[]{'W','A','V','E','f','m','t',' '}); w.Write(16); w.Write((short)1); w.Write((short)ch); w.Write(rate); w.Write(rate*2*ch); w.Write((short)(2*ch)); w.Write((short)16); w.Write(new[]{'d','a','t','a'}); w.Write(o.Length); w.Write(o); }
 Console.WriteLine(Path.GetFileName(a[1])+" "+ (o.Length/(2.0*ch*rate)).ToString("F1")+"s"); } }
