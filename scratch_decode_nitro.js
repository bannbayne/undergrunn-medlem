const fs = require('fs');

// Let's decode furni/f_sofa.nitro and see what Habbo furniture asset it is!
const buf = fs.readFileSync('furni/f_sofa.nitro');
console.log('f_sofa size:', buf.length);

// In nitro: first 4 bytes is length of json or binary format
// Nitro is a zip/uncompressed or binary format:
// Usually a Nitro archive is: [file1_name_len, file1_name, file1_len, file1_bytes, ...]
// Or gzip/zlib compressed.
const zlib = require('zlib');
try {
  const decompressed = zlib.inflateSync(buf);
  console.log('Decompressed with inflate:', decompressed.length);
  console.log('First 200 chars:', decompressed.slice(0, 200).toString('utf8'));
} catch (e) {
  console.log('Not simple inflate:', e.message);
}
