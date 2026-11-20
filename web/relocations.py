"""Initialize remaining 64-bit address fields at entry on wasm32."""
import pathlib,re,sys
p=pathlib.Path(sys.argv[1])
lines=p.read_text().splitlines()
stores=[]
for i,line in enumerate(lines):
    if not line.startswith('@') or not re.search(r'i64 ptrtoint \([^)]* to i64\)',line):continue
    head,value=re.split(r' (?:global|constant) ',line,maxsplit=1)
    ident=head.split()[0]
    if value.startswith('['):
        end=value.index(']')+1
    elif value.startswith('%'):
        end=value.index(' ')
    else:raise ValueError(line[:200])
    ty=value[:end]
    stores.append('  store '+value+', ptr '+ident)
    lines[i]=head+' global '+ty+' zeroinitializer, align 8'
entry=next(i for i,l in enumerate(lines) if l.startswith('define i32 @hmje_app_main('))
pos=entry+1
if lines[pos].endswith(':'):pos+=1
lines[pos:pos]=['  call void @ninja_web_relocations()']
lines.extend(['define internal void @ninja_web_relocations() noinline optnone {',*stores,'  ret void','}'])
p.write_text('\n'.join(lines)+'\n')
