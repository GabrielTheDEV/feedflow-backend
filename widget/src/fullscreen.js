export function createFullscreenViewer() {
  const viewer = document.createElement('div');
  viewer.id = 'feedflow-fullscreen-viewer';
  viewer.style.cssText = `
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 999999;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  `;
  viewer.innerHTML = `
    <img id="feedflow-fullscreen-img" src="" alt="Screenshot fullscreen" style="
      max-width: 90%;
      max-height: 90%;
      object-fit: contain;
      cursor: auto;
      border-radius: 8px;
    " />
  `;

  viewer.addEventListener('click', (e) => {
    if (e.target === viewer) {
      closeFullscreenViewer(viewer);
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeFullscreenViewer(viewer);
    }
  });

  document.body.appendChild(viewer);

  return viewer;
}

export function openFullscreenViewer(viewer, imageSrc) {
  if (!viewer || !imageSrc) return;
  const img = viewer.querySelector('#feedflow-fullscreen-img');
  if (!img) return;
  img.src = imageSrc;
  viewer.style.display = 'flex';
}

export function closeFullscreenViewer(viewer) {
  if (!viewer) return;
  viewer.style.display = 'none';
}
