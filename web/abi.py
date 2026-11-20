"""Bridge HMJE's 64-bit host addresses to wasm32 libc calls."""
import pathlib,re,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
for name in 'getcwd getenv memmem freeaddrinfo mkdir clock_gettime poll getsockopt setsockopt fread fwrite ferror chdir localtime_r getaddrinfo connect free memcpy realloc memchr memcmp malloc memset'.split():
    match=re.search(r'^declare (i32|i64|void) @'+name+r'\(([^)]*)\)$',s,re.M)
    ret,args=match.groups();args=args.split(', ')
    s=re.sub('@'+name+r'\(', '@ninja32_'+name+'(',s)
    out='i32' if ret=='i64' else ret
    body=[f'declare {out} @{name}('+', '.join(['i32']*len(args))+')',f'define {ret} @ninja32_{name}('+', '.join(f'{ty} %a{i}' for i,ty in enumerate(args))+') {']
    actual=[]
    for i,ty in enumerate(args):
        val=f'%a{i}'
        if ty=='i64':
            body.append(f'  %b{i} = trunc i64 {val} to i32');val=f'%b{i}'
        actual.append('i32 '+val)
    body.append('  '+('%res = ' if ret!='void' else '')+f'call {out} @{name}('+', '.join(actual)+')')
    if ret=='i64':body+=['  %addr = zext i32 %res to i64','  ret i64 %addr']
    else:body+=['  ret '+ret+(' %res' if ret!='void' else '')]
    s=s.replace(match.group().replace('@'+name+'(', '@ninja32_'+name+'('),'',1)+'\n'+'\n'.join(body+['}'])+'\n'
p.write_text(s)
