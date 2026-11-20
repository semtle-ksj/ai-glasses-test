/* Device boundary only. HMJE synthesizes all game audio; callback owns copied PCM. */
#define MINIAUDIO_IMPLEMENTATION
#define MA_NO_DECODING
#define MA_NO_ENCODING
#define MA_NO_RESOURCE_MANAGER
#define MA_NO_NODE_GRAPH
#define MA_NO_ENGINE
#include "vendor/miniaudio.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define VOICES 128
static ma_device device;
static ma_mutex lock;
static int ready, muted;
static struct voice { float *pcm; uint64_t len, pos, delay; float left, right; } voices[VOICES];
static void output(ma_device *d, void *out, const void *in, ma_uint32 count) {
    (void)d; (void)in; float *dst=out;
    memset(dst,0,(size_t)count*2*sizeof(float));
    ma_mutex_lock(&lock);
    for(int v=0;v<VOICES;v++) if(voices[v].pcm) {
        struct voice *s=&voices[v];
        for(ma_uint32 f=0;f<count;f++) {
            if(s->delay) { s->delay--; continue; }
            if(s->pos==s->len) break;
            float x=s->pcm[s->pos++];
            if(!muted) { dst[f*2]+=x*s->left*.9f; dst[f*2+1]+=x*s->right*.9f; }
        }
        if(s->pos==s->len) { free(s->pcm); memset(s,0,sizeof(*s)); }
    }
    ma_mutex_unlock(&lock);
}
int64_t ninja_audio_open(void) {
    if(ready) return 1;
    if(ma_mutex_init(&lock)!=MA_SUCCESS) return 0;
    ma_device_config c=ma_device_config_init(ma_device_type_playback);
    c.playback.format=ma_format_f32; c.playback.channels=2; c.sampleRate=48000; c.dataCallback=output;
    if(ma_device_init(NULL,&c,&device)!=MA_SUCCESS) { ma_mutex_uninit(&lock); return 0; }
    if(ma_device_start(&device)!=MA_SUCCESS) { ma_device_uninit(&device); ma_mutex_uninit(&lock); return 0; }
    ready=1; return 1;
}
int64_t ninja_audio_play(const float *data,uint64_t frames,double delay,double pan) {
    if(!ready || !data || !frames || frames>480000) return 0;
    float *copy=malloc((size_t)frames*sizeof(float)); if(!copy) return 0;
    memcpy(copy,data,(size_t)frames*sizeof(float));
    ma_mutex_lock(&lock);
    for(int v=0;v<VOICES;v++) if(!voices[v].pcm) {
        pan=fmax(-1,fmin(1,pan));
        voices[v]=(struct voice){copy,frames,0,(uint64_t)(fmax(0,delay)*48000),cosf((float)((pan+1)*MA_PI/4)),sinf((float)((pan+1)*MA_PI/4))};
        ma_mutex_unlock(&lock); return 1;
    }
    ma_mutex_unlock(&lock); free(copy); return 0;
}
void ninja_audio_mute(int64_t value) { if(!ready) return; ma_mutex_lock(&lock); muted=value!=0; ma_mutex_unlock(&lock); }
void ninja_audio_stop(void) {
    if(!ready) return;
    ma_mutex_lock(&lock);
    for(int i=0;i<VOICES;i++) { free(voices[i].pcm); memset(&voices[i],0,sizeof(voices[i])); }
    ma_mutex_unlock(&lock);
}
