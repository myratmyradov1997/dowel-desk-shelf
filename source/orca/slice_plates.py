"""Slice plates with a flattened profile dir; writes gcode + 3mf + summary.
Usage: python3 slice_plates.py PROFILE_DIR OUT_DIR plates.json"""
import json,os,re,subprocess,sys
O='/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer'
prof,out,plan=os.path.abspath(sys.argv[1]),os.path.abspath(sys.argv[2]),json.load(open(sys.argv[3]))
os.makedirs(out,exist_ok=True)
rows=[]
for plate,files in plan.items():
    wd=os.path.join(out,'_work',plate);os.makedirs(wd,exist_ok=True)
    for f in os.listdir(wd):os.remove(os.path.join(wd,f))
    cmd=[O,'--arrange','1','--orient','0','--slice','0','--load-settings',prof+'/machine.json;'+prof+'/process.json',
         '--load-filaments',prof+'/filament.json','--outputdir',wd,'--export-3mf',plate+'.3mf']+[os.path.expanduser(f) for f in files]
    r=subprocess.run(cmd,cwd=wd,capture_output=True,text=True)
    g=os.path.join(wd,'plate_1.gcode')
    if r.returncode or not os.path.exists(g):
        rows.append(dict(plate=plate,error=r.returncode));print(plate,'FAILED',r.returncode);continue
    txt=open(g,errors='ignore').read()
    w=float(re.search(r'; total filament used \[g\] = ([\d.]+)',txt).group(1))
    t=re.search(r'; estimated printing time \(normal mode\) = (.+)',txt).group(1).strip()
    s=sum(int(v)*{'d':86400,'h':3600,'m':60,'s':1}[u] for v,u in re.findall(r'(\d+)([dhms])',t))
    h,m=s//3600,s%3600//60
    name='%s_%dh%02dm.gcode'%(plate,h,m)
    os.replace(g,os.path.join(out,name))
    if os.path.exists(os.path.join(wd,plate+'.3mf')):os.replace(os.path.join(wd,plate+'.3mf'),os.path.join(out,plate+'.3mf'))
    rows.append(dict(plate=plate,parts=[os.path.basename(f) for f in files],grams=w,time=t,seconds=s,gcode=name))
    print(plate,w,'g',t)
tot_g=sum(r.get('grams',0) for r in rows);tot_s=sum(r.get('seconds',0) for r in rows)
json.dump(dict(profile=json.load(open(prof+'/process.json'))['name'],filament=json.load(open(prof+'/filament.json'))['name'],
               total_g=round(tot_g,1),total_h=round(tot_s/3600,1),plates=rows),open(os.path.join(out,'summary.json'),'w'),indent=2,ensure_ascii=False)
print('TOTAL',round(tot_g),'g',round(tot_s/3600,1),'h')
