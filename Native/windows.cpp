#define NOMINMAX
#include <windows.h>
#include <commdlg.h>
#include <sapi.h>
#include <wincodec.h>
#include <stdint.h>
#include <string>
static ISpVoice *voice;
static bool checked;
static std::wstring utf16(const uint8_t *s,uint64_t n) {
    if(!s || n>16384) return L"";
    int count=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,(const char*)s,(int)n,NULL,0);
    std::wstring result(count,L'\0');
    if(count) MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,(const char*)s,(int)n,&result[0],count);
    return result;
}
extern "C" int64_t ninja_speech_ready(void) {
    if(!checked) {
        checked=true; CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);
        if(SUCCEEDED(CoCreateInstance(CLSID_SpVoice,NULL,CLSCTX_ALL,IID_ISpVoice,(void**)&voice))) {
            IEnumSpObjectTokens *tokens=NULL;
            ISpObjectTokenCategory *category=NULL;
            HRESULT found=CoCreateInstance(CLSID_SpObjectTokenCategory,NULL,CLSCTX_ALL,IID_ISpObjectTokenCategory,(void**)&category);
            if(SUCCEEDED(found)) found=category->SetId(SPCAT_VOICES,FALSE);
            if(SUCCEEDED(found)) found=category->EnumTokens(L"Language=412",NULL,&tokens);
            if(category) category->Release();
            if(SUCCEEDED(found)) {
                ISpObjectToken *token=NULL;
                if(tokens->Next(1,&token,NULL)==S_OK) { voice->SetVoice(token); token->Release(); }
                else { voice->Release(); voice=NULL; }
                tokens->Release();
            } else { voice->Release(); voice=NULL; }
        }
    }
    return voice!=NULL;
}
extern "C" int64_t ninja_speech(const uint8_t *text,uint64_t n,double rate,double pitch,double volume,int64_t interrupt) {
    (void)pitch;
    if(!ninja_speech_ready()) return 0;
    voice->SetRate((LONG)((rate-1)*10)); voice->SetVolume((USHORT)(volume*100));
    auto wide=utf16(text,n);
    return SUCCEEDED(voice->Speak(wide.c_str(),SPF_ASYNC|(interrupt?SPF_PURGEBEFORESPEAK:0),NULL));
}
extern "C" void ninja_speech_stop(void) { if(voice) voice->Speak(NULL,SPF_PURGEBEFORESPEAK,NULL); }
extern "C" int64_t ninja_result(const uint8_t *pixels,uint64_t n,int64_t w,int64_t h,const uint8_t *text,uint64_t tn,int64_t save) {
    (void)text; (void)tn;
    if(!save) return 0; /* HMJE copies text to clipboard, matching desktop browser fallback. */
    if(!pixels || w<1 || h<1 || n!=(uint64_t)w*h*4) return 0;
    wchar_t path[MAX_PATH]=L"중급닌자시험-결과.png";
    OPENFILENAMEW ofn={sizeof(ofn)}; ofn.hwndOwner=GetActiveWindow(); ofn.lpstrFile=path; ofn.nMaxFile=MAX_PATH;
    ofn.lpstrFilter=L"PNG image\0*.png\0\0"; ofn.lpstrDefExt=L"png"; ofn.Flags=OFN_OVERWRITEPROMPT;
    if(!GetSaveFileNameW(&ofn)) return 1;
    IWICImagingFactory *factory=NULL; IWICStream *stream=NULL; IWICBitmapEncoder *encoder=NULL; IWICBitmapFrameEncode *frame=NULL; IPropertyBag2 *props=NULL;
    CoInitializeEx(NULL,COINIT_APARTMENTTHREADED);
    HRESULT hr=CoCreateInstance(CLSID_WICImagingFactory,NULL,CLSCTX_INPROC_SERVER,IID_PPV_ARGS(&factory));
    if(SUCCEEDED(hr)) hr=factory->CreateStream(&stream);
    if(SUCCEEDED(hr)) hr=stream->InitializeFromFilename(path,GENERIC_WRITE);
    if(SUCCEEDED(hr)) hr=factory->CreateEncoder(GUID_ContainerFormatPng,NULL,&encoder);
    if(SUCCEEDED(hr)) hr=encoder->Initialize(stream,WICBitmapEncoderNoCache);
    if(SUCCEEDED(hr)) hr=encoder->CreateNewFrame(&frame,&props);
    if(SUCCEEDED(hr)) hr=frame->Initialize(props);
    if(SUCCEEDED(hr)) hr=frame->SetSize((UINT)w,(UINT)h);
    WICPixelFormatGUID format=GUID_WICPixelFormat32bppBGR;
    if(SUCCEEDED(hr)) hr=frame->SetPixelFormat(&format);
    if(SUCCEEDED(hr)) hr=frame->WritePixels((UINT)h,(UINT)w*4,(UINT)n,(BYTE*)pixels);
    if(SUCCEEDED(hr)) hr=frame->Commit();
    if(SUCCEEDED(hr)) hr=encoder->Commit();
    if(props) props->Release(); if(frame) frame->Release(); if(encoder) encoder->Release(); if(stream) stream->Release(); if(factory) factory->Release();
    return SUCCEEDED(hr);
}
extern "C" int64_t ninja_is_touch(void) { return 0; }
extern "C" void ninja_configure_window(void) { HWND w=GetActiveWindow(); if(w){RECT r={0,0,1280,720};AdjustWindowRect(&r,(DWORD)GetWindowLongPtr(w,GWL_STYLE),FALSE);SetWindowPos(w,NULL,0,0,r.right-r.left,r.bottom-r.top,SWP_NOMOVE|SWP_NOZORDER);} }
