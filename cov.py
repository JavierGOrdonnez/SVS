import subprocess,sys
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True,errors='replace').stdout
b=sys.argv[1]; mb=g('merge-base','origin/main','origin/'+b).strip()
tot=found=0; per=[]
for line in g('diff','-M','--name-status',mb,'origin/'+b).splitlines():
    p=line.split('\t'); s=p[0]; f=p[-1]
    if s=='D' or not f.endswith(('.py','.md','.js','.html','.csv','.json','.jsonl','.toml')): continue
    new=g('show',f'origin/{b}:{f}').splitlines()
    old=set(g('show',f'{mb}:{p[1]}').splitlines()) if s[0]=='R' or s=='M' else set()
    added=[l for l in new if l.strip() and l not in old]
    main=set(g('show',f'origin/main:{f}').splitlines())
    if s[0]=='R' and not main: main=set(g('show',f'origin/main:{f}').splitlines())
    h=sum(1 for l in added if l in main); tot+=len(added); found+=h
    if added: per.append((len(added)-h,f,len(added)))
per.sort(reverse=True)
print(f'{b}: added-lines {tot}, present in main {found} ({100*found//max(tot,1)}%)')
for m,f,n in per[:6]:
    if m: print(f'   missing {m}/{n}  {f}')
