import html2canvas from 'html2canvas';

const COLOR_PROPERTIES = [
  'color',
  'backgroundColor',
  'borderTopColor',
  'borderRightColor',
  'borderBottomColor',
  'borderLeftColor',
  'outlineColor',
  'textDecorationColor',
  'fill',
  'stroke',
  'caretColor',
];

function buildColorSnapshot() {
  const elements = Array.from(document.querySelectorAll('*'));
  const snapshot = elements.map((el) => {
    const computed = window.getComputedStyle(el);
    const values = {};

    for (const prop of COLOR_PROPERTIES) {
      const value = computed[prop];
      if (value) values[prop] = value;
    }

    return values;
  });

  return { elementsCount: elements.length, snapshot };
}

function applyColorSnapshotToClone(clonedDoc, colorSnapshot) {
  const clonedElements = Array.from(clonedDoc.querySelectorAll('*'));
  const len = Math.min(clonedElements.length, colorSnapshot.elementsCount);

  for (let index = 0; index < len; index += 1) {
    const el = clonedElements[index];
    const values = colorSnapshot.snapshot[index];
    if (!el || !values) continue;

    for (const prop of COLOR_PROPERTIES) {
      if (values[prop]) {
        el.style[prop] = values[prop];
      }
    }
  }
}

async function renderCanvas(options = {}) {
  return html2canvas(document.body, {
    allowTaint: true,
    useCORS: true,
    logging: false,
    scale: window.devicePixelRatio || 1,
    ...options,
  });
}

export async function captureScreenshot() {
  let canvas;

  try {
    canvas = await renderCanvas();
  } catch (error) {
    const message = String(error?.message || '').toLowerCase();
    const isUnsupportedColorError = message.includes('unsupported color function') || message.includes('oklab') || message.includes('oklch');

    if (!isUnsupportedColorError) {
      throw error;
    }

    const colorSnapshot = buildColorSnapshot();

    canvas = await renderCanvas({
      onclone: (clonedDoc) => {
        applyColorSnapshotToClone(clonedDoc, colorSnapshot);
      },
    });
  }

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Falha ao converter canvas para blob'));
      }
    }, 'image/png');
  });
}
