const fs = require('fs');
const zlib = require('zlib');

async function nB(bytes) {
  return zlib.inflateSync(bytes);
}

async function kk(buf) {
  const e = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const n = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  const s = new Map();
  const a = e.getUint16(0);
  let l = 2;
  for (let c = 0; c < a; c++) {
    const d = e.getUint16(l);
    l += 2;
    const u = new TextDecoder().decode(n.subarray(l, l + d));
    l += d;
    const p = e.getUint32(l);
    l += 4;
    s.set(u, await nB(n.subarray(l, l + p)));
    l += p;
  }
  return s;
}

async function main() {
  const buf = fs.readFileSync('furni/f_sofa.nitro');
  const files = await kk(buf);
  console.log('Files in f_sofa.nitro:', [...files.keys()]);
  const jsonName = [...files.keys()].find(k => k.endsWith('.json'));
  if (jsonName) {
    const json = JSON.parse(new TextDecoder().decode(files.get(jsonName)));
    console.log('JSON type:', json.type);
    console.log('JSON assets:', Object.keys(json.assets || {}));
    console.log('JSON visualization:', json.visualization);
  }
}
main();
