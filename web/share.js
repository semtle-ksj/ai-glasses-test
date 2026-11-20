(() => {
  const art = new Image();
  art.src = new URL('share-art.jpg', document.baseURI).href;
  const qr = new Image();
  qr.src = new URL('share-qr.png', document.baseURI).href;
  const sheet = document.querySelector('#share-sheet');
  const preview = document.querySelector('#share-preview');
  const caption = document.querySelector('#share-caption');
  const address = document.querySelector('#share-address').href;
  const send = document.querySelector('#share-send');
  const copy = document.querySelector('#share-copy');
  const save = document.querySelector('#share-save');
  const status = document.querySelector('#share-status');
  const manual = document.querySelector('#share-manual');
  const filename = save.download;
  let current;

  function drawArt(ctx, x, y, width, height) {
    if (!art.complete || !art.naturalWidth) return false;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(width / 1200, height / 630);
    ctx.drawImage(art, 0, 0, art.naturalWidth, art.naturalHeight * 535 / 630, 0, 0, 1200, 535);
    const shade = ctx.createLinearGradient(0, 0, 580, 0);
    shade.addColorStop(0, 'rgba(10,24,17,.82)');
    shade.addColorStop(.65, 'rgba(10,24,17,.76)');
    shade.addColorStop(1, 'rgba(10,24,17,0)');
    ctx.fillStyle = shade;
    ctx.fillRect(0, 0, 580, 535);
    if (qr.complete && qr.naturalWidth) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(qr, 1074, 546, 74, 74);
    }
    ctx.restore();
    return true;
  }

  function open(source, text, saveOnly) {
    const card = document.createElement('canvas');
    card.width = 1200;
    card.height = 630;
    card.getContext('2d').drawImage(source, 0, 0, card.width, card.height);
    if (saveOnly) {
      const download = document.createElement('a');
      download.download = filename;
      download.href = card.toDataURL('image/png');
      download.click();
      return;
    }

    const result = { text, file: null, imageURL: null };
    current = result;
    caption.textContent = text;
    manual.value = text + '\n' + address;
    manual.hidden = true;
    status.textContent = '';
    send.hidden = typeof navigator.share !== 'function';
    send.disabled = true;
    save.removeAttribute('href');
    preview.hidden = true;
    sheet.showModal();
    card.toBlob(blob => {
      if (current !== result) return;
      if (blob) {
        if (typeof File === 'function') result.file = new File([blob], filename, { type: 'image/png' });
        result.imageURL = URL.createObjectURL(blob);
        preview.src = result.imageURL;
        preview.hidden = false;
        save.href = result.imageURL;
      } else {
        status.textContent = '이미지를 만들지 못했습니다. 결과와 링크를 공유할 수 있습니다.';
      }
      send.disabled = false;
    }, 'image/png');
  }

  send.addEventListener('click', async () => {
    const result = current;
    if (!result) return;
    const payload = { title: document.title, text: result.text, url: address };
    send.disabled = true;
    status.textContent = '';
    try {
      let data = payload;
      if (result.file && navigator.canShare) {
        const files = [result.file];
        const withImage = { ...payload, files };
        const withCaption = { title: payload.title, text: result.text + '\n' + address, files };
        if (navigator.canShare(withImage)) data = withImage;
        else if (navigator.canShare(withCaption)) data = withCaption;
      }
      await navigator.share(data);
    } catch (error) {
      if (current === result && error.name !== 'AbortError') {
        status.textContent = '공유할 수 없습니다. 결과를 복사하거나 이미지를 저장하세요.';
      }
    } finally {
      if (current === result) send.disabled = false;
    }
  });

  copy.addEventListener('click', async () => {
    const result = current;
    try {
      await navigator.clipboard.writeText(manual.value);
      if (current === result) status.textContent = '결과와 링크를 복사했습니다.';
    } catch {
      if (current !== result) return;
      manual.hidden = false;
      manual.focus();
      manual.select();
      status.textContent = '선택한 문구를 복사하세요.';
    }
  });

  sheet.addEventListener('close', () => {
    preview.removeAttribute('src');
    save.removeAttribute('href');
    if (current?.imageURL) URL.revokeObjectURL(current.imageURL);
    current = null;
  });
  window.examShare = { drawArt, open };
})();
