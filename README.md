# 중급닌자시험 · 훈민정음 네이티브 포트

원본 커밋: `4d742f3ef05eeb143483f35454d0caa38323a93e`.
상위의 `중급닌자시험/`, 기획서, 웹 시안은 수정하지 않는다.

게임 상태·문항 생성·촬영·감독관·마킹·채점과 화면은 `Sources/Game/*.hmje`이다.
HmjeUI의 캔버스와 HmjeGraphics로 그리며 HTML, JavaScript 실행기, WebView를 쓰지 않는다.
`Native/`는 운영체제의 오디오 출력, 한국어 음성 합성, 창과 결과 이미지 내보내기를 연결한다.
음향 합성 수치와 게임 판정은 훈민정음에 있다.
Mac에서는 편집 필드가 없는 캔버스의 입력기 조합을 비활성화해 게임 키를 HmjeUI로 전달한다.

## 빌드와 실행

설치된 훈민정음 툴체인에 `HmjeUI` 플랫폼 라이브러리가 필요하다. `HMJEC` 환경변수로
컴파일러 경로를 지정하거나 PATH의 `hmjec`를 사용한다. 현재 작업 컴퓨터의 경로는
버전 관리하지 않는 `.local/toolchain.txt`에 기록했다.

```sh
python3 scripts/build.py macos --run
python3 scripts/build.py windows
python3 scripts/build.py ios      # iPhone Simulator
python3 scripts/build.py iphone   # iPhone 실기기용, 개발 서명 필요
python3 scripts/build.py android
python3 scripts/test.py
```

| 대상 | 산출물 | 조건 |
| --- | --- | --- |
| macOS 14+ | `build/중급닌자시험.app` | Apple 명령줄 개발 도구 |
| Windows 10+ | `build/Windows/중급닌자시험.exe`와 같은 폴더의 `.assets` | Windows LLVM·MSVC·Windows SDK. Mac 교차 빌드는 툴체인의 Parallels 연결 사용 |
| iPhone Simulator, iOS 17+ | `build/iOS/중급닌자시험.app` | iOS Simulator SDK |
| iPhone, iOS 17+ | `build/iPhone/중급닌자시험.app` | iOS SDK, 개발 인증서와 해당 기기를 포함하는 프로비저닝 |
| Android API 26+ | `build/Android/중급닌자시험.apk` | Android SDK/NDK, JDK. 기본 ABI arm64-v8a |

이번 컴퓨터에서 만든 기본 산출물은 모두 ARM64이다. Mac Intel·Windows x64 빌드는
`--arch x86_64`로 별도 생성할 수 있으며 이번 실행 검증에는 포함하지 않았다.
Windows의 `.assets` 폴더도 실행 파일과 함께 옮겨야 한다. Mac의 Parallels 교차 빌드에서는
게스트에서 접근할 수 있는 프로젝트 내부 `build/windows-cache`를 사용한다.
출력 파일은 모두 절대 경로로 전달해 Android 서명 도구의 작업 디렉터리에 영향을 받지 않는다.
각 빌드의 전체 로그는 `build/<대상>-build.log`에 있다.

다른 컴퓨터에서 iPhone 개발 빌드를 할 때는 다음을 지정한다.

```sh
export HMJE_IOS_SIGNING_IDENTITY='<Apple Development 인증서 이름 또는 SHA-1>'
export HMJE_IOS_PROVISIONING_PROFILE='/absolute/path/profile.mobileprovision'
python3 scripts/build.py iphone
```

이 컴퓨터의 기존 서명 조합은 `.local/ios-signing.json`에서만 읽는다. 인증서나
프로비저닝을 저장소에 복사하지 않는다. 실기기 설치는 그 프로비저닝에 등록된 기기에서만 가능하다.
앱스토어 업로드나 새 기기 등록은 수행하지 않는다.

## 조작

시험은 2분 동안 진행한다. 1~6번은 객관식, 7~8번은 단답형이며 두 쪽에 네 문항씩 실린다. 1~4번은 각 12점, 5~8번은 각 13점으로 총 100점이다.

문항을 꾹 누른다. AI 글래스는 1초, 초소형 카메라는 2.5초 동안 누르면 초점이 뜬다. 준비 중에 손을 떼면 취소된다. 초점이 뜨면 손을 떼고, 표시가 가운데 선명 구간에 왔을 때 다시 눌러 촬영한다.

휴대폰은 가로로 플레이한다. 화면을 밀어 시점을 바꾸고, 답안지를 눌러 확대하고, 칸을 눌러 직접 마킹한다. 세로로 돌리면 시간이 멈춘다. 키보드에서는 A/W/D/S로 시점을 바꾸고 Q/E로 쪽을 넘긴다. M으로 음소거를 전환한다.

