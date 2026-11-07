document.addEventListener("DOMContentLoaded", () => {

  const hintRows = document.getElementById("hint-rows");
  const addHintRowButton = document.getElementById("add-hint-row");

  if (!hintRows || !addHintRowButton) {
    return;
  }

  const createHintRow = () => {

    const row = document.createElement("div");

    row.className =
      "row g-3 align-items-center hint-row";

    row.innerHTML = `
      <div class="col-12 col-lg-3">
        <input
          type="number"
          name="hint_attempts[]"
          class="form-control"
          placeholder="Versuche"
          min="1"
        >
      </div>

      <div class="col">
        <input
          type="text"
          name="hint_texts[]"
          class="form-control"
          placeholder="Hinweistext"
        >
      </div>

      <div class="col-auto">
        <button
          type="button"
          class="btn btn-outline-danger remove-hint-row"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    `;

    return row;
  };

  addHintRowButton.addEventListener("click", () => {
    hintRows.appendChild(createHintRow());
  });

  hintRows.addEventListener("click", (event) => {

    const removeButton = event.target.closest(
      ".remove-hint-row"
    );

    if (!removeButton) {
      return;
    }

    removeButton.closest(".hint-row")?.remove();

    if (!hintRows.querySelector(".hint-row")) {
      hintRows.appendChild(createHintRow());
    }

  });

});
