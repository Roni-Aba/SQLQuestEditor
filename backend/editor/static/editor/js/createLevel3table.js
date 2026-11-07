document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById(
    "table-item-form"
  );

  const columnsContainer = document.getElementById(
    "columns-container"
  );

  const addColumnButton = document.getElementById(
    "add-column-button"
  );

  const addRowButton = document.getElementById(
    "add-row-button"
  );

  const tableWrapper = document.getElementById(
    "table-wrapper"
  );

  const emptyTableMessage = document.getElementById(
    "empty-table-message"
  );

  const tableHead = document.getElementById(
    "data-table-head"
  );

  const tableBody = document.getElementById(
    "data-table-body"
  );

  const rowsJsonInput = document.getElementById(
    "rows-json"
  );

  const savedColumns = JSON.parse(
    document.getElementById(
      "saved-table-columns"
    ).textContent
  );

  const savedRows = JSON.parse(
    document.getElementById(
      "saved-table-rows"
    ).textContent
  );

  const typeOptions = JSON.parse(
    document.getElementById(
      "table-type-options"
    ).textContent
  );

  let columns = Array.isArray(savedColumns)
    ? savedColumns
    : [];

  let rows = Array.isArray(savedRows)
    ? savedRows
    : [];

  function createTypeOptions(
    selectedType
  ) {
    return typeOptions
      .map((option) => {
        const selected = (
          option.value === selectedType
        )
          ? "selected"
          : "";

        return `
          <option
            value="${option.value}"
            ${selected}
          >
            ${option.label}
          </option>
        `;
      })
      .join("");
  }

  function readRowsFromTable() {
    const currentRows = [];

    tableBody
      .querySelectorAll("tr")
      .forEach((tableRow) => {
        const row = {};

        tableRow
          .querySelectorAll("[data-column-id]")
          .forEach((input) => {
            const columnId = (
              input.dataset.columnId
            );

            if (input.type === "checkbox") {
              row[columnId] = input.checked;
            } else {
              row[columnId] = input.value;
            }
          });

        currentRows.push(row);
      });

    rows = currentRows;
  }

  function readColumnsFromForm() {
    readRowsFromTable();

    columns = Array.from(
      columnsContainer.querySelectorAll(
        ".column-editor-row"
      )
    ).map((columnRow) => {
      return {
        id: columnRow.querySelector(
          ".column-id-input"
        ).value.trim(),

        type: columnRow.querySelector(
          ".column-type-select"
        ).value,
      };
    });
  }

  function createCellInput(
    column,
    value
  ) {
    const input = document.createElement(
      "input"
    );

    input.classList.add(
      "form-control"
    );

    input.dataset.columnId = column.id;

    if (column.type === "number") {
      input.type = "number";
      input.step = "any";
      input.value = value ?? "";
    } else if (column.type === "date") {
      input.type = "date";
      input.value = value ?? "";
    } else if (column.type === "boolean") {
      input.type = "checkbox";

      input.classList.remove(
        "form-control"
      );

      input.classList.add(
        "form-check-input"
      );

      input.checked = (
        value === true
        || value === "true"
        || value === 1
        || value === "1"
      );
    } else {
      input.type = "text";
      input.value = value ?? "";
    }

    return input;
  }

  function renderColumns() {
    columnsContainer.innerHTML = "";

    if (columns.length === 0) {
      columns.push({
        id: "",
        type: "text",
      });
    }

    columns.forEach(
      (column, columnIndex) => {
        const columnRow = document.createElement(
          "div"
        );

        columnRow.className = (
          "column-editor-row row g-3 align-items-end"
        );

        columnRow.innerHTML = `
          <div class="col-12 col-lg-6">
            <label
              class="form-label"
              for="column-id-${columnIndex}"
            >
              Spaltenname
            </label>

            <input
              type="text"
              class="form-control column-id-input"
              id="column-id-${columnIndex}"
              name="column_ids[]"
              value="${column.id ?? ""}"
              placeholder="z. B. name"
              required
            >
          </div>

          <div class="col-8 col-lg-4">
            <label
              class="form-label"
              for="column-type-${columnIndex}"
            >
              Datentyp
            </label>

            <select
              class="form-select column-type-select"
              id="column-type-${columnIndex}"
              name="column_types[]"
            >
              ${createTypeOptions(column.type)}
            </select>
          </div>

          <div class="col-4 col-lg-2">
            <button
              type="button"
              class="btn btn-outline-danger w-100 remove-column-button"
              aria-label="Spalte entfernen"
            >
              <i
                class="bi bi-trash"
                aria-hidden="true"
              ></i>
            </button>
          </div>
        `;

        const idInput = columnRow.querySelector(
          ".column-id-input"
        );

        const typeSelect = columnRow.querySelector(
          ".column-type-select"
        );

        idInput.addEventListener(
          "input",
          () => {
            readColumnsFromForm();
            renderDataTable();
          }
        );

        typeSelect.addEventListener(
          "change",
          () => {
            readColumnsFromForm();
            renderDataTable();
          }
        );

        columnRow
          .querySelector(
            ".remove-column-button"
          )
          .addEventListener(
            "click",
            () => {
              readColumnsFromForm();

              columns.splice(
                columnIndex,
                1
              );

              renderColumns();
              renderDataTable();
            }
          );

        columnsContainer.appendChild(
          columnRow
        );
      }
    );
  }

  function renderDataTable() {
    tableHead.innerHTML = "";
    tableBody.innerHTML = "";

    const validColumns = columns.filter(
      (column) => column.id.trim() !== ""
    );

    if (validColumns.length === 0) {
      tableWrapper.classList.add(
        "d-none"
      );

      emptyTableMessage.classList.remove(
        "d-none"
      );

      return;
    }

    tableWrapper.classList.remove(
      "d-none"
    );

    emptyTableMessage.classList.add(
      "d-none"
    );

    validColumns.forEach((column) => {
      const heading = document.createElement(
        "th"
      );

      heading.scope = "col";
      heading.textContent = column.id;

      tableHead.appendChild(heading);
    });

    const actionHeading = document.createElement(
      "th"
    );

    actionHeading.scope = "col";
    actionHeading.className = "text-end";
    actionHeading.textContent = "Aktion";

    tableHead.appendChild(
      actionHeading
    );

    rows.forEach(
      (row, rowIndex) => {
        const tableRow = document.createElement(
          "tr"
        );

        validColumns.forEach((column) => {
          const tableCell = document.createElement(
            "td"
          );

          tableCell.appendChild(
            createCellInput(
              column,
              row[column.id]
            )
          );

          tableRow.appendChild(
            tableCell
          );
        });

        const actionCell = document.createElement(
          "td"
        );

        actionCell.className = "text-end";

        const removeButton = document.createElement(
          "button"
        );

        removeButton.type = "button";

        removeButton.className = (
          "btn btn-outline-danger"
        );

        removeButton.setAttribute(
          "aria-label",
          "Datensatz entfernen"
        );

        removeButton.innerHTML = `
          <i
            class="bi bi-trash"
            aria-hidden="true"
          ></i>
        `;

        removeButton.addEventListener(
          "click",
          () => {
            readRowsFromTable();

            rows.splice(
              rowIndex,
              1
            );

            renderDataTable();
          }
        );

        actionCell.appendChild(
          removeButton
        );

        tableRow.appendChild(
          actionCell
        );

        tableBody.appendChild(
          tableRow
        );
      }
    );
  }

  addColumnButton.addEventListener(
    "click",
    () => {
      readColumnsFromForm();

      columns.push({
        id: "",
        type: "text",
      });

      renderColumns();
      renderDataTable();
    }
  );

  addRowButton.addEventListener(
    "click",
    () => {
      readColumnsFromForm();

      const validColumns = columns.filter(
        (column) => column.id.trim() !== ""
      );

      if (validColumns.length === 0) {
        return;
      }

      const newRow = {};

      validColumns.forEach((column) => {
        newRow[column.id] = (
          column.type === "boolean"
            ? false
            : ""
        );
      });

      rows.push(newRow);

      renderDataTable();
    }
  );

  form.addEventListener(
    "submit",
    () => {
      readColumnsFromForm();
      readRowsFromTable();

      rowsJsonInput.value = JSON.stringify(
        rows
      );
    }
  );

  renderColumns();
  renderDataTable();
});
