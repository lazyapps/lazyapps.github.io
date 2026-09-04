# Project Memory

## Project Environment

- Astro 5 static website; not React Native or a native iOS/Android project.
- Package manager: npm (`npm ci --prefer-offline --no-audit`). A pnpm lockfile also exists.
- Development: `npm run dev` at `http://localhost:4321`.
- Build: `npm run build`; preview: `npm run preview`.
- No dedicated lint, unit-test, or end-to-end test command is configured.
- Browser QA can use Argent with a Chromium CDP target or a mobile browser in an iOS simulator.
