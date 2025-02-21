<script setup>
import {ref, onMounted} from 'vue';
import axios from "axios";
import html2canvas from "html2canvas";
import HeartGridComponent from './gridComponents/HeartGridComponent.vue';
import RectangleGridComponent from './gridComponents/RectangleGridComponent.vue';
import StarGridComponent from "@/components/gridComponents/StarGridComponent.vue";
import HexagonGridComponent from "@/components/gridComponents/HexagonGridComponent.vue";
import CloudGridComponent from "@/components/gridComponents/CloudGridComponent.vue";
import FishGridComponent from "@/components/gridComponents/FishGridComponent.vue";
import LeafGridComponent from "@/components/gridComponents/LeafGridComponent.vue";
import TriangleGridComponent from "@/components/gridComponents/TriangleGridComponent.vue";

import {fetchAndStoreImages} from "@/controller/SynchronizeImages.js";
import {clearCollage, updateImageSelectionMode} from "@/controller/GridComponentHelper.js";
import {removeEmptyPlaceholders, scaleCollageImages, removeRemoveButtons} from "@/controller/FinishCollage.js";

import {store} from "@/store.js";

const collageShapes = ref([]); // Stores collage shape options
const selectedCollageShape = ref('placeholder-heart.png'); // Default collage shape

const isHeartGridVisible = ref(false);
const isRectangleGridVisible = ref(false);
const isStarGridVisible = ref(false);
const isHexagonGridVisible = ref(false);
const isCloudGridVisible = ref(false);
const isFishGridVisible = ref(false);
const isLeafGridVisible = ref(false);
const isTriangleGridVisible = ref(false);

const isSelectedShape = (shapeSrc) => {
  return shapeSrc === selectedCollageShape.value;
};

const shapeVisibility = {
  "heart.png": isHeartGridVisible,
  "rectangle.png": isRectangleGridVisible,
  "star.png": isStarGridVisible,
  "hexagon.png": isHexagonGridVisible,
  "cloud.png": isCloudGridVisible,
  "fish.png": isFishGridVisible,
  "leaf.png": isLeafGridVisible,
  "triangle.png": isTriangleGridVisible,
};

const ImageSelectionModes = {
  FACE_DETECTION: "faceDetection",
  SIMILARITY: "similarity",
  STYLE: "style",
};

const imageSelectionMode = ref(ImageSelectionModes.SIMILARITY);
const userPrompt = ref("");

const onImageSelectionModeChange = (event) => {
  const newMode = event.target.value;
  imageSelectionMode.value = newMode;
  updateImageSelectionMode(newMode);
  console.log(imageSelectionMode.value);
};

const componentNameMap = {
  "heart.png": "heartComponent",
  "rectangle.png": "rectangleComponent",
  "star.png": "starComponent",
  "hexagon.png": "hexagonComponent",
  "cloud.png": "cloudComponent",
  "fish.png": "fishComponent",
  "leaf.png": "leafComponent",
  "triangle.png": "triangleComponent",
};

const downloadSuccess = ref(false);
const saveToGallerySuccess = ref(false);
onMounted(() => {
  const savedShape = localStorage.getItem('selectedCollageShape');
  if (savedShape) {
    selectedCollageShape.value = savedShape;
    const fileName = savedShape.split('/').pop();
    setOtherGridsInvisible(fileName);
  }

  const collageTemplatesPath = 'collage_templates/';
  const shapeFiles = [
    'heart.png',
    'star.png',
    'hexagon.png',
    'cloud.png',
    'fish.png',
    'leaf.png',
    'rectangle.png',
    'triangle.png',
  ];
  collageShapes.value = shapeFiles.map((fileName) => ({
    src: `${collageTemplatesPath}${fileName}`,
    alt: fileName.split('.')[0],
  }));

  fetchAndStoreImages();
});

const captureAndDownload = async () => {
  const activeGrid = Object.keys(shapeVisibility).find(
      (key) => shapeVisibility[key].value
  );

  if (!activeGrid) {
    console.error("No grid found.");
    return;
  }

  const gridContainer = document.querySelector(
      `.${activeGrid.split('.')[0]}-grid-container`
  );

  if (!gridContainer) {
    console.error("No grid-container found.");
    return;
  }

  // Removing empty slots
  const resetPlaceholders = await removeEmptyPlaceholders(gridContainer);

  // Temporarily remove remove-buttons
  const resetRemoveButtons = await removeRemoveButtons(gridContainer);

  try {
    // Taking screenshot
    const canvas = await html2canvas(gridContainer, {
      backgroundColor: null,
    });

    // Save the image
    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = `${activeGrid.split('.')[0]}-collage.png`;
    link.click();
    displaySuccess(downloadSuccess);
  } catch (error) {
    console.error("Couldn't take screenshot:", error);
  } finally {
    // Reset styles
    resetPlaceholders();
    resetRemoveButtons();
  }
};

