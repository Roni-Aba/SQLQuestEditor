document.addEventListener("DOMContentLoaded", () => {
  const hintTypeSelect =
    document.getElementById("hint-type");

  const hintTextArea =
    document.getElementById("hint-text-area");

  const hintImageArea =
    document.getElementById("hint-image-area");

  const hintImageInput =
    document.getElementById("hint-image");

  const hintImageName =
    document.getElementById("hint-image-name");

  if (
    !hintTypeSelect ||
    !hintTextArea ||
    !hintImageArea ||
    !hintImageInput ||
    !hintImageName
  ) {
    return;
  }

  const updateHintFields = () => {
    const selectedType = hintTypeSelect.value;

    const showText =
      selectedType === "text" ||
      selectedType === "text_image";

    const showImage =
      selectedType === "image" ||
      selectedType === "text_image";

    hintTextArea.classList.toggle(
      "d-none",
      !showText
    );

    hintImageArea.classList.toggle(
      "d-none",
      !showImage
    );

    const hintTextInput =
      document.getElementById("hint-text");

    if (hintTextInput) {
      hintTextInput.required = showText;
    }

    hintImageInput.required =
      showImage && !hintImageName.textContent.includes(
        "Bereits ausgewählt:"
      );
  };

  hintImageInput.addEventListener("change", () => {
    const selectedFile =
      hintImageInput.files[0] ?? null;

    hintImageName.textContent = selectedFile
      ? `Neu ausgewählt: ${selectedFile.name}`
      : "Noch kein Bild ausgewählt";

    updateHintFields();
  });

  hintTypeSelect.addEventListener(
    "change",
    updateHintFields
  );

  updateHintFields();
});
