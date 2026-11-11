// Liten QR-kode-generator (bytemodus, feilretting M, versjon 1–10). Lagd for Medlem.
(function(){
  const ECC=[10,16,26,18,24,16,18,22,22,26], BLK=[1,1,1,2,2,4,4,4,5,5];
  function mul(x,y){let z=0;for(let i=7;i>=0;i--){z=(z<<1)^((z>>>7)*0x11D);z^=((y>>>i)&1)*x;}return z&255;}
  function rsDiv(n){const r=new Array(n).fill(0);r[n-1]=1;let root=1;for(let i=0;i<n;i++){for(let j=0;j<n;j++){r[j]=mul(r[j],root);if(j+1<n)r[j]^=r[j+1];}root=mul(root,2);}return r;}
  function rsRem(data,div){const r=div.map(()=>0);for(const b of data){const f=b^r.shift();r.push(0);div.forEach((c,i)=>r[i]^=mul(c,f));}return r;}
  function rawModules(v){let r=(16*v+128)*v+64;if(v>=2){const n=Math.floor(v/7)+2;r-=(25*n-10)*n-55;if(v>=7)r-=36;}return r;}
  function dataCw(v){return Math.floor(rawModules(v)/8)-ECC[v-1]*BLK[v-1];}
  function alignPos(v){if(v===1)return[];const n=Math.floor(v/7)+2,size=v*4+17,step=Math.ceil((v*4+4)/(n*2-2))*2;const r=[6];for(let p=size-7;r.length<n;p-=step)r.splice(1,0,p);return r;}
  function encode(text){
    const bytes=Array.from(new TextEncoder().encode(text));
    let v=1;for(;v<=10;v++){const cap=dataCw(v)*8;const need=4+(v<10?8:16)+bytes.length*8;if(need<=cap)break;}
    if(v>10)throw new Error('for lang tekst');
    const size=v*4+17,cap=dataCw(v)*8;
    const bits=[];const put=(val,n)=>{for(let i=n-1;i>=0;i--)bits.push((val>>>i)&1);};
    put(4,4);put(bytes.length,v<10?8:16);bytes.forEach(b=>put(b,8));
    put(0,Math.min(4,cap-bits.length));while(bits.length%8)bits.push(0);
    for(let p=0xEC;bits.length<cap;p^=0xEC^0x11)put(p,8);
    const data=[];for(let i=0;i<bits.length;i+=8){let b=0;for(let j=0;j<8;j++)b=(b<<1)|bits[i+j];data.push(b);}
    // blokker + feilretting, flettet
    const nb=BLK[v-1],el=ECC[v-1],raw=Math.floor(rawModules(v)/8),nShort=nb-raw%nb,shortLen=Math.floor(raw/nb),div=rsDiv(el);
    const blocks=[];for(let i=0,k=0;i<nb;i++){const dat=data.slice(k,k+shortLen-el+(i<nShort?0:1));k+=dat.length;const ecc=rsRem(dat,div);if(i<nShort)dat.push(0);blocks.push(dat.concat(ecc));}
    const cw=[];for(let i=0;i<blocks[0].length;i++)for(let j=0;j<blocks.length;j++)if(i!==shortLen-el||j>=nShort)cw.push(blocks[j][i]);
    // matrise
    const M=[...Array(size)].map(()=>Array(size).fill(false)),F=[...Array(size)].map(()=>Array(size).fill(false));
    const set=(x,y,d)=>{M[y][x]=d;F[y][x]=true;};
    for(let i=0;i<size;i++){set(6,i,i%2===0);set(i,6,i%2===0);}
    const finder=(cx,cy)=>{for(let dy=-4;dy<=4;dy++)for(let dx=-4;dx<=4;dx++){const d=Math.max(Math.abs(dx),Math.abs(dy)),x=cx+dx,y=cy+dy;if(x>=0&&x<size&&y>=0&&y<size)set(x,y,d!==2&&d!==4);}};
    finder(3,3);finder(size-4,3);finder(3,size-4);
    const ap=alignPos(v);for(let i=0;i<ap.length;i++)for(let j=0;j<ap.length;j++){if((i===0&&j===0)||(i===0&&j===ap.length-1)||(i===ap.length-1&&j===0))continue;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)set(ap[i]+dx,ap[j]+dy,Math.max(Math.abs(dx),Math.abs(dy))!==1);}
    const fmt=(mask)=>{const d=(0<<3)|mask;let r=d;for(let i=0;i<10;i++)r=(r<<1)^((r>>>9)*0x537);const b=((d<<10)|r)^0x5412;const g=i=>((b>>>i)&1)===1;
      for(let i=0;i<=5;i++)set(8,i,g(i));set(8,7,g(6));set(8,8,g(7));set(7,8,g(8));for(let i=9;i<15;i++)set(14-i,8,g(i));
      for(let i=0;i<8;i++)set(size-1-i,8,g(i));for(let i=8;i<15;i++)set(8,size-15+i,g(i));set(8,size-8,true);};
    fmt(0);
    if(v>=7){let r=v;for(let i=0;i<12;i++)r=(r<<1)^((r>>>11)*0x1F25);const b=(v<<12)|r;for(let i=0;i<18;i++){const c=((b>>>i)&1)===1,a=size-11+i%3,bb=Math.floor(i/3);set(a,bb,c);set(bb,a,c);}}
    // data i sikksakk
    let bi=0;for(let right=size-1;right>=1;right-=2){if(right===6)right=5;for(let vert=0;vert<size;vert++)for(let j=0;j<2;j++){const x=right-j,up=((right+1)&2)===0,y=up?size-1-vert:vert;if(!F[y][x]&&bi<cw.length*8){M[y][x]=((cw[bi>>>3]>>>(7-(bi&7)))&1)===1;bi++;}}}
    const inv=(m,x,y)=>[(x+y)%2===0,y%2===0,x%3===0,(x+y)%3===0,(Math.floor(x/3)+Math.floor(y/2))%2===0,x*y%2+x*y%3===0,(x*y%2+x*y%3)%2===0,((x+y)%2+x*y%3)%2===0][m];
    const applyMask=m=>{for(let y=0;y<size;y++)for(let x=0;x<size;x++)if(!F[y][x]&&inv(m,x,y))M[y][x]=!M[y][x];};
    const penalty=()=>{let p=0;
      for(let y=0;y<size;y++){let run=1;for(let x=1;x<=size;x++){if(x<size&&M[y][x]===M[y][x-1])run++;else{if(run>=5)p+=run-2;run=1;}}}
      for(let x=0;x<size;x++){let run=1;for(let y=1;y<=size;y++){if(y<size&&M[y][x]===M[y-1][x])run++;else{if(run>=5)p+=run-2;run=1;}}}
      for(let y=0;y<size-1;y++)for(let x=0;x<size-1;x++){const c=M[y][x];if(c===M[y][x+1]&&c===M[y+1][x]&&c===M[y+1][x+1])p+=3;}
      let dark=0;for(const r of M)for(const c of r)if(c)dark++;p+=Math.floor(Math.abs(dark*20-size*size*10)/(size*size))*10;return p;};
    let best=0,bestP=Infinity;for(let m=0;m<8;m++){applyMask(m);fmt(m);const p=penalty();if(p<bestP){bestP=p;best=m;}applyMask(m);}
    applyMask(best);fmt(best);
    return M;
  }
  window.qrDraw=function(canvas,text,px){const M=encode(text),n=M.length,q=4,s=px||6;canvas.width=canvas.height=(n+q*2)*s;const g=canvas.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,canvas.width,canvas.height);g.fillStyle='#000';for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(M[y][x])g.fillRect((x+q)*s,(y+q)*s,s,s);return n;};
})();
