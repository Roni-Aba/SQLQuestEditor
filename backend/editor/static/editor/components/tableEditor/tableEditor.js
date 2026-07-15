document.addEventListener("DOMContentLoaded", () => {
  const columnRows = document.getElementById("column-rows");
  const addColumnRowButton =
    document.getElementById("add-column-row");
  const optionsElement =
    document.getElementById("data-type-options");

  if (
    !columnRows ||
    !addColumnRowButton ||
    !optionsElement
  ) {
    return;
  }

  const readDataTypeOptions = () => {
    try {
      const parsedOptions = JSON.parse(
        optionsElement.textContent
      );

      return Array.isArray(parsedOptions)
        ? parsedOptions
        : [];
    } catch (error) {
      console.error(
        "Datentypen konnten nicht geladen werden.",
        error
      );

      return [];
    }
  };

  const dataTypeOptions = readDataTypeOptions();

  const createOption = ({ value, label }) => {
    const option = document.createElement("option");

    option.value = value;
    option.textContent = label;

    return option;
  };

  const createTypeSelect = (rowNumber) => {
    const wrapper = document.createElement("div");
    const label = document.createElement("label");
    const select = document.createElement("select");

    label.htmlFor = `column-type-${rowNumber}`;
    label.className = "visually-hidden";
    label.textContent = "Datentyp";

    select.id = `column-type-${rowNumber}`;
    select.name = "column_types[]";
    select.className = "form-select";
    select.required = true;

    const placeholder = document.createElement("option");

    placeholder.value = "";
    placeholder.textContent = "Datentyp auswählen";

    select.appendChild(placeholder);

    dataTypeOptions.forEach((optionData) => {
      select.appendChild(
        createOption(optionData)
      );
    });

    wrapper.appendChild(label);
    wrapper.appendChild(select);

    return wrapper;
  };

  const createIdInput = (rowNumber) => {
    const wrapper = document.createElement("div");
    const label = document.createElement("label");
    const input = document.createElement("input");

    label.htmlFor = `column-id-${rowNumber}`;
    label.className = "visually-hidden";
    label.textContent = "Spalten-ID";

    input.id = `column-id-${rowNumber}`;
    input.type = "text";
    input.name = "column_ids[]";
    input.className = "form-control";
    input.placeholder = "Spalten-ID";
    input.required = true;

    wrapper.appendChild(label);
    wrapper.appendChild(input);

    return wrapper;
  };

  const createRemoveButton = () => {
    const wrapper = document.createElement("div");
    const button = document.createElement("button");
    const icon = document.createElement("i");

    wrapper.className =
      "table-editor__remove-column";

    button.type = "button";
    button.className =
      "btn btn-outline-danger table-editor__remove-button";

    button.setAttribute(
      "aria-label",
      "Spalte entfernen"
    );

    icon.className = "bi bi-x-lg";
    icon.setAttribute("aria-hidden", "true");

    button.appendChild(icon);
    wrapper.appendChild(button);

    return wrapper;
  };

  const createColumnRow = () => {
    const row = document.createElement("div");
    const rowNumber =
      columnRows.querySelectorAll(
        ".table-editor__row"
      ).length + 1;

    row.className = "table-editor__row";

    row.appendChild(
      createIdInput(rowNumber)
    );

    row.appendChild(
      createTypeSelect(rowNumber)
    );

    row.appendChild(
      createRemoveButton()
    );

    return row;
  };

  addColumnRowButton.addEventListener("click", () => {
    columnRows.appendChild(
      createColumnRow()
    );
  });

  columnRows.addEventListener("click", (event) => {
    const removeButton = event.target.closest(
      ".table-editor__remove-button"
    );

    if (!removeButton) {
      return;
    }

    const row = removeButton.closest(
      ".table-editor__row"
    );

    row?.remove();
  });
});