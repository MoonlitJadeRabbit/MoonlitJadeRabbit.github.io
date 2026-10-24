(function () {
  const arrowPrev =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 6l-6 6 6 6"></path></svg>';
  const arrowNext =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 6l6 6-6 6"></path></svg>';

  function getFigureMedia(figure) {
    const video = figure.querySelector("video");
    if (video) {
      return { kind: "video", node: video };
    }
    const img = figure.querySelector("img");
    if (img) {
      return { kind: "img", node: img };
    }
    return null;
  }

  function cloneFigureMedia(media) {
    if (media.kind === "video") {
      const video = media.node.cloneNode(true);
      video.controls = true;
      video.playsInline = true;
      video.preload = "metadata";
      return video;
    }
    const img = media.node.cloneNode(true);
    if (!img.getAttribute("loading")) {
      img.loading = "lazy";
    }
    return img;
  }

  function convertFigureGrids() {
    document.querySelectorAll(".figure-grid").forEach((grid) => {
      if (grid.dataset.gallerySkip === "true") {
        return;
      }

      const figures = Array.from(
        grid.querySelectorAll(":scope > figure, :scope > .portfolio-figure")
      );
      if (figures.length < 2) {
        return;
      }

      const label =
        grid.dataset.galleryLabel ||
        grid.getAttribute("aria-label") ||
        "Figures";

      const viewport = document.createElement("div");
      viewport.className = "reference-gallery-viewport";
      let slideCount = 0;

      figures.forEach((figure, index) => {
        const media = getFigureMedia(figure);
        if (!media) {
          return;
        }

        const slide = document.createElement("figure");
        slide.className = "reference-gallery-slide";
        if (slideCount === 0) {
          slide.classList.add("is-active");
        } else {
          slide.hidden = true;
        }

        const mediaWrap = document.createElement("div");
        mediaWrap.className = "reference-gallery-media";
        if (media.kind === "video") {
          mediaWrap.classList.add("reference-gallery-media--video");
        }
        mediaWrap.appendChild(cloneFigureMedia(media));

        slide.appendChild(mediaWrap);

        const caption = figure.querySelector("figcaption");
        if (caption) {
          const slideCaption = document.createElement("figcaption");
          slideCaption.innerHTML = caption.innerHTML;
          slide.appendChild(slideCaption);
        }

        viewport.appendChild(slide);
        slideCount += 1;
      });

      if (slideCount < 2) {
        return;
      }

      const gallery = document.createElement("section");
      gallery.className = "reference-gallery";
      gallery.setAttribute("data-reference-gallery", "");
      gallery.tabIndex = 0;
      gallery.setAttribute("aria-roledescription", "carousel");
      gallery.setAttribute("aria-label", label);

      const frame = document.createElement("div");
      frame.className = "reference-gallery-frame";

      const prevButton = document.createElement("button");
      prevButton.type = "button";
      prevButton.className = "reference-gallery-arrow";
      prevButton.setAttribute("data-gallery-prev", "");
      prevButton.setAttribute("aria-label", "Previous slide");
      prevButton.innerHTML = arrowPrev;

      const nextButton = document.createElement("button");
      nextButton.type = "button";
      nextButton.className = "reference-gallery-arrow";
      nextButton.setAttribute("data-gallery-next", "");
      nextButton.setAttribute("aria-label", "Next slide");
      nextButton.innerHTML = arrowNext;

      const dots = document.createElement("div");
      dots.className = "reference-gallery-dots";
      dots.setAttribute("data-gallery-dots", "");
      for (let dotIndex = 0; dotIndex < slideCount; dotIndex += 1) {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "reference-gallery-dot";
        if (dotIndex === 0) {
          dot.classList.add("is-active");
        }
        dot.setAttribute("data-gallery-dot", String(dotIndex));
        dot.setAttribute("aria-label", "Go to image " + (dotIndex + 1));
        dots.appendChild(dot);
      }

      frame.append(prevButton, viewport, nextButton);
      gallery.append(frame, dots);
      gallery.dataset.galleryLabel = label;
      grid.replaceWith(gallery);
    });
  }

  function pauseGalleryVideos(gallery, activeSlide) {
    gallery.querySelectorAll("video").forEach((video) => {
      if (!activeSlide || !activeSlide.contains(video)) {
        video.pause();
      }
    });
  }

  function initGalleries() {
    document.querySelectorAll("[data-reference-gallery]").forEach((gallery) => {
      const slides = Array.from(
        gallery.querySelectorAll(".reference-gallery-slide")
      );
      if (slides.length < 2) {
        return;
      }

      gallery.querySelector(".reference-gallery-toolbar")?.remove();

      const prevButton = gallery.querySelector("[data-gallery-prev]");
      const nextButton = gallery.querySelector("[data-gallery-next]");
      const frame = gallery.querySelector(".reference-gallery-frame");
      let dots = Array.from(gallery.querySelectorAll("[data-gallery-dot]"));
      if (!dots.length && frame) {
        const dotRow = document.createElement("div");
        dotRow.className = "reference-gallery-dots";
        slides.forEach((_, dotIndex) => {
          const dot = document.createElement("button");
          dot.type = "button";
          dot.className = "reference-gallery-dot";
          dot.setAttribute("data-gallery-dot", String(dotIndex));
          dot.setAttribute("aria-label", "Go to image " + (dotIndex + 1));
          dotRow.appendChild(dot);
        });
        frame.insertAdjacentElement("afterend", dotRow);
        dots = Array.from(dotRow.querySelectorAll("[data-gallery-dot]"));
      }
      let index = 0;

      function placeArrows() {
        const media = slides[index].querySelector(".reference-gallery-media");
        if (!media || !frame) {
          return;
        }
        const top = media.offsetTop + media.offsetHeight / 2;
        if (prevButton) {
          prevButton.style.top = top + "px";
        }
        if (nextButton) {
          nextButton.style.top = top + "px";
        }
      }

      function show(nextIndex) {
        index = (nextIndex + slides.length) % slides.length;
        slides.forEach((slide, slideIndex) => {
          const isActive = slideIndex === index;
          slide.classList.toggle("is-active", isActive);
          slide.hidden = !isActive;
        });
        dots.forEach((dot, dotIndex) => {
          dot.classList.toggle("is-active", dotIndex === index);
        });
        pauseGalleryVideos(gallery, slides[index]);
        placeArrows();
        const mediaEl = slides[index].querySelector("img, video");
        if (mediaEl && mediaEl.tagName === "IMG" && !mediaEl.complete) {
          mediaEl.addEventListener("load", placeArrows, { once: true });
        }
      }

      prevButton?.addEventListener("click", () => show(index - 1));
      nextButton?.addEventListener("click", () => show(index + 1));
      dots.forEach((dot) => {
        dot.addEventListener("click", () => {
          show(Number(dot.getAttribute("data-gallery-dot")));
        });
      });
      window.addEventListener("resize", placeArrows);

      gallery.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          show(index - 1);
        }
        if (event.key === "ArrowRight") {
          event.preventDefault();
          show(index + 1);
        }
      });

      show(0);
    });
  }

  convertFigureGrids();
  initGalleries();
})();
