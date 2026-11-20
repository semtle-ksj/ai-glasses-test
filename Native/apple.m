#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <ImageIO/ImageIO.h>
#import <UniformTypeIdentifiers/UniformTypeIdentifiers.h>
#import <TargetConditionals.h>
#if TARGET_OS_IPHONE
#import <UIKit/UIKit.h>
#else
#import <AppKit/AppKit.h>
#endif
#include <stdint.h>
#if !TARGET_OS_IPHONE
#import <objc/runtime.h>
static id ninja_no_text_context(id object, SEL selector) { return nil; }
#endif
static AVSpeechSynthesizer *speaker;
static AVSpeechSynthesisVoice *voice;
int64_t ninja_speech_ready(void) {
    if(!speaker) speaker=[AVSpeechSynthesizer new];
    if(!voice) {
        voice=[AVSpeechSynthesisVoice voiceWithLanguage:@"ko-KR"];
#if !__has_feature(objc_arc)
        [voice retain];
#endif
    }
    return voice!=nil;
}
int64_t ninja_speech(const uint8_t *bytes,uint64_t len,double rate,double pitch,double volume,int64_t interrupt) {
    if(!ninja_speech_ready() || !bytes || len>16384) return 0;
    NSString *text=[[NSString alloc] initWithBytes:bytes length:(NSUInteger)len encoding:NSUTF8StringEncoding];
    if(!text) return 0;
    dispatch_async(dispatch_get_main_queue(), ^{
        if(interrupt) [speaker stopSpeakingAtBoundary:AVSpeechBoundaryImmediate];
        AVSpeechUtterance *u=[AVSpeechUtterance speechUtteranceWithString:text];
        u.voice=voice; u.rate=AVSpeechUtteranceDefaultSpeechRate*rate; u.pitchMultiplier=pitch; u.volume=volume;
        [speaker speakUtterance:u];
    });
    return 1;
}
void ninja_speech_stop(void) { dispatch_async(dispatch_get_main_queue(), ^{ [speaker stopSpeakingAtBoundary:AVSpeechBoundaryImmediate]; }); }
#if TARGET_OS_IPHONE
static UIViewController *controller(void) {
    for(UIWindowScene *scene in UIApplication.sharedApplication.connectedScenes) if([scene isKindOfClass:UIWindowScene.class])
        for(UIWindow *w in scene.windows) if(w.isKeyWindow) { UIViewController *v=w.rootViewController; while(v.presentedViewController) v=v.presentedViewController; return v; }
    return nil;
}
#endif
int64_t ninja_result(const uint8_t *pixels,uint64_t length,int64_t width,int64_t height,const uint8_t *text,uint64_t textLength,int64_t save) {
    if(!pixels || width<=0 || height<=0 || width>4096 || height>4096 || length!=(uint64_t)width*height*4) return 0;
    NSData *data=[NSData dataWithBytes:pixels length:(NSUInteger)length];
    CGDataProviderRef provider=CGDataProviderCreateWithCFData((__bridge CFDataRef)data);
    CGColorSpaceRef space=CGColorSpaceCreateDeviceRGB();
    CGImageRef image=CGImageCreate(width,height,8,32,width*4,space,kCGBitmapByteOrder32Little|kCGImageAlphaNoneSkipFirst,provider,NULL,false,kCGRenderingIntentDefault);
    CGColorSpaceRelease(space); CGDataProviderRelease(provider);
    if(!image) return 0;
    NSMutableData *png=[NSMutableData data];
    CGImageDestinationRef dest=CGImageDestinationCreateWithData((__bridge CFMutableDataRef)png,(__bridge CFStringRef)UTTypePNG.identifier,1,NULL);
    if(!dest) { CGImageRelease(image); return 0; }
    CGImageDestinationAddImage(dest,image,NULL); BOOL encoded=CGImageDestinationFinalize(dest); CFRelease(dest); CGImageRelease(image);
    if(!encoded) return 0;
    NSString *caption=[[NSString alloc] initWithBytes:text length:(NSUInteger)textLength encoding:NSUTF8StringEncoding] ?: @"";
    dispatch_async(dispatch_get_main_queue(), ^{
#if TARGET_OS_IPHONE
        NSURL *url=[NSURL fileURLWithPath:[NSTemporaryDirectory() stringByAppendingPathComponent:@"중급닌자시험-결과.png"]];
        [png writeToURL:url atomically:YES];
        UIViewController *root=controller(); if(!root) return;
        if(save) {
            UIDocumentPickerViewController *picker=[[UIDocumentPickerViewController alloc] initForExportingURLs:@[url] asCopy:YES];
            [root presentViewController:picker animated:YES completion:nil];
        } else {
            UIActivityViewController *share=[[UIActivityViewController alloc] initWithActivityItems:@[caption,url] applicationActivities:nil];
            share.popoverPresentationController.sourceView=root.view;
            share.popoverPresentationController.sourceRect=CGRectMake(CGRectGetMidX(root.view.bounds),CGRectGetMidY(root.view.bounds),1,1);
            [root presentViewController:share animated:YES completion:nil];
        }
#else
        if(save) {
            NSSavePanel *panel=[NSSavePanel savePanel]; panel.allowedContentTypes=@[UTTypePNG]; panel.nameFieldStringValue=@"중급닌자시험-결과.png";
            [panel beginWithCompletionHandler:^(NSModalResponse result){ if(result==NSModalResponseOK) [png writeToURL:panel.URL atomically:YES]; }];
        } else {
            NSPasteboard *pb=NSPasteboard.generalPasteboard; [pb clearContents]; [pb setString:caption forType:NSPasteboardTypeString];
        }
#endif
    });
    return 1;
}
int64_t ninja_is_touch(void) {
#if TARGET_OS_IPHONE
    return 1;
#else
    return 0;
#endif
}
void ninja_configure_window(void) {
#if !TARGET_OS_IPHONE
    dispatch_async(dispatch_get_main_queue(), ^{
        // This canvas game has no editable fields: leave physical key events
        // with HmjeUI instead of handing them to the Korean composition engine.
        Class input=NSClassFromString(@"HmjeTextInputView");
        if(input) class_addMethod(input,@selector(inputContext),(IMP)ninja_no_text_context,"@@:");
        NSWindow *w=NSApp.mainWindow ?: NSApp.windows.firstObject; if(!w)return;
        CGFloat width=MIN(1280.0,NSApp.mainWindow.screen.visibleFrame.size.width-80.0);
        if(width<800)width=800;
        w.contentMinSize=NSMakeSize(800,450); [w setContentSize:NSMakeSize(width,width*9/16)]; [w center];
    });
#endif
}
