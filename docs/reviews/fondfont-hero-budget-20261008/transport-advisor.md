**Yes—implement the explicit gzip transport.** It is a reasonable adaptation to static hosting: substantial transfer savings, unchanged GLB bytes, and no dependency on configurable response headers. Keeping originals for browsers without `DecompressionStream` is sensible; avoid automatic raw retries that can double the download.

Before implementation, tighten these points:

- **Validate the final bytes.** Accept gzip or an already decoded GLB, then confirm the resulting payload is a GLB before parsing. Reject unexpected content explicitly.
- **Preserve cancellation through completion.** Aborting fetch does not guarantee later decompression or parsing stops. Guard against stale results after teardown, and dispose any parsed scene that can no longer be attached.
- **Measure temporary memory and startup time.** Decoded asset memory stays unchanged, but holding compressed and decompressed buffers can increase peak loading memory. Validate cold time to first rendered frame on a representative mobile device alongside transfer savings.
- **Gate WebP separately on rendered color equivalence.** Identical RGBA values alone do not prove identical appearance under color management. If metadata equivalence remains uncertain, ship the gzip improvement first and retain the PNGs.

Your proposed compressed-path, unsupported-browser, and already-decoded-response checks cover the important transport branches. The decisive acceptance condition is fewer transferred bytes **without a meaningful startup regression**, in addition to byte-exact GLB round trips.