const safeCollageToGallery = async () => {
  const activeGrid = Object.keys(shapeVisibility).find(
      (key) => shapeVisibility[key].value
  );

  if (!activeGrid) {
    console.error("No grid found.");
    return;
  }

  const gridContainer = document.querySelector(
      `.${activeGrid.split('.')[0]}-grid-container`
  );

  if (!gridContainer) {
    console.error("No grid-container found.");
    return;
  }

  const originalStyle = gridContainer.style.cssText;
  gridContainer.style.margin = "0";
  gridContainer.style.padding = "0";
  gridContainer.style.transform = "none";
  gridContainer.style.position = "static";

  const resetPlaceholders = await removeEmptyPlaceholders(gridContainer);
  const resetRemoveButtons = await removeRemoveButtons(gridContainer);

  const scaledBlob = await scaleCollageImages(gridContainer, 2);
  store.galleryBlobs.push(scaledBlob);

  // Save the new galleryBlob to localStorage
  saveToLocalStorage(); // Ensure localStorage is updated with the new blob

  displaySuccess(saveToGallerySuccess);

  await fetchAndStoreImages();

  resetPlaceholders();
  resetRemoveButtons();
  gridContainer.style.cssText = originalStyle;
};

const saveToLocalStorage = () => {
  const blobArray = store.galleryBlobs.map(blob => ({
    type: blob.type,
    data: Array.from(new Uint8Array(blob))
  }));
  localStorage.setItem('galleryBlobs', JSON.stringify(blobArray));
};

const displaySuccess = (popup, duration = 2000) => {
  popup.value = true;
  setTimeout(() => {
    popup.value = false;
  }, duration);
};

const updateCollagePreview = async (imageSrc) => {
  if (selectedCollageShape.value === imageSrc) {
    return;
  }

  selectedCollageShape.value = imageSrc;
  localStorage.setItem('selectedCollageShape', imageSrc);
  const fileName = imageSrc.split('/').pop();
  setOtherGridsInvisible(fileName);
};

const setOtherGridsInvisible = (shape) => {
  Object.keys(shapeVisibility).forEach((key) => {
    shapeVisibility[key].value = false;
  });

  if (shape in shapeVisibility) {
    shapeVisibility[shape].value = true;
  }
};

const removeImages = async () => {
  const fileName = selectedCollageShape.value.split('/').pop();
  const componentName = componentNameMap[fileName];

  if (!componentName) {
    console.error("No matching componentName found for:", fileName);
    return;
  }
  try {
    await clearCollage(componentName);
    console.log(`Images cleared for component: ${componentName}`);
  } catch (error) {
    console.error("Error clearing collage:", error);
  }
  location.reload();
};
</script>

<template>
  <div class="main-container">
    <div class="collage-preview">
      <div class="collage-shape">
        <HeartGridComponent v-if="isHeartGridVisible" class="heart-grid-container" :userPrompt="userPrompt"
                            :imageSelectionMode="imageSelectionMode"/>
        <RectangleGridComponent v-if="isRectangleGridVisible" class="rectangle-grid-container" :userPrompt="userPrompt"
                                :imageSelectionMode="imageSelectionMode"/>
        <StarGridComponent v-if="isStarGridVisible" class="star-grid-container" :userPrompt="userPrompt"
                           :imageSelectionMode="imageSelectionMode"/>
        <CloudGridComponent v-if="isCloudGridVisible" class="cloud-grid-container" :userPrompt="userPrompt"
                            :imageSelectionMode="imageSelectionMode"/>
        <HexagonGridComponent v-if="isHexagonGridVisible" class="hexagon-grid-container" :userPrompt="userPrompt"
                              :imageSelectionMode="imageSelectionMode"/>
        <FishGridComponent v-if="isFishGridVisible" class="fish-grid-container" :userPrompt="userPrompt"
                           :imageSelectionMode="imageSelectionMode"/>
        <LeafGridComponent v-if="isLeafGridVisible" class="leaf-grid-container" :userPrompt="userPrompt"
                           :imageSelectionMode="imageSelectionMode"/>
        <TriangleGridComponent v-if="isTriangleGridVisible" class="triangle-grid-container" :userPrompt="userPrompt"
                               :imageSelectionMode="imageSelectionMode"/>
      </div>
    </div>

    <div class="settings-panel">
      <h2>Image Selection Mode</h2>
      <section class="sorting-options horizontal-layout">
        <v-radio-group v-model="imageSelectionMode" @change="onImageSelectionModeChange">
          <div class="option">
            <v-radio label="Face Similarity" :value="ImageSelectionModes.FACE_DETECTION" name="sort"
                     color="indigo"></v-radio>
          </div>
          <div class="option">
            <v-radio label="Visual Similarity" :value="ImageSelectionModes.SIMILARITY" name="sort"
                     color="indigo"></v-radio>
          </div>
          <div class="option">
            <v-radio label="Textual Prompt" :value="ImageSelectionModes.STYLE" name="sort" color="indigo"></v-radio>
          </div>
        </v-radio-group>
      </section>

      <!--
      <section>
        <h2>Textual Prompt</h2>
        <v-text-field class="next-image-prompt"
                      v-model="userPrompt"
                      clear-icon="mdi-close-circle"
                      label="Type in a prompt for the next image!"
                      type="text"
                      clearable
                      :disabled="imageSelectionMode === ImageSelectionModes.FACE_DETECTION || imageSelectionMode === ImageSelectionModes.SIMILARITY"></v-text-field>
      </section>
      <br>
      -->

      <section class="collage-shapes">
        <h2>Collage Shape</h2>
        <div class="shapes">
          <img
              v-for="shape in collageShapes"
              :key="shape.alt"
              :src="shape.src"
              :alt="shape.alt"
              @click="updateCollagePreview(shape.src)"
              :class="{ 'selected-shape': isSelectedShape(shape.src) }"
          />
        </div>
      </section>
      <br>
      <p v-if="downloadSuccess" class="success-message">Collage Downloaded successfully!</p>
      <p v-if="saveToGallerySuccess" class="success-message">Collage saved to gallery!</p>
      <button
          @click="captureAndDownload"
          class="button download-button">
        Download
      </button>
      <button
          @click="safeCollageToGallery"
          class="button save-button">
        Save to Gallery
      </button>
      <button
          @click="removeImages"
          class="button clear-button">
        Clear Collage
      </button>
      <button
          onclick="window.open('https://youtu.be/zOwMHHnZ_78', '_blank')"
          class="button watch-tutorial-button">
        Watch Tutorial
      </button>
    </div>
  </div>
