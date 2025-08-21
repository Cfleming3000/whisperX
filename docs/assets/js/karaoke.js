// Load words and build transcript
window.addEventListener('DOMContentLoaded', () => {
  const audio = document.getElementById('audio');
  const container = document.getElementById('transcript');
  let words = [];
  let segmentEnd = null;
  const wordSpans = [];

  document.getElementById('speed').addEventListener('change', (e) => {
    audio.playbackRate = parseFloat(e.target.value);
  });

  // Usamos directamente la ruta del atributo data-json
  const jsonSrc = container.dataset.json;

  fetch(jsonSrc)
    .then((resp) => resp.json())
    .then((data) => {
      words = data.segments.flatMap(seg => seg.words || []);

      data.segments.forEach((seg) => {
        const div = document.createElement('div');
        div.classList.add('segment');
        div.textContent = seg.text;
        div.addEventListener('click', () => {
          audio.currentTime = seg.start;
          segmentEnd = seg.end;
          audio.play();
        });
        container.appendChild(div);
      });

      words.forEach((w) => {
        const span = document.createElement('span');
        span.classList.add('word');
        span.textContent = w.word + ' ';
        span.dataset.start = w.start;
        span.dataset.end = w.end;
        span.addEventListener('click', () => {
          segmentEnd = w.end;
          audio.currentTime = w.start;
          audio.play();
        });
        container.appendChild(span);
        wordSpans.push(span);
      });
    })
    .catch(err => console.error("Error cargando JSON:", err));

  audio.addEventListener('timeupdate', () => {
    const t = audio.currentTime;
    if (segmentEnd !== null && t >= segmentEnd) {
      audio.pause();
      segmentEnd = null;
    }
    wordSpans.forEach((span, i) => {
      const w = words[i];
      if (t >= w.start && t < w.end) {
        span.classList.add('highlight');
      } else {
        span.classList.remove('highlight');
      }
    });
  });
});

