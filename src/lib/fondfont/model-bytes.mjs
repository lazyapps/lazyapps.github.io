/** Static hosting cannot guarantee HTTP compression for GLB files. */
export async function fetchModelBytes(url, signal) {
  const compressed = typeof DecompressionStream === 'function';
  const response = await fetch(compressed ? `${url}.gz` : url, { signal });
  if (!response.ok) throw new Error(`Model download failed: ${response.status} ${response.url}`);
  let bytes = await response.arrayBuffer();
  const header = new Uint8Array(bytes);
  // A host may already have decoded Content-Encoding: gzip in fetch().
  if (header[0] === 0x1f && header[1] === 0x8b) {
    bytes = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  }
  signal?.throwIfAborted();
  const view = new DataView(bytes);
  if (bytes.byteLength < 20 || view.getUint32(0, true) !== 0x46546c67
    || view.getUint32(4, true) !== 2 || view.getUint32(8, true) !== bytes.byteLength) {
    throw new Error(`Invalid GLB payload: ${url}`);
  }
  return bytes;
}
