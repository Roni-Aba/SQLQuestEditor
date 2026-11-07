document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("item-position-form");

  const imageArea = document.querySelector("#image-area");
  const backgroundImage = document.querySelector(
    "#level-background-image"
  );
  const selectionBox = document.querySelector("#selection-box");

  const startImageButton = document.querySelector(
    "#start-image-selection"
  );
  const startIconButton = document.querySelector(
    "#start-icon-selection"
  );
  const continueButton = document.querySelector(
    "#continue-button"
  );

  const coordinateInputs = {
    image: {
      x: document.querySelector("#image-x"),
      y: document.querySelector("#image-y"),
      width: document.querySelector("#image-width"),
      height: document.querySelector("#image-height")
    },
    icon: {
      x: document.querySelector("#icon-x"),
      y: document.querySelector("#icon-y"),
      width: document.querySelector("#icon-width"),
      height: document.querySelector("#icon-height")
    }
  };

  if (
    !form ||
    !imageArea ||
    !backgroundImage ||
    !selectionBox ||
    !startImageButton ||
    !startIconButton ||
    !continueButton
  ) {
    return;
  }

  let activeTarget = null;
  let isDrawing = false;
  let startX = 0;
  let startY = 0;

  function hasValidBoundingBox(target) {
    const inputs = coordinateInputs[target];

    if (
      !inputs.x ||
      !inputs.y ||
      !inputs.width ||
      !inputs.height
    ) {
      return false;
    }

    const x = Number(inputs.x.value);
    const y = Number(inputs.y.value);
    const width = Number(inputs.width.value);
    const height = Number(inputs.height.value);

    return (
      Number.isFinite(x) &&
      Number.isFinite(y) &&
      Number.isFinite(width) &&
      Number.isFinite(height) &&
      x >= 0 &&
      y >= 0 &&
      width > 0 &&
      height > 0
    );
  }

  function updateButtonStates() {
    const imageBoxIsValid =
      hasValidBoundingBox("image");

    const iconBoxIsValid =
      hasValidBoundingBox("icon");

    startIconButton.disabled = !imageBoxIsValid;

    continueButton.disabled = !(
      imageBoxIsValid &&
      iconBoxIsValid
    );

    /*
     * Falls der Bildbereich nachträglich ungültig wird,
     * darf der Iconmodus nicht aktiv bleiben.
     */
    if (
      !imageBoxIsValid &&
      activeTarget === "icon"
    ) {
      activeTarget = null;
      selectionBox.style.display = "none";

      startIconButton.classList.remove("active");
      startIconButton.setAttribute(
        "aria-pressed",
        "false"
      );
    }
  }

  function setActiveTarget(target) {
    if (
      target === "icon" &&
      !hasValidBoundingBox("image")
    ) {
      return;
    }

    activeTarget = target;
    selectionBox.style.display = "none";

    const imageIsActive = target === "image";
    const iconIsActive = target === "icon";

    startImageButton.classList.toggle(
      "active",
      imageIsActive
    );

    startIconButton.classList.toggle(
      "active",
      iconIsActive
    );

    startImageButton.setAttribute(
      "aria-pressed",
      String(imageIsActive)
    );

    startIconButton.setAttribute(
      "aria-pressed",
      String(iconIsActive)
    );
  }

  function setValues(
    target,
    x,
    y,
    width,
    height
  ) {
    const inputs = coordinateInputs[target];

    inputs.x.value = x;
    inputs.y.value = y;
    inputs.width.value = width;
    inputs.height.value = height;

    updateButtonStates();
  }

  function getImageScale() {
    const displayedRect =
      backgroundImage.getBoundingClientRect();

    const scaleX =
      backgroundImage.naturalWidth /
      displayedRect.width;

    const scaleY =
      backgroundImage.naturalHeight /
      displayedRect.height;

    return {
      scaleX: scaleX,
      scaleY: scaleY,
      displayedRect: displayedRect
    };
  }

  function getMousePositionOnDisplayedImage(event) {
    const imageData = getImageScale();
    const displayedRect =
      imageData.displayedRect;

    return {
      x: event.clientX - displayedRect.left,
      y: event.clientY - displayedRect.top
    };
  }

  function convertDisplayedBoxToOriginalImageBox(
    x,
    y,
    width,
    height
  ) {
    const imageData = getImageScale();

    return {
      x: Math.round(x * imageData.scaleX),
      y: Math.round(y * imageData.scaleY),
      width: Math.round(
        width * imageData.scaleX
      ),
      height: Math.round(
        height * imageData.scaleY
      )
    };
  }

  startImageButton.addEventListener(
    "click",
    function () {
      setActiveTarget("image");
    }
  );

  startIconButton.addEventListener(
    "click",
    function () {
      setActiveTarget("icon");
    }
  );

  imageArea.addEventListener(
    "mousedown",
    function (event) {
      if (!activeTarget) {
        return;
      }

      event.preventDefault();

      isDrawing = true;

      const position =
        getMousePositionOnDisplayedImage(event);

      startX = position.x;
      startY = position.y;

      selectionBox.style.display = "block";
      selectionBox.style.left = `${startX}px`;
      selectionBox.style.top = `${startY}px`;
      selectionBox.style.width = "0px";
      selectionBox.style.height = "0px";
    }
  );

  imageArea.addEventListener(
    "mousemove",
    function (event) {
      if (!isDrawing || !activeTarget) {
        return;
      }

      const position =
        getMousePositionOnDisplayedImage(event);

      const currentX = position.x;
      const currentY = position.y;

      const x = Math.min(startX, currentX);
      const y = Math.min(startY, currentY);

      const width = Math.abs(
        currentX - startX
      );

      const height = Math.abs(
        currentY - startY
      );

      selectionBox.style.left = `${x}px`;
      selectionBox.style.top = `${y}px`;
      selectionBox.style.width = `${width}px`;
      selectionBox.style.height = `${height}px`;
    }
  );

  document.addEventListener(
    "mouseup",
    function () {
      if (!isDrawing || !activeTarget) {
        return;
      }

      isDrawing = false;

      const displayedX =
        parseFloat(selectionBox.style.left) || 0;

      const displayedY =
        parseFloat(selectionBox.style.top) || 0;

      const displayedWidth =
        parseFloat(selectionBox.style.width) || 0;

      const displayedHeight =
        parseFloat(selectionBox.style.height) || 0;

      /*
       * Ein Klick ohne gezogenen Bereich zählt nicht
       * als gültige Bounding Box.
       */
      if (
        displayedWidth <= 0 ||
        displayedHeight <= 0
      ) {
        selectionBox.style.display = "none";
        return;
      }

      const originalBox =
        convertDisplayedBoxToOriginalImageBox(
          displayedX,
          displayedY,
          displayedWidth,
          displayedHeight
        );

      setValues(
        activeTarget,
        originalBox.x,
        originalBox.y,
        originalBox.width,
        originalBox.height
      );
    }
  );

  Object.values(coordinateInputs).forEach(
    function (inputs) {
      Object.values(inputs).forEach(
        function (input) {
          input?.addEventListener(
            "input",
            updateButtonStates
          );
        }
      );
    }
  );

  form.addEventListener(
    "submit",
    function (event) {
      const imageBoxIsValid =
        hasValidBoundingBox("image");

      const iconBoxIsValid =
        hasValidBoundingBox("icon");

      if (
        imageBoxIsValid &&
        iconBoxIsValid
      ) {
        return;
      }
      event.preventDefault();
      updateButtonStates();
    }
  );
  updateButtonStates();
});
