export function windowContent(app, t, art) {
  return `<div class="pd-app-preview"><img src="${art[app]}" alt="" draggable="false"><span>${t.appNames[app]}</span></div>`;
}
