document.addEventListener("DOMContentLoaded", () => {
  const itemSelect = document.getElementById("item-select");
  const selectedTagsContainer =
    document.getElementById("selected-tags");
  const selectedTagsEmpty =
    document.getElementById("selected-tags-empty");
  const unlockedItemsInput =
    document.getElementById("unlocked-items-input");

  if (
    !itemSelect ||
    !selectedTagsContainer ||
    !selectedTagsEmpty ||
    !unlockedItemsInput
  ) {
    return;
  }

  const readSelectedItems = () => {
    try {
      const parsedItems = JSON.parse(
        unlockedItemsInput.value || "[]"
      );

      return Array.isArray(parsedItems)
        ? parsedItems
        : [];
    } catch (error) {
      return [];
    }
  };

  let selectedItems = readSelectedItems();

  const updateHiddenInput = () => {
    unlockedItemsInput.value =
      JSON.stringify(selectedItems);
  };

  const removeItem = (itemToRemove) => {
    selectedItems = selectedItems.filter(
      (item) => item !== itemToRemove
    );

    updateHiddenInput();
    renderTags();
  };

  const createTag = (item) => {
    const tag = document.createElement("span");
    tag.className = "tag-neutral";

    const title = document.createElement("span");
    title.className = "tag-title";
    title.textContent = item;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "tag-btn tag-remove";
    removeButton.setAttribute(
      "aria-label",
      `${item} entfernen`
    );
    removeButton.textContent = "×";

    removeButton.addEventListener("click", () => {
      removeItem(item);
    });

    tag.appendChild(title);
    tag.appendChild(removeButton);

    return tag;
  };

  const renderTags = () => {
    selectedTagsContainer.replaceChildren();

    selectedItems.forEach((item) => {
      selectedTagsContainer.appendChild(
        createTag(item)
      );
    });

    selectedTagsEmpty.classList.toggle(
      "d-none",
      selectedItems.length > 0
    );
  };

  itemSelect.addEventListener("change", () => {
    const selectedValue = itemSelect.value;

    if (
      !selectedValue ||
      selectedItems.includes(selectedValue)
    ) {
      itemSelect.value = "";
      return;
    }

    selectedItems.push(selectedValue);

    updateHiddenInput();
    renderTags();

    itemSelect.value = "";
  });

  updateHiddenInput();
  renderTags();
});
