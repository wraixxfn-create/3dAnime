(() => {
  const model = document.querySelector('#model');
  const status = document.querySelector('#viewer-status');
  const fallback = document.querySelector('#fallback');
  const progress = document.querySelector('.loading-bar');
  const rotate = document.querySelector('#rotate');
  const reset = document.querySelector('#reset');
  const zoomIn = document.querySelector('#zoom-in');
  const zoomOut = document.querySelector('#zoom-out');
  const fullscreen = document.querySelector('#fullscreen');
  const shell = document.querySelector('#viewer');
  const views = [...document.querySelectorAll('[data-view]')];
  const controls = [rotate, reset, zoomIn, zoomOut, fullscreen, ...views];
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
    fullscreen.disabled = !document.fullscreenEnabled || !shell.requestFullscreen;
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

  function zoom(factor) {
    if (!loaded) return;
    const orbit = model.getCameraOrbit();
    model.cameraOrbit = `${orbit.theta}rad ${orbit.phi}rad ${orbit.radius * factor}m`;
  }
  zoomIn.addEventListener('click', () => zoom(0.8));
  zoomOut.addEventListener('click', () => zoom(1.25));

  fullscreen.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement === shell) await document.exitFullscreen();
      else await shell.requestFullscreen();
    } catch (_) {
      status.textContent = 'Schermo intero non disponibile in questo browser.';
    }
  });
  document.addEventListener('fullscreenchange', () => {
    const active = document.fullscreenElement === shell;
    fullscreen.setAttribute('aria-pressed', String(active));
    fullscreen.setAttribute('aria-label', active ? 'Esci dallo schermo intero' : 'Apri a schermo intero');
    fullscreen.title = active ? 'Esci dallo schermo intero' : 'Schermo intero';
  });

  const gallery = {
    back: { src: 'renders/model_back.png', alt: 'Render della vista posteriore di Hoshino, con mantello blu e stella dorata', count: '01 / 02', caption: 'VISTA POSTERIORE · RENDER DEL MODELLO' },
    front: { src: 'renders/model_preview.png', alt: 'Render della vista frontale di Hoshino con armatura e spada', count: '02 / 02', caption: 'VISTA FRONTALE · RENDER DEL MODELLO' }
  };
  const galleryImage = document.querySelector('#gallery-image');
  const galleryButtons = [...document.querySelectorAll('[data-render]')];
  galleryButtons.forEach(button => button.addEventListener('click', () => {
    const render = gallery[button.dataset.render];
    galleryImage.src = render.src;
    galleryImage.alt = render.alt;
    document.querySelector('#gallery-count').textContent = render.count;
    document.querySelector('#gallery-caption').textContent = render.caption;
    galleryButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  }));

  // Se la libreria locale non si registra, non lasciare un riquadro vuoto.
  window.setTimeout(() => {
    if (!customElements.get('model-viewer')) showError();
    else if (!loaded && !failed) status.textContent = 'Caricamento in corso…';
  }, 10000);
})();
