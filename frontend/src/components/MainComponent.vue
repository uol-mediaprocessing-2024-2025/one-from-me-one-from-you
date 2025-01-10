<script setup>
import {ref, onMounted, provide} from 'vue';
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

import UploadImage from "@/components/UploadImage.vue";
import {fetchAndStoreImages} from "@/controller/SynchronizeImages.js";
import {clearCollage, wait} from "@/controller/GridComponentHelper.js";
import {removeEmptyPlaceholders, scaleCollageImages} from "@/controller/FinishCollage.js";

import {store} from "@/store.js";

const collageShapes = ref([]); // Stores collage shape options
const selectedCollageShape = ref('placeholder-heart.png'); // Default collage shape
const sortingOption = ref('contrast'); // Selected sorting option

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

// For mapping the currently selected shape onto the collageName, as in each Component
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

const responseMessage = ref('');

const downloadSuccess = ref(false);
const saveToGallerySuccess = ref(false);

const callPing = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/ping');
    responseMessage.value = response.data.message;
  } catch {
    responseMessage.value = 'Failed to connect';
  }
};

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

  try {
    // Getting screenshot
    const canvas = await html2canvas(gridContainer, {
      backgroundColor: null,
    });

    // Bild speichern
    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = `${activeGrid.split('.')[0]}-collage.png`;
    link.click();
    displaySuccess(downloadSuccess)
  } catch (error) {
    console.error("Couldn't take screenshot:", error);
  } finally {
    // Resetting styles
    resetPlaceholders();
  }
};

const displaySuccess = (popup, duration = 1500) => {
  popup.value = true; // Popup anzeigen
  setTimeout(() => {popup.value = false; // Popup nach der angegebenen Zeit ausblenden
  }, duration);
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

  try {
    // Scaling collage
    const scaledBlob = await scaleCollageImages(gridContainer, 2);

    // Saving in backend
    const formData = new FormData();
    formData.append("files", scaledBlob, "collage-upscaled.png");

    const response = await axios.post(`${store.apiUrl}/saveImages`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (response.status === 200) {
      console.log("Upscaled collage saved to gallery.");
      displaySuccess(saveToGallerySuccess)
      await fetchAndStoreImages();
    } else {
      console.error("Unexpected response:", response);
    }
  } catch (error) {
    console.error("Couldn't upscale or save collage:", error);
  } finally {
    resetPlaceholders();
    gridContainer.style.cssText = originalStyle;
  }
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
        <HeartGridComponent v-if="isHeartGridVisible" class="heart-grid-container"/>
        <RectangleGridComponent v-if="isRectangleGridVisible" class="rectangle-grid-container"/>
        <StarGridComponent v-if="isStarGridVisible" class="star-grid-container"/>
        <CloudGridComponent v-if="isCloudGridVisible" class="cloud-grid-container"/>
        <HexagonGridComponent v-if="isHexagonGridVisible" class="hexagon-grid-container"/>
        <FishGridComponent v-if="isFishGridVisible" class="fish-grid-container"/>
        <LeafGridComponent v-if="isLeafGridVisible" class="leaf-grid-container"/>
        <TriangleGridComponent v-if="isTriangleGridVisible" class="triangle-grid-container"/>
      </div>
    </div>

    <div class="settings-panel">


      <!-- Sorting Options -->
      <h2>Settings</h2>
      <section class="sorting-options horizontal-layout">
        <div class="option">
          <label>
            <input
                type="radio"
                name="sort"
                value="contrast"
                v-model="sortingOption"
            />
            Face Detection
          </label>
        </div>
        <div class="option">
          <label>
            <input
                type="radio"
                name="sort"
                value="size"
                v-model="sortingOption"
            />
            Similarity
          </label>
        </div>
        <div class="option">
          <label>
            <input
                type="radio"
                name="sort"
                value="style"
                v-model="sortingOption"
            />
            Style
          </label>
        </div>
      </section>
      <br>
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
      <v-btn @click="captureAndDownload">Download</v-btn>
      <v-btn @click="safeCollageToGallery">Save to Gallery</v-btn>
      <v-btn @click="removeImages">Clear collage</v-btn>
    </div>
  </div>

  <div>
    <UploadImage/>
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

#collage-container {
  position: relative;
  width: 100%;
  height: auto;
  overflow: hidden;
  border: 2px solid #ccc;
  border-radius: 5px;
}

.collage-container img {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

.collage-container map area {
  cursor: pointer;
}

.popup {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.shapes img.selected-shape {
  border-color: Red;
}

.horizontal-layout {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.horizontal-layout .option {
  margin-right: 20px;
}

.grid-item:not(:has(img)) {
  background-color: transparent !important; /* Entferne die Hintergrundfarbe */
  border: none; /* Optional: Entferne die Umrandung */
}

.success-message{
  color: green;
}

</style>