## 검증 범위

`python3 scripts/test.py`는 게임 코어와 테스트를 훈민정음 네이티브 실행 파일로 빌드한다. 문항 구성과 배점, 양 끝 쪽의 넘김 제한, 촬영 준비 중 손을 뗐을 때의 취소와 초점 터치의 일회 판정, OMR 채점, 경보와 남은 시간 방송, 2분 종료와 재시작을 검사한다.

웹판은 Chrome의 모바일 터치 에뮬레이션에서 두 장비의 짧은 터치, 준비 중 취소, 초점이 보인 뒤 손을 떼고 다시 눌러 촬영하는 동작을 확인했다. 가로 화면에서 두 번째 쪽과 답안지 확대, 시간 종료 후 결과 화면까지 확인했다.

초기 이식판의 2026-11-19 검증 기록:

- macOS: 입실, 시험 시작, 교실 시점 버튼, 한글 입력 상태의 D/S/E 키, 촬영·분석 화면을 실제 앱에서 확인했다.
- Windows 11 ARM VM: 네이티브 시작 화면을 확인했다. `prlctl exec`의 서비스 세션은 D3D11 화면을 만들 수 없어 로그인된 사용자 세션에서 실행했다. 임시 실행 작업은 제거했다.
- iOS Simulator와 Android API 33 ARM 에뮬레이터: 설치·실행과 세로 방향 안내 화면을 확인했다. Android 게임 화면의 불필요한 소프트 키보드를 숨겼다.
- iPhone 실기기용: 기존 개발 인증서와 호환되는 프로비저닝으로 서명했다. 실제 iPhone 설치·터치 플레이는 확인하지 않았다.
- 코어 네이티브 테스트와 원본 30문항 대조: 실패 0.

당시 검증은 플랫폼별 수동 완주를 포함하지 않았다.
폰트 래스터화와 OS별 음성은 플랫폼에 따라 차이가 있을 수 있다.

## 소스와 자원

| 파일 | 역할 |
| --- | --- |
| `Core.hmje` | 문항·상태·감독관·촬영·답변·마킹·채점 |
| `Draw.hmje`, `Classroom.hmje`, `RoomGeometry.hmje` | 공통 그래픽 도구와 교실 |
| `Exam.hmje` | 문제지의 깨진 글자·수식·도형과 OMR |
| `Interface.hmje`, `Overlay.hmje` | 촬영 연출, 화면 정보, 메뉴와 결과 |
| `Input.hmje`, `Main.hmje` | 포인터·터치·키보드·프레임 루프 |
| `Audio.hmje`, `Share.hmje` | 음향 합성, 음성 및 결과 내보내기 |

`prepare.py`는 설치된 컴파일러와의 호환을 위해 구조체의 생략된 필드를 명시적으로
초기화하는 빌드 입력을 생성한다. 생성물도 훈민정음이며 Python은 실행 시 필요 없다.
`room.mjs`는 원본 `drawRoom`의 정적 좌표를 추출하는 개발 도구다. 재생성하려면
저장소 루트에서 `node HmjePort/scripts/room.mjs`를 실행한다.

Noto Sans KR 자원은 원본 글꼴의 500/800 웨이트를 게임에 사용하는 문자로 서브셋했다.
글꼴의 SIL Open Font License는 `Resources/fonts/OFL.txt`, miniaudio의 라이선스는
`Native/vendor/LICENSE.miniaudio`에 있다.

## 브라우저에서 실행

게임 메뉴·교실·문제지·OMR은 같은 훈민정음 소스로 그린다. 웹 타깃에서도
HmjeGraphics가 글꼴 외곽선과 도형을 픽셀로 그린다. 브라우저는 그 픽셀을 캐시하고
화면에 합성하며 포인터·키 입력, Web Audio, 음성 합성과 결과 파일 내보내기를 연결한다.

현재 작업 컴퓨터에서는 아래 명령으로 재빌드하고 로컬 서버를 실행할 수 있다.

```sh
bash web/build.sh
python3 web/serve.py --port 51082
```

브라우저에서 http://127.0.0.1:51082/ 를 연다. 빌드에는 위에서 설명한 툴체인,
Emscripten의 LLVM 도구와 천리안 HmjePort 웹 호스트 오브젝트가 필요하다.
다른 경로에 있는 천리안 체크아웃은 CHEOLLIAN_PORT로 지정한다.
배포 파일은 build/web/dist에 생성된다. pthread를 쓰므로 HTTPS(로컬은 localhost)에서
COOP same-origin, COEP require-corp 헤더를 보내야 한다. 서버 예제는 gzip을 지원하는
브라우저에 미리 압축한 WASM, JS, 자원 묶음을 올바른 Content-Encoding으로 전송한다.
