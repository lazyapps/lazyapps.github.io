# Shheep deployment artifacts

The game source, build tools, tests and native fixtures are maintained outside this public repository. This repository contains only the exported game wrapper (`src/components/ShheepGame.astro`), hashed obfuscated JavaScript and minified CSS (`public/shheep/game/`), and the runtime art/audio/font assets. The landing page remains editable here.

Do not edit the generated game wrapper or bundle. Build and test in the private web project, then run its export command against this checkout. The ordinary site build needs no access to private sources or obfuscation tools.

The exported JavaScript uses identifier renaming, encoded string tables, control-flow transformations and injected dead code, with no source maps or development handle. Obfuscation increases inspection cost; it cannot prevent extraction of browser code or art assets. No debugger traps or domain locks are used.

The game uses a stable 600-unit course and local browser records. Game Center rankings, challenges and invitations remain iOS-only.
