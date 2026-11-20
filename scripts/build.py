#!/usr/bin/env python3
"""Build the same native HMJE game for desktop and mobile; outputs are absolute."""
import argparse,os,pathlib,shutil,subprocess,sys,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
TARGETS={'macos':('macos-app','중급닌자시험.app'),'windows':('windows-exe','Windows/중급닌자시험.exe'),'ios':('ios-sim-app','iOS/중급닌자시험.app'),'iphone':('ios-app','iPhone/중급닌자시험.app'),'android':('android-apk','Android/중급닌자시험.apk')}
def compiler():
 value=os.environ.get('HMJEC') or shutil.which('hmjec')
 if value and pathlib.Path(value).is_file():return value
 local=ROOT/'.local/toolchain.txt'
 if local.exists() and pathlib.Path(local.read_text().strip()).is_file():return local.read_text().strip()
 raise SystemExit('HMJEC 환경변수에 설치된 hmjec의 전체 경로를 지정하세요.')
def main():
 p=argparse.ArgumentParser();p.add_argument('platform',choices=TARGETS);p.add_argument('--arch',choices=['aarch64','x86_64']);p.add_argument('--run',action='store_true');args=p.parse_args()
 target,name=TARGETS[args.platform];out=ROOT/'build'/name;out.parent.mkdir(parents=True,exist_ok=True)
 generated=ROOT/'build/Generated/Game.hmje';generated.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/prepare.py'),str(generated),'--app'],check=True)
 cmd=[compiler(),'--project',str(ROOT),'--artifact','중급닌자시험','--target',target,'-o',str(out)]
 if args.platform=='windows' and sys.platform=='darwin':
  # Parallels excludes ~/Library from its Home share; keep guest linker work in the project.
  cmd+=['--cache-dir',str(ROOT/'build/windows-cache')]
 if args.arch:cmd+=['--target-arch',args.arch]
 env=os.environ.copy();env.setdefault('HMJE_JOBS','4');env.setdefault('HMJE_LINK_THREADS','4')
 if args.platform=='iphone' and (ROOT/'.local/ios-signing.json').exists():
  signing=json.loads((ROOT/'.local/ios-signing.json').read_text())
  env.setdefault('HMJE_IOS_SIGNING_IDENTITY',signing['identity'])
  env.setdefault('HMJE_IOS_PROVISIONING_PROFILE',signing['profile'])
 log=ROOT/'build'/f'{args.platform}-build.log'
 print('빌드:',args.platform,flush=True)
 with log.open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:
  print('\n'.join(log.read_text().splitlines()[-35:]));print('전체 로그:',log);return r.returncode
 print('완료:',out)
 if args.run:
  if args.platform=='macos':subprocess.run(['open',str(out)],check=True)
  elif args.platform=='windows' and os.name=='nt':subprocess.Popen([str(out)])
  else: print('시뮬레이터 또는 장치에 설치할 산출물:',out)
 return 0
if __name__=='__main__':sys.exit(main())
