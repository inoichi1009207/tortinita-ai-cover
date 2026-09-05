// HyPack v3 SCRIPT.PAK 提取宿主:链 GARbro 的 KogadoCocotte.cs(GPL v2 派生,许可证见仓根 LICENSE)。
// 用法: ExtractScript.exe <SCRIPT.PAK> <outDir>
using System;
using System.IO;
using GameRes.Formats.Kogado;

class ExtractScript
{
    static string ReadStr(byte[] d, long o, int n)
    {
        int end = (int)o;
        while (end < o + n && d[end] != 0) end++;
        return System.Text.Encoding.ASCII.GetString(d, (int)o, end - (int)o);
    }

    static void Main(string[] args)
    {
        string pak = args[0], outDir = args[1];
        Directory.CreateDirectory(outDir);
        byte[] data = File.ReadAllBytes(pak);
        if (data[0] != 'H' || data[1] != 'y') { Console.WriteLine("NOT_HYPACK"); return; }
        uint idx = 0x10 + BitConverter.ToUInt32(data, 8);
        uint count = BitConverter.ToUInt32(data, 12);
        int ok = 0, fail = 0;
        for (uint i = 0; i < count; i++)
        {
            long rec = idx + 48 * i;
            string name = ReadStr(data, rec, 0x15);
            string ext = ReadStr(data, rec + 0x15, 3);
            uint off = 0x10 + BitConverter.ToUInt32(data, (int)rec + 0x18);
            uint unpacked = BitConverter.ToUInt32(data, (int)rec + 0x1c);
            uint packed = BitConverter.ToUInt32(data, (int)rec + 0x20);
            byte comp = data[rec + 0x24];
            string outPath = Path.Combine(outDir, name + "." + ext);
            if (comp == 0)
            {
                using (FileStream w = File.Create(outPath)) { w.Write(data, (int)off, (int)packed); }
                ok++;
                continue;
            }
            if (comp == 2)
            {
                using (MemoryStream ms = new MemoryStream(data, (int)off, (int)packed))
                using (FileStream w = File.Create(outPath))
                {
                    CocotteEncoder dec = new CocotteEncoder();
                    bool good = dec.Decode(ms, w);
                    if (good && w.Length == unpacked) ok++;
                    else { fail++; Console.WriteLine("FAIL " + name + " got=" + w.Length + " want=" + unpacked); }
                }
                continue;
            }
            Console.WriteLine("SKIP comp=" + comp + " " + name);
            fail++;
        }
        Console.WriteLine("OK=" + ok + " FAIL=" + fail + " COUNT=" + count);
    }
}