</template>

<style scoped>
header {
  width: 100%;
  padding: 20px;
  background-color: #ddd;
  text-align: center;
}

header h1 {
  font-size: 24px;
}

.main-container {
  display: flex;
  gap: 20px;
  padding: 20px;
  flex-direction: row; /* Ensures horizontal alignment */
}

.collage-preview {
  flex: 3; /* Gives more room to the collage preview */
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid #ccc;
  border-radius: 5px;
  padding: 20px;
  background-color: #f9f9f9;
}

.settings-panel {
  flex: 1;
  max-height: 70%; /* Restricts the height of the settings panel */
  display: flex;
  flex-direction: column;
  gap: 10px; /* Reduced the space between elements */
  padding: 15px; /* Reduced overall padding */
  border: 2px solid #ddd;
  border-radius: 5px;
  background-color: #fefefe;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto; /* Adds scrolling if the content exceeds the height */
}

.settings-panel h2 {
  font-size: 18px; /* Reduced heading font size */
  margin-bottom: 10px; /* Reduced margin below headings */
}

.settings-panel section {
  margin-bottom: 10px; /* Reduced spacing between sections */
}

.settings-panel .horizontal-layout {
  gap: 10px; /* Reduced spacing between radio buttons */
}

.settings-panel .button {
  margin: 5px 0; /* Reduced button margin */
}

.settings-panel .shapes {
  display: flex;
  flex-wrap: wrap;
  gap: 5px; /* Reduced spacing between shape images */
  justify-content: flex-start;
}

.shapes img {
  width: 45px; /* Slightly smaller images */
  height: 45px;
  cursor: pointer;
  border: 2px solid #ccc;
  border-radius: 5px;
  object-fit: cover;
}

.collage-preview img {
  width: 300px;
  height: auto;
}

.shapes img {
  width: 50px;
  height: 50px;
  margin: 5px;
  cursor: pointer;
  border: 2px solid #ccc;
  border-radius: 5px;
  object-fit: cover;
}

.photo-gallery img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border: 2px solid #ccc;
  border-radius: 5px;
}

.button {
  font-family: 'Arial', sans-serif;
  font-size: 16px;
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  color: #fff;
  margin: 10px 0;
  transition: transform 0.2s, box-shadow 0.2s;
}

.watch-tutorial-button {
  background-color: #FFB347;
}

.watch-tutorial-button:hover {
  background-color: #FF8C00;
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.download-button {
  background-color: #28a745;
}

.download-button:hover {
  background-color: #218838;
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.save-button {
  background-color: #007bff;
}

.save-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.clear-button {
  background-color: #dc3545;
}

.clear-button:hover {
  background-color: #c82333;
  transform: scale(1.05);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.collage-container img {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

.collage-container map area {
  cursor: pointer;
}

.shapes img.selected-shape {
  border-color: blue;
}

.horizontal-layout {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.horizontal-layout .option {
  margin-right: 20px;
}

.success-message {
  color: green;
}

</style>