import re
def blocks(f):
    s=open(f).read(); R=re.compile(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n',re.S); return s,R
MAP={'T96':'T107','T97':'T108','T98':'T109','T99':'T110'}
# SPEC-crime
f='src/crime/SPEC-crime.md'; s,R=blocks(f); m=R.search(s); h,t=m.group(1),m.group(2)
add=[]
for l in h.splitlines():
    k=l.split('|')[1].strip() if l.startswith('| T') else ''
    if k in MAP:
        n=MAP[k]; l=re.sub(r'^\| T\d+ ',f'| {n} ',l.rstrip()); l=l[:-2]+f'; SIA:CRIME-{n} |'
        for a,b in MAP.items(): l=re.sub(r'\b'+a+r'\b',b,l) if not l.startswith(f'| {b} ') else l
        add.append(l)
# fix intra-row references (mentions inside rows) for all four
add=[ re.sub(r'\bT(96|97|98|99)\b',lambda x:MAP['T'+x.group(1)],l.split('|',2)[2]) and l for l in add]
s=s[:m.start()]+t+'\n'.join(add)+'\n'+s[m.end():]; open(f,'w').write(s)
# SPEC.md
f='SPEC.md'; s,R=blocks(f); m=R.search(s); t=m.group(2).replace('T76-T88 |','T76-T88, T93-T95, T107-T110 |'); s=s[:m.start()]+t+s[m.end():]; open(f,'w').write(s)
# PIPELINE
f='data/PIPELINE.md'; s,R=blocks(f); ms=list(R.finditer(s)); out=s
for m in reversed(ms):
    h,t=m.group(1),m.group(2)
    if 'mir_migrant_nationality_parser' in h:
        r=h  # keep HEAD's reference/ path
        extra=[l for l in t.splitlines(True) if l.startswith('| `macroencuesta_parser.py`')]
        new=r+''.join(extra)
    else:
        new=t.replace('hate_crimes_mir_2016-2021_2023.json','hate_crimes_mir_2014-2025.json')
    out=out[:m.start()]+new+out[m.end():]
open(f,'w').write(out)
