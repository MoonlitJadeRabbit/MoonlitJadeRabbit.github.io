(function () {
  const figures = document.querySelectorAll(
    ".portfolio-figure img, .reference-gallery-slide img"
  );
  if (!figures.length) return;

  const dialog = document.createElement("dialog");
  dialog.className = "image-lightbox";
  dialog.setAttribute("aria-label", "Expanded image view");

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "image-lightbox-close";
  closeButton.setAttribute("aria-label", "Close expanded image");
  closeButton.textContent = "×";

  const fullImage = document.createElement("img");
  fullImage.className = "image-lightbox-img";
  fullImage.alt = "";

  const caption = document.createElement("p");
  caption.className = "image-lightbox-caption";

  dialog.append(closeButton, fullImage, caption);
  document.body.append(dialog);

  let savedScrollY = 0;

  function lockPageScroll() {
    savedScrollY = window.scrollY;
    document.body.classList.add("lightbox-open");
    document.body.style.top = `-${savedScrollY}px`;
  }

  function unlockPageScroll() {
    document.body.classList.remove("lightbox-open");
    document.body.style.top = "";
    const root = document.documentElement;
    const previousScrollBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    window.scrollTo(0, savedScrollY);
    root.style.scrollBehavior = previousScrollBehavior;
  }

  function openLightbox(img) {
    fullImage.src = img.currentSrc || img.src;
    fullImage.alt = img.alt;

    const figure = img.closest("figure");
    const figcaption = figure?.querySelector("figcaption");
    caption.textContent = figcaption?.textContent?.trim() || "";
    caption.hidden = !caption.textContent;

    lockPageScroll();
    dialog.showModal();
  }

  function closeLightbox() {
    if (!dialog.open) return;
    dialog.close();
    unlockPageScroll();
    fullImage.removeAttribute("src");
  }

  figures.forEach((img) => {
    img.classList.add("portfolio-zoomable");
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.setAttribute(
      "aria-label",
      `View full image: ${img.alt || "project figure"}`
    );

    img.addEventListener("click", (event) => {
      event.preventDefault();
      openLightbox(img);
    });
    img.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openLightbox(img);
      }
    });
  });

  closeButton.addEventListener("click", closeLightbox);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closeLightbox();
  });
  dialog.addEventListener("cancel", closeLightbox);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeLightbox();
  });
})();
