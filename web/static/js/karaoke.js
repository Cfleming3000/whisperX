// Load words and build transcript
window.addEventListener('DOMContentLoaded', () => {
  const audio = document.getElementById('audio');
  const container = document.getElementById('transcript');
  let words = [];
  let segmentEnd = null;

  fetch('/static/words.json')
    .then((resp) => resp.json())
    .then((data) => {
      words = data;
      words.forEach((w) => {
        const span = document.createElement('span');
        span.textContent = w.word + ' ';
        span.dataset.start = w.start;
        span.dataset.end = w.end;
        span.addEventListener('click', () => {
          segmentEnd = w.end;
          audio.currentTime = w.start;
          audio.play();
        });
        container.appendChild(span);
      });
    });

  audio.addEventListener('timeupdate', () => {
    const t = audio.currentTime;
    if (segmentEnd !== null && t >= segmentEnd) {
      audio.pause();
      segmentEnd = null;
    }
    words.forEach((w, i) => {
      const span = container.children[i];
      if (t >= w.start && t < w.end) {
        span.classList.add('highlight');
      } else {
        span.classList.remove('highlight');
      }
    });
  });
});
