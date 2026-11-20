// Browser adapter for compositing and caching HMJE-rasterized surfaces.
addToLibrary({
  // Unused native framebuffer and event hooks referenced by the shared platform shim.
  hmje_posix_input_poll2:()=>0n,
  hmje_posix_input_poll:()=>0n,
  hmje_posix_framebuffer_present:()=>0n,
  hmje_posix_framebuffer_blit:()=>0n,
  hmje_posix_framebuffer_info:()=>0n,
  hmje_posix_gpu_command:()=>0n,

  spritepixels:(p,w,h)=>Ninja.upload(Number(p),Number(w),Number(h)),
  spritebaseline:(base,advance)=>{Ninja.pending.baseline=base;Ninja.pending.advance=advance;},
  spritetext:(ptr,n,x,y,size,rasterSize,weight,align,col)=>{
    const key='t'+weight+'-'+rasterSize+'/'+(Number(col)>>>8)+'/'+UTF8ToString(Number(ptr),Number(n));
    const p={key,text:true,x,y,size,rasterSize,align:Number(align),alpha:(Number(col)&255)/255};
    const sprite=Ninja.sprites.get(key);
    if(sprite){Ninja.sprites.delete(key);Ninja.sprites.set(key,sprite);Ninja.paintText(sprite,p);return 1n;}
    Ninja.pending=p;return 0n;
  },
  webrect:(x,y,w,h,r,col,line)=>{
    if(w<=0||h<=0)return;
    const k=Ninja.density(),sw=r||line?Math.max(1,Math.round(w*k)):1,sh=r||line?Math.max(1,Math.round(h*k)):1;
    const radius=Math.round(r*k),lw=line?Math.max(1,Math.round(line*k)):0;
    Ninja.shape(1,['r',sw,sh,radius,lw].join(','),col,[x,y,w,h],sw,sh,[0,0,0,0,radius,lw]);
  },
  webline:(x,y,a,b,line,col)=>{
    const box=Ninja.bounds(Math.min(x,a),Math.min(y,b),Math.max(x,a),Math.max(y,b),line+1);
    if(!box)return;
    const k=Ninja.density(),w=Math.ceil(box[2]*k),h=Math.ceil(box[3]*k);
    const args=[(x-box[0])*k,(y-box[1])*k,(a-box[0])*k,(b-box[1])*k,0,Math.max(1,line*k)].map(Math.round);
    Ninja.shape(2,['l',w,h,...args].join(','),col,box,w,h,args);
  },
  webpoly:(ptr,count,s,x,y,fill,line,col)=>{
    const base=Number(ptr)/8,n=Number(count),points=HEAPF64;
    let l=Infinity,t=Infinity,r=-Infinity,b=-Infinity;
    for(let i=0;i<n;i++){
      const px=points[base+2*i]*s+x,py=points[base+2*i+1]*s+y;
      l=Math.min(l,px);t=Math.min(t,py);r=Math.max(r,px);b=Math.max(b,py);
    }
    const box=Ninja.bounds(l,t,r,b,fill?1:line+1);if(!box)return;
    const k=Ninja.density(),w=Math.ceil(box[2]*k),h=Math.ceil(box[3]*k),lw=fill?0:Math.max(1,Math.round(line*k));
    const ox=(x-box[0])*k,oy=(y-box[1])*k,f=s*k;
    const key=['p',w,h,lw];
    for(let i=0;i<n;i++)key.push(Math.round(points[base+2*i]*f+ox),Math.round(points[base+2*i+1]*f+oy));
    Ninja.shape(3,key.join(','),col,box,w,h,[0,0,0,0,0,lw,ptr,count,f,ox,oy]);
  },
  webellipse:(x,y,rx,ry,rot,fill,line,col)=>{
    if(rx<=0||ry<=0)return;
    const k=Ninja.density(),a=Math.max(1,Math.round(rx*k)),b=Math.max(1,Math.round(ry*k)),lw=fill?0:Math.max(1,Math.round(line*k));
    const pad=1+Math.ceil(lw/2),w=2*(a+pad),h=2*(b+pad);
    const g=Ninja.g;g.save();g.translate(x,y);g.rotate(rot);
    Ninja.shape(4,['e',a,b,lw].join(','),col,[-w/(2*k),-h/(2*k),w/k,h/k],w,h,[a+pad,b+pad,a,b,0,lw]);
    g.restore();
  },
  webtarget:(w,h)=>{const c=document.createElement('canvas'),d=Ninja.cacheScale;c.width=Number(w)*d;c.height=Number(h)*d;
    const id=++Ninja.id;Ninja.images.set(id,c);Ninja.stack.push(Ninja.g);Ninja.g=c.getContext('2d');Ninja.g.scale(d,d);return BigInt(id);},
  webrestore:()=>{Ninja.g=Ninja.stack.pop();},
  webdrop:id=>{Ninja.images.delete(Number(id));},
  webimage:(id,x,y,w,h)=>Ninja.g.drawImage(Ninja.images.get(Number(id)),x,y,w,h),
  webwood:()=>Ninja.shape(5,'wood',0xffffffffn,[0,0,1280,720],320,180,[]),
  webtransform:(a,b,c,d,x,y)=>{Ninja.g.save();Ninja.g.transform(a,b,c,d,x,y);},
  webend:()=>Ninja.g.restore(),
  webblur:r=>{Ninja.g.filter=r>.05?'blur('+r+'px)':'none';},
  webcardart:(x,y,w,h)=>window.examShare.drawArt(Ninja.g,x,y,w,h)?1n:0n,
  webshare:(id,ptr,n,save)=>{
    window.examShare.open(Ninja.images.get(Number(id)),UTF8ToString(Number(ptr),Number(n)),Boolean(save));
    return 1n;
  }
});
