#include <emscripten.h>
#include <stdint.h>
typedef int64_t I;
I ninja_is_touch(void){return MAIN_THREAD_EM_ASM_INT({return matchMedia('(pointer:coarse)').matches;});}
void ninja_configure_window(void){}
I ninja_audio_open(void){return MAIN_THREAD_EM_ASM_INT({return !!window.ninjaAudio;});}
I ninja_audio_play(I ptr,I frames,double delay,double pan){
 return MAIN_THREAD_EM_ASM_INT({
  const a=window.ninjaAudio;if(!a)return 0;
  const buffer=a.createBuffer(1,$1,48000);
  buffer.copyToChannel(HEAPF32.slice($0>>>2,($0>>>2)+$1),0);
  const source=a.createBufferSource();const p=a.createStereoPanner();source.buffer=buffer;p.pan.value=$3;
  source.connect(p).connect(window.ninjaGain);window.ninjaVoices.add(source);
  source.onended=()=>window.ninjaVoices.delete(source);source.start(a.currentTime+$2);return 1;
 },(int)ptr,(int)frames,delay,pan);}
void ninja_audio_stop(void){MAIN_THREAD_EM_ASM({for(const s of window.ninjaVoices)s.stop();});}
void ninja_audio_mute(I mute){MAIN_THREAD_EM_ASM({if(window.ninjaGain)window.ninjaGain.gain.value=$0?0:0.9;},(int)mute);}
I ninja_speech_ready(void){return MAIN_THREAD_EM_ASM_INT({return 'speechSynthesis' in window;});}
I ninja_speech(I ptr,I n,double rate,double pitch,double volume,I interrupt){
 return MAIN_THREAD_EM_ASM_INT({
 if(!window.speechSynthesis)return 0;
 const u=new SpeechSynthesisUtterance(UTF8ToString($0,$1));u.lang='ko-KR';u.rate=$2;u.pitch=$3;u.volume=$4;
 if($5)speechSynthesis.cancel();speechSynthesis.speak(u);return 1;
 },(int)ptr,(int)n,rate,pitch,volume,(int)interrupt);}
void ninja_speech_stop(void){MAIN_THREAD_EM_ASM({window.speechSynthesis?.cancel();});}
I ninja_result(I pixels,I len,I w,I h,I txt,I n,I save){
 return MAIN_THREAD_EM_ASM_INT({
 const c=document.createElement('canvas');c.width=$2;c.height=$3;const ctx=c.getContext('2d');const out=ctx.createImageData($2,$3);
 for(let i=0;i<$1;i+=4){out.data[i]=HEAPU8[$0+i+2];out.data[i+1]=HEAPU8[$0+i+1];out.data[i+2]=HEAPU8[$0+i];out.data[i+3]=255;}
 ctx.putImageData(out,0,0);
 const caption=UTF8ToString($4,$5);
 const download=()=>{const a=document.createElement('a');a.download='중급닌자시험-결과.png';a.href=c.toDataURL();a.click();};
 if($6){download();}else if(navigator.share){navigator.share({text:caption}).catch(err=>{if(err.name!=='AbortError')download();});}
 else if(navigator.clipboard){navigator.clipboard.writeText(caption).catch(download);}else{download();}return 1;
 },(int)pixels,(int)len,(int)w,(int)h,(int)txt,(int)n,(int)save);}
#include <string.h>
void (*__hmje_external_ui_start)(void);
#include <fcntl.h>
#include <stdio.h>
I hmje_resource_open(I ptr,I len){
 const char *s=(const char*)(uintptr_t)ptr;
 if(len<=6 || len>400 || memcmp(s,"fonts/",6) || memchr(s+6,'/',len-6))return -1;
 char path[420];
 snprintf(path,sizeof(path),"/bundle/%.*s",(int)len,s);
 return open(path,O_RDONLY);
}
#include <time.h>
extern int __real_clock_gettime(clockid_t,struct timespec *);
int __wrap_clock_gettime(clockid_t clock,struct timespec *out){
 return __real_clock_gettime(clock==6?CLOCK_MONOTONIC:clock,out);
}
