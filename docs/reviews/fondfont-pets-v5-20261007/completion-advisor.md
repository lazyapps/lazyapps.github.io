No remaining critical tail-transform flaw is evident in the described implementation.

Premultiplying is correct because the world-up axis is converted into the bone’s parent space. Refreshing transforms base → mid → tip ensures each child uses its already-modified parent rotation. Restoring and caching unmodified animation quaternions before applying offsets prevents accumulated rotation drift.

The measured .252 m lateral versus .00293 m vertical tip travel, with no body spin, supports the intended behavior.

One assumption remains unspecified: nonuniform scale or shear in the tail’s ancestry. Inverse world rotation alone cannot compensate for those transforms. If ancestor scales are applied or uniform, approve the tail transform implementation; no further transform redesign is warranted.