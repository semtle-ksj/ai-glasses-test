"""Specialize the shared HMJE game for the browser's vector canvas backend."""
import pathlib, re, sys, textwrap
path=pathlib.Path(sys.argv[1])
s=path.read_text()
def block(start,end,new):
    global s
    a=s.index(start);b=s.index(end,a);s=s[:a]+new+'\n'+s[b:]
block('함수 색은','구조체 점2의','''함수 색은 (v: 자연수)를 받아
    ((v << 8) + 255)를 자연수로 반환한다.
함수 알파색은 (v: 자연수, a: 실수)를 받아
    ((v << 8) + 자연수(제한(a * 255.0, 0.0, 255.0)))를 자연수로 반환한다.
함수 사각은 (x: 실수, y: 실수, w: 실수, h: 실수, col: 자연수)를 받아
    webrect(x * scale + tx, y * scale + ty, w * scale, h * scale, 0.0, col, 0.0).
함수 둥근상자는 (x: 실수, y: 실수, w: 실수, h: 실수, r: 실수, col: 자연수)를 받아
    webrect(x * scale + tx, y * scale + ty, w * scale, h * scale, r * scale, col, 0.0).
함수 테두리는 (x: 실수, y: 실수, w: 실수, h: 실수, width: 실수, col: 자연수)를 받아
    webrect(x * scale + tx, y * scale + ty, w * scale, h * scale, 0.0, col, width * scale).
함수 선은 (x1: 실수, y1: 실수, x2: 실수, y2: 실수, width: 실수, col: 자연수)를 받아
    webline(x1 * scale + tx, y1 * scale + ty, x2 * scale + tx, y2 * scale + ty, width * scale, col).
''')
block('함수 다각형은','함수 칩은','''함수 다각형은 (pts: 점2의 배열, fill: 참거짓, width: 실수, col: 자연수)를 받아
    만약 pts.길이 >= 2이면
        webpoly(pts.데이터, pts.길이, scale, tx, ty, fill, width * scale, col).
함수 타원은 (x: 실수, y: 실수, rx: 실수, ry: 실수, rot: 실수, fill: 참거짓, width: 실수, col: 자연수)를 받아
    webellipse(x * scale + tx, y * scale + ty, rx * scale, ry * scale, rot, fill, width * scale, col).
함수 글폭은 (text: 문자열, size: 실수)를 받아
    (webwidth(text.주소, text.길이, size * scale, fontWeight) / scale)를 실수로 반환한다.
함수 글자는 (text: 문자열, x: 실수, y: 실수, size: 실수, align: 정수, col: 자연수)를 받아
    webtext(text.주소, text.길이, x * scale + tx, y * scale + ty, size * scale, fontWeight, align, col).
''')
s=s.replace('색상','자연수').replace('전역 변수 G는 그래픽만들기(0, 0)이고, 그래픽이다.', '전역 변수 G는 0이고, 정수이다.').replace('그래픽이미지의 배열','정수의 배열').replace('image: 그래픽이미지','image: 정수')
s=re.sub(r'    G는 그래픽불투명이미지스케일그리기[^\n]+','    webimage(image, x * scale + tx, y * scale + ty, w * scale, h * scale).',s)
s=re.sub(r'G는 그래픽만들기\((\d+), (\d+)\)이다\.',r'G는 webtarget(\1, \2)이다.',s)
s=re.sub(r'G는 그래픽그라데이션채우기[^\n]+','webwood().',s)
s=s.replace('그래픽이미지복사(G)','G').replace('그래픽해제를 (G)로 실행한다.', 'webrestore().')
s=s.replace('        paperImages는 []이다.', '        paperImages의 각 image에 대해\n            webdrop(image).\n        paperImages는 []이다.')
s=re.sub(r'G는 그래픽명령변형층시작\(G, \d+, \d+, (.*)\)이다\.',r'webtransform(\1).',s)
s=s.replace('G는 그래픽명령변형층끝(G, parent)이다.','webend().').replace('    만약 blur > 0.05이면\n        G는 그래픽자기블러(G, blur / s)이다.','').replace('    확대그림(deskImage[0]', '    webblur(blur / s).\n    확대그림(deskImage[0]')
s=s.replace('    상수 pixels는 그래픽픽셀바이트들(G)이고, 자연수8의 배열이다.','').replace('ninja_result(pixels.데이터, pixels.길이, 1200, 630, text.주소, text.길이, save)','webshare(G, text.주소, text.길이, save)').replace('    G는 oldG이다.', '    webdrop(G).\n    G는 oldG이다.')
s=s.replace('    카드답안지를 실행한다.', '    만약 webcardart(tx, ty, 1200.0 * scale, 630.0 * scale) == 0이면\n        카드답안지를 실행한다.')
s=s.replace('함수 화면그리기는 (g: 그래픽, 영역: 사각형)를 받아','함수 화면그리기는 (영역: 사각형)를 받아').replace('G는 그래픽사각형채우기(g, 영역, 색(0x0b0f0d))이다.','webrect(0.0, 0.0, 실수(영역.너비), 실수(영역.높이), 0.0, 색(0x0b0f0d), 0.0).').replace('G를 그래픽으로 반환한다.','반환한다.')
s=s.replace('함수 포인터처리는 (p: 포인터표본)를 받아','함수 webpointer는 (px: 실수, py: 실수, id: 자연수, phase: 정수, tool: 정수)를 받아')
for old,new in {'p.x':'px','p.y':'py','p.단계':'phase','p.도구':'tool','p.식별자':'id','포인터단계의 눌림':'1','포인터단계의 이동':'2','포인터단계의 뗌':'3','포인터단계의 취소':'4','포인터도구의 터치':'2','포인터도구의 마우스':'3'}.items():
    a=s.index('함수 webpointer');b=s.find('\n함수 ',a+4);s=s[:a]+s[a:b].replace(old,new)+s[b:]
