const gameUploadForm = document.getElementById("game-upload-form");
const gameFolderInput = document.getElementById("game-folder");

gameUploadForm.addEventListener("submit", () => {
  gameUploadForm.querySelectorAll('input[name="game_relative_paths"]').forEach((input) => {
    input.remove();
  });

  for (const file of gameFolderInput.files) {
    const pathInput = document.createElement("input");
    pathInput.type = "hidden";
    pathInput.name = "game_relative_paths";
    pathInput.value = file.webkitRelativePath || file.name;
    gameUploadForm.appendChild(pathInput);
  }
});
