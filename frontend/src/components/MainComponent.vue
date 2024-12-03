<script setup>
import { ref, onMounted } from 'vue';
import axios from "axios";
import { store } from '../store';
import HeartGridComponent from './gridComponents/HeartGridComponent.vue';
import RectangleGridComponent from './gridComponents/RectangleGridComponent.vue';
import StarGridComponent from "@/components/gridComponents/StarGridComponent.vue";
import HexagonGridComponent from "@/components/gridComponents/HexagonGridComponent.vue";
import CloudGridComponent from "@/components/gridComponents/CloudGridComponent.vue";
import FishGridComponent from "@/components/gridComponents/FishGridComponent.vue";
import LeafGridComponent from "@/components/gridComponents/LeafGridComponent.vue";
import TriangleGridComponent from "@/components/gridComponents/TriangleGridComponent.vue";

import UploadImage from "@/components/UploadImage.vue";
const uploadedPhotos = ref([]); // Stores uploaded photos

const collageShapes = ref([]); // Stores collage shape options
const selectedCollageShape = ref('placeholder-heart.png'); // Default collage shape
const quantity = ref(50); // Range for number of photos
const spacing = ref(10); // Range for spacing
const sortingOption = ref('contrast'); // Selected sorting option

onMounted(() => {
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
});

const updateCollagePreview = async (imageSrc) => {
  if (selectedCollageShape.value === imageSrc) {
    console.log('Shape already selected.');
    return;
  }
  selectedCollageShape.value = imageSrc;
  const fileName = imageSrc.split('/').pop();
  setOtherGridsInvisible(fileName)
};


const responseMessage = ref('');
const callPing = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/ping');
    responseMessage.value = response.data.message;
  } catch {
    responseMessage.value = 'Failed to connect';
  }
};

const isHeartGridVisible = ref(false);
const isRectangleGridVisible = ref(false);
const isStarGridVisible = ref(false);
const isHexagonGridVisible = ref(false);
const isCloudGridVisible = ref(false);
const isFishGridVisible = ref(false);
const isLeafGridVisible = ref(false);
const isTriangleGridVisible = ref(false);

const setOtherGridsInvisible = (grid) => {
  console.log(grid)
  isHeartGridVisible.value = false;
  isRectangleGridVisible.value = false;
  isStarGridVisible.value = false;
  isHexagonGridVisible.value = false;
  isCloudGridVisible.value = false;
  isFishGridVisible.value = false;
  isLeafGridVisible.value = false;
  isTriangleGridVisible.value = false;

  if (grid === "heart.png") isHeartGridVisible.value = true;
  if (grid === "rectangle.png") isRectangleGridVisible.value = true;
  if (grid === "star.png") isStarGridVisible.value = true;
  if (grid === "hexagon.png") isHexagonGridVisible.value = true;
  if (grid === "cloud.png") isCloudGridVisible.value = true;
  if (grid === "fish.png") isFishGridVisible.value = true;
  if (grid === "leaf.png") isLeafGridVisible.value = true;
  if (grid === "triangle.png") isTriangleGridVisible.value = true;
};

onMounted(() => {
  console.log("Component mounted.");
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
});

</script>

<template>
  <div class="main-container">
    <!-- Collage Preview -->
    <div class="collage-preview">
      <div class="collage-shape">
         <!-- Shape components -->
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
      <section class="settings">
        <h2>Settings</h2>

        <!-- Debug Remove -->
        <button @click="callPing">Ping Backend</button>
        <p>{{ responseMessage }}</p>
        <!-- Debug Remove -->
      </section>

      <!-- Sorting Options -->
      <section class="sorting-options">
        <h2>Collage options</h2>
        <ul>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="contrast"
                v-model="sortingOption"
              />
              Same face
            </label>
          </li>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="size"
                v-model="sortingOption"
              />
              Similarity
            </label>
          </li>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="harmoniousColors"
                v-model="sortingOption"
              />

            </label>
          </li>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="saturation"
                v-model="sortingOption"
              />

            </label>
          </li>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="style"
                v-model="sortingOption"
              />
              Style
            </label>
          </li>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="random"
                v-model="sortingOption"
              />

            </label>
          </li>
        </ul>
      </section>

      <section class="collage-shapes">
        <h2>Collage Shape</h2>
        <div class="shapes">
          <img
            v-for="shape in collageShapes"
            :key="shape.alt"
            :src="shape.src"
            :alt="shape.alt"
            @click="updateCollagePreview(shape.src)"
          />
        </div>
      </section>
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

</style>
