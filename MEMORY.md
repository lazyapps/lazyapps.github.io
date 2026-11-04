# Project Memory

## Project Environment

- Astro 5 static website; not React Native or a native iOS/Android project.
- Package manager: npm (`npm ci --prefer-offline --no-audit`). A pnpm lockfile also exists.
- Development: `npm run dev` at `http://localhost:4321`.
- Build: `npm run build`; preview: `npm run preview`.
- No dedicated lint, unit-test, or end-to-end test command is configured.
- Browser QA can use Argent with a Chromium CDP target or a mobile browser in an iOS simulator.

Environment inspector result (2026-10-29):

```json
{"framework":"Astro 5 static website","is_react_native":false,"is_native_ios":false,"is_native_android":false,"package_manager":"npm","dev":"npm run dev -- --host 127.0.0.1","build":"npm run build","preview":"npm run preview","qa":["npm run check:seo","npm run check:presskit","Argent Chromium CDP"],"unit_test_command":null,"lint_command":null,"e2e_command":null}
```
