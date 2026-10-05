import re,sys
f,code,tid=sys.argv[1:4]
s=open(f).read()
m=re.search(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n',s,re.S)
head,theirs=m.group(1),m.group(2)
row=[l for l in theirs.splitlines() if l.startswith(f'| {tid} ')][0].rstrip()
assert row.endswith(' |'); row=row[:-2]+f'; SIA:{code} |'
s=s[:m.start()]+head+row+'\n'+s[m.end():]
open(f,'w').write(s)
