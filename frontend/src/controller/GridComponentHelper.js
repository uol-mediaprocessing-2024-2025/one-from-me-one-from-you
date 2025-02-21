import { store } from "@/store.js"; // Assuming store.js is in the src folder
import { fetchAndStoreComponentData } from "@/controller/SynchronizeImages.js";

/**
 * Updates the collage items by fetching component data and scaling images.
 * @param {String} componentName - Name of the component to fetch data for.
 * @param {Array} items - Array of items to update.
 */
export async function updateCollageItems(componentName, items) {
  await fetchAndStoreComponentData(componentName, items);
}

/**
 * Scales an image to a fixed size and returns the resulting data URL.
 * @param {String} imageUrl - URL of the image to scale.
 * @returns {Promise<String>} - Promise resolving to a base64 image string.
 */
export function scaleImage(imageUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 78;
      canvas.height = 78;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, 78, 78);
      resolve(canvas.toDataURL("image/jpeg", 0.8));
    };
    img.onerror = (err) => {
      reject(new Error(`Failed to load image: ${err.message}`));
    };
    img.src = imageUrl;
  });
}

/**
 * Updates the image selection mode by sending the new mode to the backend.
 * @param {String} newMode - The new image selection mode to set.
 */
export async function updateImageSelectionMode(newMode) {
  console.info(newMode);
  const formData = new FormData();
  formData.append("new_mode", newMode);

  try {
    const response = await fetch(`${store.apiUrl}/update_image_selection_mode`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to update image selection mode. Status: ${response.status}`);
    }

    await response.json();
  } catch (error) {
    console.error("Error updating image selection mode:", error);
  }
}

export async function newSelection(componentName, target_id) {
  const formData = new FormData();
  formData.append("component_name", componentName);
  formData.append("target_id", target_id);
  try {
    const response = await fetch(`${store.apiUrl}/new_selection`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to send information. Status: ${response.status}`);
    }

    await response.json();
  } catch (error) {
    console.error("Error sending information to the backend:", error);
  }
}

/**
 * Extracts grid positions of items inside a container.
 * @param {HTMLElement} gridContainer - The container element of the grid.
 * @param {NodeListOf<HTMLElement>} gridItems - NodeList of grid item elements.
 * @param {Array} items - Array of items containing fileName information.
 * @param {String} componentName - Name of the component to send data for.
 * @param  {String} userPrompt - User prompt to send to the backend.
 * @returns {Promise<void>}
 */
export async function extractGridPositions(gridContainer, gridItems, items, componentName, userPrompt) {
  const containerRect = gridContainer.getBoundingClientRect();
  let positions = [];

  gridItems.forEach((item, index) => {
    const itemRect = item.getBoundingClientRect();
    const positionData = {
      id: index,
      top: itemRect.top - containerRect.top,
      left: itemRect.left - containerRect.left,
      fileName: items[index].fileName || null,
    };

    positions.push(positionData);
  });

  positions.sort((a, b) => {
    if (a.left === b.left) {
      return a.top - b.top;
    }
    return a.left - b.left;
  });

  const formData = new FormData();
  formData.append("positions", JSON.stringify(positions));
  formData.append("componentName", componentName);
  formData.append("user_prompt", userPrompt);
  console.log(JSON.stringify(positions))
  try {
    const response = await fetch(`${store.apiUrl}/positions`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to send grid positions. Status: ${response.status}`);
    }

    await response.json();
  } catch (error) {
    console.error("Error sending grid positions to the backend:", error);
  }
}

export function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
export async function clearCollage(componentName) {
  const formData = new FormData();
  formData.append("component_name", componentName);

  try {
    const response = await fetch(`${store.apiUrl}/clearCollage`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to reach backend trying to clear collage. Status: ${response.status}`);
    }
  } catch (error) {
    console.error("Error clearing collage:", error);
  }
}