"""Expose the HMJE event handlers and let requestAnimationFrame drive the web host."""
import pathlib,re,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
if len(sys.argv) > 2 and int(sys.argv[2].split('.')[0]) >= 22:
    # HMJE discards coro.end's former i1 result. LLVM 22 declares it void.
    s = s.replace('declare i1 @llvm.coro.end(', 'declare void @llvm.coro.end(')
    s = re.sub(r'%\w+ = call i1 @llvm\.coro\.end\(', 'call void @llvm.coro.end(', s)
for name in ('init','frame','key','pointer','bake'):
    prefix='_'.join('web'+name)
    match=re.search(r'^define void @([^ (]+___'+prefix+r'__[^ (]+)\(',s,re.M)
    if not match:raise RuntimeError(name)
    s=s.replace('@'+match[1]+'(', '@game_'+name+'(')
start=s.index('define i32 @hmje_app_main()')
a=s.index('  call void @hmje_fn_uc571_uc2dc_uc791__void()',start)
b=s.index('\n}',a)
s=s[:a]+'  ret i32 0'+s[b:]
p.write_text(s)
