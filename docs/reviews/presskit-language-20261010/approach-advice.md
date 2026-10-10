Yes. Presentation language and downloadable material language must be separate to preserve KeyHop’s ar/ru/hi entry language and carry selections through the hub and English-only products.

Simplify the proposal: **use the same 17-language presentation picker on every Press Kit page**. Product-specific unions plus exceptions for incoming languages create unnecessary state: the current language can otherwise be valid but absent from the picker.

Keep one selected language and derive the rest:

```text
presentationLanguage = resolved glossary language
materialLanguage = app supports presentationLanguage ? presentationLanguage : en
```

Resolve product copy separately from existing marketing translations and App-only translations. Use explicitly marked English fallback where neither exists.

Concrete blockers to address:

- **Keep presentation locales outside the download catalog.** [presskit-catalog.mjs](/Users/realazy/Projects/Sites/lazyapps/src/content/presskit-catalog.mjs) currently builds copy and assets together from App-supported tags. Expanding `kit.locales` to marketing languages would risk invented download folders and unsupported asset lookups. Add a separate presentation lookup. English fallback must not weaken the existing requirement for translated README content in actual App-supported languages.
- **Language hashes currently target real elements.** [presskit.astro](/Users/realazy/Projects/Sites/lazyapps/src/pages/[product]/presskit.astro) assigns `id="language-…"` to panels, allowing native fragment scrolling on arrival. Give panels different IDs; interpret `#language-…` as state. A subsequent `#main` change must preserve the active language and allow normal accessibility navigation.
- **The shared components need actual state updates.** [LanguagePicker.astro](/Users/realazy/Projects/Sites/lazyapps/src/components/LanguagePicker.astro) currently navigates unconditionally and renders its visible label only once. Hash mode must bypass that handler and update selected option, visible labels and accessible name. [SiteFooterBase.astro](/Users/realazy/Projects/Sites/lazyapps/src/components/SiteFooterBase.astro) hardcodes English text and `lang="en" dir="ltr"`; changing document language alone cannot localize it. English fallback blocks inside Arabic pages need both `lang="en"` and `dir="ltr"`.

For the resolver, explicit language hashes → saved Press Kit preference → browser preferences → English is sufficient once entrance links carry their page language. Omit referrer recovery from the minimal implementation; it cannot recover a source fragment and adds another interpretation path.

World Book/XVDL landing links should explicitly carry `#language-en`, overriding saved preferences. Conversely, an Arabic hub link to either Press Kit must carry `#language-ar`; show the Arabic shell, English product copy/materials, and a localized “Materials: English” notice. Preserve Arabic on the return link. Keep product-website destinations grounded in real marketing routes, including KeyHop Italian’s English fallback.

Validate those two contrasting entry paths, KeyHop Arabic and Italian, `#main`, and unchanged download-folder coverage. No second material picker or language-specific routes are needed.