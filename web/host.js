var hmjeWeb={};
if(typeof window!=='undefined'){
 const canvas=document.querySelector('canvas'), ctx=canvas.getContext('bitmaprenderer');
 window.Worker=class extends Worker{constructor(...args){super(...args);this.addEventListener('message',e=>{
 const img=e.data?.hmjeFrame;if(!img)return;
 if(canvas.width!==img.width||canvas.height!==img.height){canvas.width=img.width;canvas.height=img.height;}
 ctx.transferFromImageBitmap(img);document.querySelector('output').hidden=true;
 });}};
 hmjeWeb.firstFrame=()=>{};hmjeWeb.textInput=()=>{};
 function resize(){hmjeWeb.surface={width:innerWidth,height:innerHeight,scale:1,theme:1,top:0,bottom:0,left:0,right:0};
 Module._hmje_web_surface?.(innerWidth,innerHeight,1,0,0,0,0);}
 resize();addEventListener('resize',resize);
 window.ninjaVoices=new Set();
 canvas.addEventListener('pointerdown',()=>{if(!window.ninjaAudio){window.ninjaAudio=new AudioContext();window.ninjaGain=ninjaAudio.createGain();ninjaGain.connect(ninjaAudio.destination);}ninjaAudio.resume();});
 for(const [type,phase] of Object.entries({pointerdown:1,pointermove:2,pointerup:3,pointercancel:4})){
 canvas.addEventListener(type,e=>{if(type==='pointerdown')canvas.setPointerCapture(e.pointerId);
 Module._hmje_web_pointer?.(phase,e.pointerId,e.clientX,e.clientY,e.pointerType==='touch'?2:3,e.buttons,e.button>=0?e.button+1:0,performance.now()*1000,0,0);e.preventDefault();});}
 const scans={KeyA:30,KeyW:17,KeyD:32,KeyS:31,KeyQ:16,KeyE:18,KeyM:50};
 for(const type of ['keydown','keyup'])addEventListener(type,e=>{if(scans[e.code]&&!e.metaKey&&!e.ctrlKey){Module._hmje_web_key?.(scans[e.code],type==='keydown'?1:0);e.preventDefault();}});
}
