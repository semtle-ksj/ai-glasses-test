"""Attach native HMJE pixel and font rasterization to the browser event adapter."""
import pathlib, re, sys
path = pathlib.Path(sys.argv[1])
s = path.read_text()
draw = pathlib.Path('Sources/Game/Draw.hmje').read_text()
poly = draw[draw.index('함수 다각형은'):draw.index('함수 타원은')]
poly = poly[poly.index('    # 가까운'):].replace('p.x * scale + tx','p.x').replace('p.y * scale + ty','p.y')
poly = '함수 래스터다각형은 (pts: 점2의 배열, fill: 참거짓, width: 실수, col: 색상)를 받아\n'+poly.replace('(G,','(rasterG,').replace('(G)', '(rasterG)').replace('G는 ', 'rasterG는 ')
font = draw[draw.index('함수 글꼴은'):draw.index('함수 글폭은')].replace('함수 글꼴은','함수 래스터글꼴은').replace('size * scale','size')
# Allocate atlas cells for game text, including dynamic numbers and labels.
characters = set(range(32, 127))
for literal in re.findall(r'"([^"\n]*)"', s):
    characters.update(ord(c) for c in literal if ord(c) >= 32)
codes = ', '.join(str(c) for c in sorted(characters))
font = font.replace('    상수 f는 폰트열기(path, 자연수(n))', '    상수 codes는 ['+codes+']이고, 자연수의 배열이다.\n    상수 f는 폰트열기(path, 자연수(n), codes)')
s = s.replace('webwidth(text.주소, text.길이, size * scale, fontWeight)', '래스터폭(text, size * scale)').replace('webtext(text.주소, text.길이,','래스터문자(text,').replace('size * scale, fontWeight, align, col)', 'size * scale, align, col)')
s = s.replace('                webinit().','                webbake(1, 1, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 주소(0), 0, 1.0, 0.0, 0.0).\n                webinit().')
# A static border has four narrow runs. Keep their cached area proportional to
# the perimeter, including the forty overlapping vignette borders.
border = "    webrect(x * scale + tx, y * scale + ty, w * scale, h * scale, 0.0, col, width * scale)."
s=s.replace(border, """    상수 t는 제한(width, 0.0, 제한(w / 2.0, 0.0, h / 2.0))이다.
    사각(x, y, w, t, col).
    사각(x, y + h - t, w, t, col).
    사각(x, y + t, t, h - t * 2.0, col).
    사각(x + w - t, y + t, t, h - t * 2.0, col).""")
# Materialize each exam page when first displayed.
a=s.index("        paperImages는 []이다.",s.index("함수 정적화면준비"))
b=s.index("    G는 savedG이다.",a)
s=s[:a]+"""        paperImages는 []이다.
        변수 pageIndex는 0이다.
        pageIndex < 쪽수일 동안
            paperImages에 0을 추가한다.
            pageIndex는 pageIndex + 1이다.
        paperImageSeed는 run.id이다.
    상수 p는 run.page이다.
    만약 paperImages[p] == 0이면
        G는 webtarget(640, 690)이다.
        tx는 -165.0이다.
        ty는 -26.0이다.
        사각(165.0, 26.0, 640.0, 690.0, 색(0xf2f1ea)).
        문제지머리(p).
        run.qs의 각 q에 대해
            만약 q.n > 0 그리고 q.page == p이면
                문제그리기(q).
        paperImages[p]는 G이다.
        webrestore().
"""+s[b:]
path.write_text(s+'\n'+poly+font+pathlib.Path('web/raster.hmje').read_text())
