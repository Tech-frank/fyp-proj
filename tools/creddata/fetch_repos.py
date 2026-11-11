import csv,glob,json,subprocess,os,sys,random
need=json.load(open('needed_repos.json'))
rows=[]
for f in glob.glob('creddata/meta/*.csv'):
    rows+=list(csv.DictReader(open(f,newline='',encoding='utf-8')))
def testy(p): p=p.lower(); return any(w in p for w in ('test','example','sample','demo','fixture','mock'))
py=[r for r in rows if r['FilePath'].endswith('.py') and not testy(r['FilePath'])]
t_repos=sorted({r['RepoName'] for r in py if r['GroundTruth']=='T'})
f_only=sorted({r['RepoName'] for r in py if r['GroundTruth']=='F'}-set(t_repos))
random.seed(7); random.shuffle(f_only)
order=t_repos+f_only[:15]
os.makedirs('repos',exist_ok=True)
ok=[]
for name in order:
    full,url=need[name]; sha=full[:40]; d=f'repos/{name}'
    if os.path.exists(d+'/.done'): ok.append(name); continue
    subprocess.run(['rm','-rf',d]); os.makedirs(d)
    try:
        for cmd in (['git','init','-q'],['git','remote','add','origin',url],
                    ['git','fetch','-q','--depth','1','origin',sha],['git','checkout','-q',sha]):
            subprocess.run(cmd,cwd=d,check=True,timeout=300,capture_output=True)
        open(d+'/.done','w').close(); ok.append(name); print('OK',name,url,flush=True)
    except Exception as e:
        print('FAIL',name,url,type(e).__name__,flush=True)
        subprocess.run(['rm','-rf',d])
json.dump(ok,open('fetched.json','w')); print(len(ok),'fetched of',len(order))
