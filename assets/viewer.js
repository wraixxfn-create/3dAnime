(() => {
  const model = document.querySelector('#model');
  const status = document.querySelector('#viewer-status');
  const fallback = document.querySelector('#fallback');
  const progress = document.querySelector('.loading-bar');
  const rotate = document.querySelector('#rotate');
  const reset = document.querySelector('#reset');
  const views = [...document.querySelectorAll('[data-view]')];
  const controls = [rotate, reset, ...views];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const defaultOrbit = '15deg 78deg 105%';
  const orbits = { front: '0deg 78deg 105%', side: '90deg 78deg 105%', back: '180deg 78deg 105%' };
  let loaded = false;
  let failed = false;

  function setRotation(enabled) {
    model.autoRotate = enabled;
    rotate.setAttribute('aria-pressed', String(enabled));
    rotate.title = enabled ? 'Ferma la rotazione automatica' : 'Avvia la rotazione automatica';
    if (enabled) views.forEach(button => button.setAttribute('aria-pressed', 'false'));
  }

  function showError() {
    if (failed || loaded) return;
    failed = true;
    status.textContent = '';
    fallback.hidden = false;
    controls.forEach(button => { button.disabled = true; });
  }

  if (reducedMotion.matches) {
    model.removeAttribute('auto-rotate');
    rotate.setAttribute('aria-pressed', 'false');
  }

  model.addEventListener('progress', event => {
    if (event.detail && Number.isFinite(event.detail.totalProgress)) {
      progress.style.width = `${Math.round(event.detail.totalProgress * 100)}%`;
    }
  });
  model.addEventListener('load', () => {
    if (failed) return;
    loaded = true;
    controls.forEach(button => { button.disabled = false; });
    setRotation(!reducedMotion.matches);
    status.textContent = 'Modello 3D caricato';
    window.setTimeout(() => { status.textContent = ''; }, 2500);
  });
  model.addEventListener('error', showError);
  model.addEventListener('camera-change', event => {
    if (event.detail && event.detail.source === 'user-interaction') {
      views.forEach(button => button.setAttribute('aria-pressed', 'false'));
    }
  });

  views.forEach(button => button.addEventListener('click', () => {
    if (!loaded) return;
    setRotation(false);
    model.cameraOrbit = orbits[button.dataset.view];
    views.forEach(view => view.setAttribute('aria-pressed', String(view === button)));
  }));
  rotate.addEventListener('click', () => {
    if (loaded) setRotation(!model.autoRotate);
  });
  reset.addEventListener('click', () => {
    if (!loaded) return;
    model.cameraTarget = 'auto auto auto';
    model.cameraOrbit = defaultOrbit;
    model.fieldOfView = 'auto';
    views.forEach(button => button.setAttribute('aria-pressed', 'false'));
    setRotation(!reducedMotion.matches);
  });

  // Se la libreria locale non si registra, non lasciare un riquadro vuoto.
  window.setTimeout(() => {
    if (!customElements.get('model-viewer')) showError();
    else if (!loaded && !failed) status.textContent = 'Caricamento in corso…';
  }, 10000);
})();
