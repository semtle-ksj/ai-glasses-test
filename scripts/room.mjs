// Build-time extraction of the original classroom geometry. No JS ships in the native app.
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../../', import.meta.url);
let src=fs.readFileSync(new URL('중급닌자시험/js/classroom.js',root),'utf8');
const out=[];
const p=v=>`점3(x: ${v[0].toFixed(8)}, y: ${v[1].toFixed(8)}, z: ${v[2].toFixed(8)})`;
const col=v=>`색(0x${v.slice(1)})`;
const ctx={W:1280,H:720,Math,console}; vm.createContext(ctx);
vm.runInContext(src,ctx);
ctx.captureQuad=(g,pts,yaw,fill,stroke)=>out.push(`    면3([${pts.map(p).join(', ')}], yaw, ${col(fill)}, ${stroke?'참':'거짓'}, ${stroke?col(stroke):'색(0)'}).`);
ctx.captureLine=(g,a,b,yaw)=>out.push(`    선3(${p(a)}, ${p(b)}, yaw, 1.0, 알파색(0, 0.09)).`);
vm.runInContext('quad=captureQuad; line3=captureLine; boardText=()=>{}; drawRoom({},0);',ctx);
fs.writeFileSync(new URL('../Sources/Game/RoomGeometry.hmje',import.meta.url),'# Generated from original drawRoom; regenerate with node scripts/room.mjs.\n함수 교실벽은 (yaw: 실수)를 받아\n'+out.join('\n')+'\n');
