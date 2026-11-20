#include <jni.h>
#include <stdint.h>
#include <string.h>
extern JavaVM *hmje_android_java_vm(void);
extern jobject hmje_android_current_activity(JNIEnv *);
struct bridge{JavaVM *vm;JNIEnv *e;jclass cls;jobject activity;int attached;};
static void end(struct bridge *b){if(b->e){if((*b->e)->ExceptionCheck(b->e))(*b->e)->ExceptionClear(b->e);(*b->e)->PopLocalFrame(b->e,NULL);}if(b->attached)(*b->vm)->DetachCurrentThread(b->vm);}
static int begin(struct bridge *b){
    memset(b,0,sizeof(*b));b->vm=hmje_android_java_vm();if(!b->vm)return 0;
    jint r=(*b->vm)->GetEnv(b->vm,(void**)&b->e,JNI_VERSION_1_6);
    if(r==JNI_EDETACHED){if((*b->vm)->AttachCurrentThread(b->vm,&b->e,NULL)!=JNI_OK){b->e=NULL;return 0;}b->attached=1;}else if(r!=JNI_OK){b->e=NULL;return 0;}
    JNIEnv *e=b->e;if((*e)->PushLocalFrame(e,24)!=JNI_OK){b->e=NULL;return 0;}
    b->activity=hmje_android_current_activity(e);if(!b->activity)return 0;
    jclass ac=(*e)->GetObjectClass(e,b->activity);jmethodID get=(*e)->GetMethodID(e,ac,"getClassLoader","()Ljava/lang/ClassLoader;");
    jobject loader=get?(*e)->CallObjectMethod(e,b->activity,get):NULL;if(!loader)return 0;
    jclass lc=(*e)->GetObjectClass(e,loader);jmethodID load=(*e)->GetMethodID(e,lc,"loadClass","(Ljava/lang/String;)Ljava/lang/Class;");
    jstring name=(*e)->NewStringUTF(e,"net.semtle.ninja.NinjaPlatform");b->cls=load?(*e)->CallObjectMethod(e,loader,load,name):NULL;
    return b->cls&&!(*e)->ExceptionCheck(e);
}
static jbyteArray bytes(JNIEnv *e,const uint8_t *p,uint64_t n){if(!p||n>16777216)return NULL;jbyteArray a=(*e)->NewByteArray(e,(jsize)n);if(a)(*e)->SetByteArrayRegion(e,a,0,(jsize)n,(const jbyte*)p);return a;}
int64_t ninja_speech_ready(void){struct bridge b;int64_t out=0;if(begin(&b)){JNIEnv *e=b.e;jmethodID m=(*e)->GetStaticMethodID(e,b.cls,"ready","(Landroid/app/Activity;)I");if(m)out=(*e)->CallStaticIntMethod(e,b.cls,m,b.activity);}end(&b);return out;}
int64_t ninja_speech(const uint8_t *p,uint64_t n,double rate,double pitch,double volume,int64_t interrupt){
    struct bridge b;int64_t out=0;if(begin(&b)){JNIEnv *e=b.e;jmethodID m=(*e)->GetStaticMethodID(e,b.cls,"speak","(Landroid/app/Activity;[BFFFZ)I");jbyteArray a=bytes(e,p,n);if(m&&a)out=(*e)->CallStaticIntMethod(e,b.cls,m,b.activity,a,(jfloat)rate,(jfloat)pitch,(jfloat)volume,(jboolean)interrupt);}end(&b);return out;
}
void ninja_speech_stop(void){struct bridge b;if(begin(&b)){JNIEnv *e=b.e;jmethodID m=(*e)->GetStaticMethodID(e,b.cls,"stop","(Landroid/app/Activity;)V");if(m)(*e)->CallStaticVoidMethod(e,b.cls,m,b.activity);}end(&b);}
int64_t ninja_result(const uint8_t *p,uint64_t n,int64_t w,int64_t h,const uint8_t *t,uint64_t tn,int64_t save){
    struct bridge b;int64_t out=0;if(begin(&b)){JNIEnv *e=b.e;jmethodID m=(*e)->GetStaticMethodID(e,b.cls,"result","(Landroid/app/Activity;[BII[BZ)I");jbyteArray a=bytes(e,p,n),text=bytes(e,t,tn);if(m&&a&&text)out=(*e)->CallStaticIntMethod(e,b.cls,m,b.activity,a,(jint)w,(jint)h,text,(jboolean)save);}end(&b);return out;
}
int64_t ninja_is_touch(void){return 1;}
void ninja_configure_window(void){struct bridge b;if(begin(&b)){JNIEnv *e=b.e;jmethodID m=(*e)->GetStaticMethodID(e,b.cls,"configure","(Landroid/app/Activity;)V");if(m)(*e)->CallStaticVoidMethod(e,b.cls,m,b.activity);}end(&b);}
