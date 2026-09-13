import json,sys,subprocess
tid,name=sys.argv[1],sys.argv[2]
d=json.load(open(f'/tmp/claude-1000/-home-hoid-Desktop/745c70e6-c1cb-44ec-873c-7451b28a08ea/tasks/{tid}.output'))
r=(d.get('result') or d)
out=f'research/recon_results/{name}.json'
json.dump(r['results'],open(out,'w'),indent=1,ensure_ascii=False)
print(name,'results:',len(r['results']),'failed:',r.get('batches_failed'))
print(subprocess.run(['python3','scripts/apply_recon.py',out],capture_output=True,text=True).stdout.strip())
