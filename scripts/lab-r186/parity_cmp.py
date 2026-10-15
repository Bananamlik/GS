import sys,glob,os
import numpy as np
from PIL import Image
a,b=sys.argv[1],sys.argv[2]
rows=[]
for f in sorted(glob.glob(a+'/*.png')):
    g=os.path.join(b,os.path.basename(f))
    if not os.path.exists(g): continue
    x=np.asarray(Image.open(f).convert('RGB')).astype(int); y=np.asarray(Image.open(g).convert('RGB')).astype(int)
    d=np.abs(x-y).max(axis=2)
    # region excluding UI: top 640 rows
    d=d[:620]
    rows.append((os.path.basename(f), (d>24).mean()*100, d.mean(), x[:620].mean(), y[:620].mean()))
for r in rows: print("%-22s diffpx>24: %6.3f%%  meanabs %.3f  lumA %.2f lumB %.2f"%r)
