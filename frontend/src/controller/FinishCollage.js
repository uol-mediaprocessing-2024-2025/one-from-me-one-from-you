import html2canvas from "html2canvas";

export async function scaleCollageImages(gridContainer, scaleFactor = 2) {
   try {
    const canvas = await html2canvas(gridContainer, {
      backgroundColor: null,
      scale: scaleFactor, // Skaliere das gesamte Canvas
    });

    const dataUrl = canvas.toDataURL("image/png");
    const blob = await (await fetch(dataUrl)).blob();

    console.log("Collage successfully upscaled.");
    return blob;
  } catch (error) {
    console.error("Error while scaling collage images:", error);
    throw error;
  }
}


export async function removeEmptyPlaceholders(gridContainer) {
  // Hiding placeholders
  const placeholders = gridContainer.querySelectorAll(".upload-label");
  placeholders.forEach((placeholder) => (placeholder.style.display = "none"));

  // Setting grid items to transparent
  const gridItems = gridContainer.querySelectorAll(".grid-item");
  gridItems.forEach((item) => {
    if (!item.querySelector("img")) {
      item.style.backgroundColor = "transparent"
      item.style.border = "none"; // Removing dotted border
    }
  });

  return () => {
    // Reverts changes after screenshot
    placeholders.forEach((placeholder) => (placeholder.style.display = "flex"));
    gridItems.forEach((item) => {
      if (!item.querySelector("img")) {
        item.style.backgroundColor = "";
        item.style.border = "";
      }
    });
  };
}

export async function removeRemoveButtons(gridContainer) {
  // Hiding all remove buttons
  const removeButtons = gridContainer.querySelectorAll(".remove-button");
  removeButtons.forEach((button) => (button.style.display = "none"));

  return () => {
    // Restoring remove buttons
    removeButtons.forEach((button) => (button.style.display = ""));
  };
}
