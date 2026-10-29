// Test dei controlli senza dipendenze: node tests/test_viewer.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.listeners = {}; this.attributes = {}; this.style = {}; this.disabled = true; }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  dispatch(type, detail = {}) { return this.listeners[type]?.({ detail }); }
  setAttribute(key, value) { this.attributes[key] = value; }
  removeAttribute(key) { delete this.attributes[key]; }
}
const ids = Object.fromEntries(['model', 'viewer-status', 'fallback', 'rotate', 'reset', 'zoom-in', 'zoom-out', 'fullscreen', 'viewer', 'gallery-image', 'gallery-count', 'gallery-caption'].map(id => [id, new Element()]));
const views = ['front', 'side', 'back'].map(view => new Element({ view }));
const renders = ['back', 'front'].map(render => new Element({ render }));
const progress = new Element();
ids.model.getCameraOrbit = () => ({ theta: 0.5, phi: 1, radius: 10 });
ids.viewer.requestFullscreen = () => {};
const document = {
  fullscreenEnabled: true,
  querySelector(selector) { return selector === '.loading-bar' ? progress : ids[selector.slice(1)]; },
  querySelectorAll(selector) { return selector === '[data-view]' ? views : renders; },
  addEventListener() {}
};
const window = { matchMedia: () => ({ matches: false }), setTimeout() {} };
vm.runInNewContext(fs.readFileSync('assets/viewer.js', 'utf8'), { document, window, customElements: { get: () => true } });
ids.model.dispatch('load');
assert.equal(ids['zoom-in'].disabled, false);
assert.equal(ids.fullscreen.disabled, false);
ids['zoom-in'].dispatch('click');
assert.equal(ids.model.cameraOrbit, '0.5rad 1rad 8m');
views[2].dispatch('click');
assert.equal(ids.model.cameraOrbit, '180deg 78deg 105%');
assert.equal(ids.rotate.attributes['aria-pressed'], 'false');
assert.equal(views[2].attributes['aria-pressed'], 'true');
renders[1].dispatch('click');
assert.equal(ids['gallery-image'].src, 'renders/model_preview.png');
assert.equal(ids['gallery-count'].textContent, '02 / 02');
assert.equal(renders[1].attributes['aria-pressed'], 'true');
assert.equal(renders[0].attributes['aria-pressed'], 'false');
console.log('Controlli del visore verificati.');
