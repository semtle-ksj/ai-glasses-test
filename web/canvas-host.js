const screenCanvas=document.querySelector('canvas');
const Ninja={
  g:screenCanvas.getContext('2d',{alpha:false}), images:new Map(), stack:[], id:0, cacheScale:2,
  sprites:new Map(), bytes:0, pending:null,
  density(){const m=this.g.getTransform();return Math.min(4,Math.max(1,Math.hypot(m.a,m.b)));},
  paint(sprite,placement){
    const g=this.g;
    g.globalAlpha=placement.alpha;
    g.drawImage(sprite.canvas,...placement.dest);
    g.globalAlpha=1;
  },
  cached(key,placement,bake){
    let sprite=this.sprites.get(key);
    if(sprite){
      this.sprites.delete(key);this.sprites.set(key,sprite);
      this.paint(sprite,placement);return;
    }
    this.pending={key,placement};
    bake();
  },
  upload(ptr,w,h){
    const p=this.pending;
    const data=new ImageData(w,h),dest=new Uint32Array(data.data.buffer);
    const src=new Uint32Array(HEAPU8.buffer,ptr,w*h);
    for(let i=0;i<src.length;i++){
      const v=src[i],alpha=v>>>24;
      if(alpha===255)dest[i]=0xff000000|((v&255)<<16)|(v&65280)|((v>>>16)&255);
      else if(alpha){const k=255/alpha;
        dest[i]=alpha<<24|Math.min(255,Math.round((v&255)*k))<<16|Math.min(255,Math.round(((v>>>8)&255)*k))<<8|Math.min(255,Math.round(((v>>>16)&255)*k));}
    }
    const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
    canvas.getContext('2d').putImageData(data,0,0);
    const sprite={canvas,baseline:p.baseline,advance:p.advance};
    this.sprites.set(p.key,sprite);this.bytes+=w*h*4;
    while(this.bytes>96*1024*1024 && this.sprites.size>1){
      const [key,old]=this.sprites.entries().next().value;
      this.bytes-=old.canvas.width*old.canvas.height*4;
      this.sprites.delete(key);old.canvas.width=0;
    }
    this.pending=null;
    if(p.text)this.paintText(sprite,p);
    else this.paint(sprite,p.placement);
  },
  paintText(sprite,p){
    const k=p.size/p.rasterSize;
    const x=p.x-(p.align===1?0.5:p.align===2?1:0)*sprite.advance*k;
    this.paint(sprite,{alpha:p.alpha,dest:[x,p.y-sprite.baseline*k,sprite.canvas.width*k,sprite.canvas.height*k]});
  },
  shape(kind,key,col,dest,w,h,args){
    if(!w||!h||w*h>12000000)return;
    this.cached(key+','+(Number(col)>>>8),{alpha:(Number(col)&255)/255,dest},()=>{
      const [a=0,b=0,c=0,d=0,r=0,line=0,ptr=0n,n=0n,f=1,ox=0,oy=0]=args;
      Module._game_bake(BigInt(kind),BigInt(w),BigInt(h),a,b,c,d,r,line,col,ptr,n,f,ox,oy);
    });
  },
  bounds(x,y,x2,y2,pad){
    const g=this.g,m=g.getTransform().inverse();
    const points=[[0,0],[g.canvas.width,0],[0,g.canvas.height],[g.canvas.width,g.canvas.height]];
    const xs=points.map(([u,v])=>m.a*u+m.c*v+m.e),ys=points.map(([u,v])=>m.b*u+m.d*v+m.f);
    const l=Math.floor(Math.max(x-pad,Math.min(...xs)-2)),t=Math.floor(Math.max(y-pad,Math.min(...ys)-2));
    const r=Math.ceil(Math.min(x2+pad,Math.max(...xs)+2)),b=Math.ceil(Math.min(y2+pad,Math.max(...ys)+2));
    if(r>l&&b>t)return [l,t,r-l,b-t];
  }
};
window.ninjaVoices=new Set();
Module.onRuntimeInitialized=async()=>{

  Module._hmje_app_main();Module._game_init();
  let last=0;
  document.addEventListener('visibilitychange',()=>{last=0;});
  function frame(now){
    const w=screenCanvas.clientWidth,h=screenCanvas.clientHeight;
    const d=Math.min(devicePixelRatio||1,3,Math.sqrt(4200000/(w*h)));
    const pw=Math.max(1,Math.round(w*d)),ph=Math.max(1,Math.round(h*d));
    if(screenCanvas.width!==pw||screenCanvas.height!==ph){screenCanvas.width=pw;screenCanvas.height=ph;}
    Ninja.g.setTransform(pw/w,0,0,ph/h,0,0);
    Module._game_frame(document.hidden?0:(now-(last||now))/1000,BigInt(w),BigInt(h));last=now;
    document.querySelector('output').hidden=true;
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  screenCanvas.addEventListener('contextmenu',e=>e.preventDefault());
  const phase={pointerdown:1,pointermove:2,pointerup:3,pointercancel:4,lostpointercapture:4};
  for(const type of Object.keys(phase))screenCanvas.addEventListener(type,e=>{
    if(type==='pointerdown'){
      screenCanvas.setPointerCapture(e.pointerId);
      if(!window.ninjaAudio){window.ninjaAudio=new AudioContext();window.ninjaGain=ninjaAudio.createGain();ninjaGain.connect(ninjaAudio.destination);}
      ninjaAudio.resume();
    }
    const r=screenCanvas.getBoundingClientRect();
    Module._game_pointer(e.clientX-r.left,e.clientY-r.top,BigInt(e.pointerId),BigInt(phase[type]),e.pointerType==='touch'?2n:3n);
    e.preventDefault();
  });
  addEventListener('keydown',e=>{if(!e.metaKey&&!e.ctrlKey&&/^Key[AWDSQEM]$/.test(e.code)){Module._game_key(BigInt(e.code.charCodeAt(3)));e.preventDefault();}});
};
