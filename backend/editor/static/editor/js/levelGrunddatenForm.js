document.addEventListener("DOMContentLoaded", () => {
  const pictureInput = document.getElementById(
    "level-picture-input"
  );
  const form = pictureInput?.form;

  const pictureFeedback = document.getElementById(
    "level-picture-feedback"
  );

  const submitButton = document.getElementById(
    form?.dataset.submitButtonId || ""
  );

  if (!pictureInput || !pictureFeedback || !submitButton) {
    return;
  }

  const hasExistingPicture =
    form.dataset.hasExistingPicture === "true";

  const requirePicture =
    form.dataset.requirePicture === "true";

  const existingPictureText =
    pictureFeedback.textContent.trim();

  const updateSubmitButton = (hasPicture) => {
    if (!requirePicture) {
      return;
    }

    submitButton.disabled = !hasPicture;
  };

  const updatePictureFeedback = (selectedFile) => {
    if (selectedFile) {
      pictureFeedback.textContent =
        `Neu ausgewählt: ${selectedFile.name}`;

      updateSubmitButton(true);
      return;
    }

    pictureFeedback.textContent = hasExistingPicture
      ? existingPictureText
      : "Noch kein Bild ausgewählt";

    updateSubmitButton(hasExistingPicture);
  };

  updateSubmitButton(hasExistingPicture);

  pictureInput.addEventListener("change", () => {
    const selectedFile = pictureInput.files[0] ?? null;

    updatePictureFeedback(selectedFile);
  });
});