base,loop=s.split('화면 게임화면의',1)
init=loop.split('    비동기 작업은\n')[1].split('        변수 last')[0]
tick=loop.split('            last는 now이다.\n')[1].split('            tick은')[0]
keys=loop.split('    A키를 누르면\n')[1].split('    그리는 내용은')[0]
s=base+'함수 webinit은\n'+textwrap.indent(textwrap.dedent(init),'    ')+'\n함수 webframe은 (dt: 실수, w: 자연수, h: 자연수)를 받아\n    canvasWidth는 실수(w)이다.\n    canvasHeight는 실수(h)이다.\n'+textwrap.indent(textwrap.dedent(tick),'    ')+'    화면그리기(사각형만들기(0, 0, w, h)).\n'
s+='함수 webkey는 (key: 정수)를 받아\n    만약 key == 65이면\n'+re.sub(r'    ([WDSEQ M])키를 누르면',lambda m:'    만약 key == '+str(ord(m[1]))+'이면',keys)
# Keep the public browser entry points in the compiler's reachable module.
s+='''화면 게임화면의
    그리는 내용은
        캔버스의
            그리기는 그래픽과 영역을 받아
                webinit().
                webframe(0.0, 1, 1).
                webkey(0).
                webpointer(0.0, 0.0, 0, 4, 3).
화면을 표시하는 함수 앱시작은
    그리는 내용은
        게임화면이다.
'''
decls={}
for row in """webrect d d d d d u d
webline d d d d d u
webpoly p u d d d b d u
webellipse d d d d d b d u
webwidth p u d i >d
webtext p u d d d i i u
webimage i d d d d
webtarget i i >i
webrestore
webwood
webdrop i
webtransform d d d d d d
webblur d
webend
webcardart d d d d >i
webshare i p u i >i""".splitlines():
    name,*args=row.split();ret=args.pop()[1:] if args and args[-1].startswith('>') else ''
    t={'i':'정수','u':'자연수','d':'실수','p':'주소','b':'참거짓'}
    params=', '.join(f'a{i}: {t[arg]}' for i,arg in enumerate(args))
    decls[name]='외부 함수 '+name+'는 '+(('('+params+')를 받아 '+t[ret]+'로 반환한다.') if ret else ('('+params+')를 받는다.' if params else '받지 않는다.'))
path.write_text('\n'.join(decls.values())+'\n'+s)
