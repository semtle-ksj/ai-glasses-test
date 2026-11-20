"""Use native wasm32 indices in LLVM pointer arithmetic."""
import pathlib,re,sys
p=pathlib.Path(sys.argv[1]);out=[]
for i,line in enumerate(p.read_text().splitlines()):
    if ' = getelementptr ' in line:
        def index(m):
            value=m[1]
            if value.startswith('%'):
                name=f'%ninja_index_{i}_{len(out)}'
                out.append(f'  {name} = trunc i64 {value} to i32')
                value=name
            return ', i32 '+value
        line=re.sub(r', i64 (%[\w.]+|-?\d+)(?=,|$)', index,line)
    out.append(line)
p.write_text('\n'.join(out)+'\n')
