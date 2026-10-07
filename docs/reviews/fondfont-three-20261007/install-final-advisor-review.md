Fix one accessibility defect before presenting this as complete: mobile tab labels can disagree with their accessible names.

In `FondFontInstallGuide.astro`, `aria-label={step.short}` overrides the visible `mobileShort` text. French users see “Polices” and “Profil,” but the controls are named “Choisir” and “Télécharger”; German users see “Öffnen,” but the control is named “Einstellungen.” This can prevent speech-control users from activating tabs by their displayed names.

Remove the button’s overriding `aria-label` and the mobile label’s `aria-hidden`. The CSS-visible label can then supply the accessible name at each breakpoint.

No other must-fix defect is evident in the supplied files and images. Screenshot and caption right alignment meets the request on desktop and mobile. Screenshot size and surrounding whitespace are preferences, not blockers; the adjacent instructions provide the necessary readable steps. The hero needs no visual revision based on this evidence.