# Global select spacing · 2026-10-10

- Shared site.css geometry for Press Kit, KeyHop gesture controls, Shheep toolbar and future .select-control wrappers: 12px current-color masked chevron, 16px inset at the logical inline end, 12px gap before text, 40px text reservation. Disable the native field arrow; retain the native select and keyboard/menu behavior. Pointer events pass through the decorative arrow; disabled fields fade it. RTL puts the reserved space and arrow on the corresponding inline end.
- Press Kit uses the shared end padding; preserve its existing field size, fill, rounded corners and focus outline.
- KeyHop removes duplicate SVG arrows and the extra grid column, uses shared geometry, increases desktop minimum height from 36px to 40px, preserves 48px mobile fields.
- Header LanguagePicker has 16px end padding, 48px minimum width and end alignment so the transparent native hit area fits even the short Chinese/Japanese labels. Its existing custom visual presentation remains.
- Shheep styling is an outer website override. Generated game wrapper, hashed CSS and JS were not modified. Arrow inherits the game's light text color against its dark toolbar.

Final npm run build and git diff --check pass. Build includes all SEO and Press Kit checks. responsive.json covers four representative dropdown contexts (Press Kit, KeyHop English/Arabic, Shheep) at 320/768/1280px; all arrows measure 16px inset and 12px width, fields reserve 40px, hit areas are at least 40px, and no page/header overflow occurs. headers.json covers all 60 landing routes at 320px: no page, header or control overflow; header arrow inset 16px and hit width at least 48px.

Interactions: Press Kit switched to French and exposed the matching French README; KeyHop Command/AZERTY selection updated leader glyphs and keyboard keys; Shheep German selection updated sound text, instructions and game-start copy. Keyboard focus remains a 2px orange outline on the Press Kit field. select.png shows the corrected focused control. Browser viewport reset after capture.
