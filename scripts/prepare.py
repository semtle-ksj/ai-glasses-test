#!/usr/bin/env python3
"""Expand default struct fields for installed pre-default-initializer toolchains."""
import pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
text=(root/'Sources/Game/Core.hmje').read_text()
if '--app' in sys.argv:
    text+='\n'+'\n'.join(p.read_text() for p in sorted((root/'Sources/Game').glob('*.hmje')) if p.name not in ('Core.hmje','Main.hmje'))+'\n'+(root/'Sources/Game/Main.hmje').read_text()
structs={}
for m in re.finditer(r'^구조체 (\w+)의\n((?:    .*\n)+)',text,re.M):
    fields={}
    for fm in re.finditer(r'변수 (\w+)[은는] (.+?)(?:이고,|이다\.)',m[2]):
        fields[fm[1]]=fm[2]
    structs[m[1]]=fields

def default(typ):
    if typ in structs:
        return typ+'('+', '.join(k+': '+default(t) for k,t in structs[typ].items())+')'
    if '고정배열' in typ:
        return '['+', '.join([default(typ.split()[0])]*int(re.search(r'(\d+)개',typ)[1]))+']'
    if '배열' in typ:
        return '[]'
    return {'실수':'0.0','자연수':'자연수(0)','정수':'0','문자열':'""','참거짓':'거짓'}[typ]
# Parse balanced calls, preserving nested expressions/strings.
def expand(s):
    pattern=re.compile(r'\b('+ '|'.join(structs)+r')\(')
    pos=0; out=[]
    while m:=pattern.search(s,pos):
        out.append(s[pos:m.start()]); depth=1; end=m.end(); quoted=False; escape=False
        while depth:
            c=s[end]
            if quoted:
                if escape: escape=False
                elif c=='\\': escape=True
                elif c=='"': quoted=False
            elif c=='"': quoted=True
            elif c=='(': depth+=1
            elif c==')': depth-=1
            end+=1
        body=expand(s[m.end():end-1]); parts=[]; start=0; depth=0; quoted=False; escape=False
        for i,c in enumerate(body):
            if quoted:
                if escape: escape=False
                elif c=='\\': escape=True
                elif c=='"': quoted=False
            elif c=='"': quoted=True
            elif c in '([': depth+=1
            elif c in ')]': depth-=1
            elif c==',' and depth==0:
                parts.append(body[start:i].strip()); start=i+1
        if body[start:].strip(): parts.append(body[start:].strip())
        values={p.split(':',1)[0].strip():p.split(':',1)[1].strip() for p in parts}
        out.append(m[1]+'('+', '.join(k+': '+values.get(k,default(t)) for k,t in structs[m[1]].items())+')')
        pos=end
    out.append(s[pos:]); return ''.join(out)
for name in structs:
    text=re.sub(r'(전역 변수 \w+[은는] )'+name+r'이다\.',lambda m:m[1]+default(name)+'이고, '+name+'이다.',text)
text=expand(text)
# Explicit float arrays: older literal inference defaults constants to integer arrays.
text=re.sub(r'(상수 \w+[은는] )(\[[^\n]+\])이다\.',lambda m:m[1]+m[2]+('이고, 실수 '+str(len(m[2][1:-1].split(',')))+'개의 고정배열이다.' if re.search(r'\d\.\d|\bPI\b',m[2]) else '이다.'),text)
if __name__=='__main__':
    output=pathlib.Path(sys.argv[1])
    import tempfile,os
    with tempfile.NamedTemporaryFile(mode='w',dir=output.parent,delete=False,suffix='.tmp') as handle:
        handle.write(text+('\n'+pathlib.Path(sys.argv[2]).read_text() if len(sys.argv)>2 and sys.argv[2]!='--app' else ''))
        temporary=handle.name
    os.replace(temporary,output)
