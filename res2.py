import re,sys
f,mod=sys.argv[1:3]; ids=sys.argv[3:]
s=open(f).read()
m=re.search(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n',s,re.S)
head=m.group(1).splitlines(); th={l.split('|')[1].strip():l for l in m.group(2).splitlines() if l.startswith('| T')}
out=[];seen=set()
for l in head:
    i=l.split('|')[1].strip() if l.startswith('| T') else None
    if i in ids: l=th[i].rstrip()[:-2]+f'; SIA:{mod}-{i} |'; seen.add(i)
    out.append(l)
for i in ids:
    if i not in seen: out.append(th[i].rstrip()[:-2]+f'; SIA:{mod}-{i} |')
s=s[:m.start()]+'\n'.join(out)+'\n'+s[m.end():]
open(f,'w').write(s)
