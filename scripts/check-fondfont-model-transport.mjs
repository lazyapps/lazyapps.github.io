import assert from 'node:assert/strict';
import { gzipSync } from 'node:zlib';
import { fetchModelBytes } from '../src/lib/fondfont/model-bytes.mjs';

const bytes = Buffer.alloc(24); bytes.write('glTF'); bytes.writeUInt32LE(2,4); bytes.writeUInt32LE(bytes.length,8);
const nativeFetch = globalThis.fetch, nativeDecompress = globalThis.DecompressionStream;
let calls=[];
const respond = (body, status=200) => { globalThis.fetch=async(url,options)=>{calls.push({url,signal:options.signal});return new Response(body,{status});}; };
try {
  respond(gzipSync(bytes));
  assert.deepEqual(Buffer.from(await fetchModelBytes('/model.glb')), bytes);
  assert.equal(calls.pop().url,'/model.glb.gz');
  respond(bytes); // HTTP Content-Encoding may already have been decoded by fetch.
  assert.deepEqual(Buffer.from(await fetchModelBytes('/model.glb')), bytes);
  globalThis.DecompressionStream=undefined;
  assert.deepEqual(Buffer.from(await fetchModelBytes('/model.glb')), bytes);
  assert.equal(calls.pop().url,'/model.glb');
  globalThis.DecompressionStream=nativeDecompress;
  calls=[];respond('missing',404);
  await assert.rejects(fetchModelBytes('/missing.glb'),/404/);assert.equal(calls.length,1,'never retry the full raw model');
  respond('<html>error</html>');await assert.rejects(fetchModelBytes('/bad.glb'),/Invalid GLB/);
  respond(gzipSync(bytes).subarray(0,12));await assert.rejects(fetchModelBytes('/truncated.glb'));
  const controller=new AbortController();controller.abort();respond(bytes);
  await assert.rejects(fetchModelBytes('/cancelled.glb',controller.signal),{name:'AbortError'});
  assert.equal(calls.at(-1).signal,controller.signal);
} finally { globalThis.fetch=nativeFetch;globalThis.DecompressionStream=nativeDecompress; }
console.log('Gzip, HTTP-decoded GLB, unsupported browser, corruption, cancellation and single-request failures passed.');
