(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  var imgs = document.querySelectorAll("img.scroll-gif[data-gif]");
  if (!imgs.length) {
    return;
  }

  function playGif(img) {
    var gif = img.dataset.gif;
    if (gif && img.getAttribute("src") !== gif) {
      img.setAttribute("src", gif);
    }
  }

  function pauseGif(img) {
    var poster = img.dataset.poster;
    if (poster && img.getAttribute("src") !== poster) {
      img.setAttribute("src", poster);
    }
  }

  if (!("IntersectionObserver" in window)) {
    imgs.forEach(playGif);
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          playGif(entry.target);
        } else {
          pauseGif(entry.target);
        }
      });
    },
    { threshold: 0.35 }
  );

  imgs.forEach(function (img) {
    if (!img.dataset.poster) {
      img.dataset.poster = img.getAttribute("src") || "";
    }
    observer.observe(img);
  });
})();
