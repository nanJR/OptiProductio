cd /home/claude/brief
pandoc brief_v1.md -f markdown -t html --metadata pagetitle=x -o body.html
python3 -c "
s=open('page_brief.html').read();body=open('body.html').read();g=open('gloss_brief2.json').read()
open('render.html','w').write(s.replace('<div id=\"src\">BODY</div>','<div id=\"src\">'+body+'</div>').replace('const G=GLOSS;','const G='+g+';'))"
node pdf.js
rm -f pg-*.png; pdftoppm -r 45 -png brief_v1.pdf pg
python3 -c "
from PIL import Image;import glob
fs=sorted(glob.glob('pg-*.png'));ims=[Image.open(f) for f in fs];w,h=ims[0].size
for k in range(0,len(ims),8):
  g=Image.new('RGB',(w*4,h*2),'white')
  for i,im in enumerate(ims[k:k+8]):g.paste(im,((i%4)*w,(i//4)*h))
  g.save(f'grid{k//8}.png')"
