import html2canvas from 'html2canvas';

export async function captureScreenshot() {
  const canvas = await html2canvas(document.body, {
    allowTaint: true,
    useCORS: true,
    logging: false,
    scale: window.devicePixelRatio || 1,
  });

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
