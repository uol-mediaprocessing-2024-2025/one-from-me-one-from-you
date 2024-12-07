<script setup>
import { ref, onMounted } from 'vue';
import axios from "axios";
import HeartGridComponent from './gridComponents/HeartGridComponent.vue';
import RectangleGridComponent from './gridComponents/RectangleGridComponent.vue';
import StarGridComponent from "@/components/gridComponents/StarGridComponent.vue";
import HexagonGridComponent from "@/components/gridComponents/HexagonGridComponent.vue";
import CloudGridComponent from "@/components/gridComponents/CloudGridComponent.vue";
import FishGridComponent from "@/components/gridComponents/FishGridComponent.vue";
import LeafGridComponent from "@/components/gridComponents/LeafGridComponent.vue";
import TriangleGridComponent from "@/components/gridComponents/TriangleGridComponent.vue";

import UploadImage from "@/components/UploadImage.vue";

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

const responseMessage = ref('');
const callPing = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/ping');
    responseMessage.value = response.data.message;
  } catch {
    responseMessage.value = 'Failed to connect';
  }
};

onMounted(() => {
  // Load persisted shape from localStorage
  const savedShape = localStorage.getItem('selectedCollageShape');
  if (savedShape) {
    selectedCollageShape.value = savedShape;
    const fileName = savedShape.split('/').pop();
    setOtherGridsInvisible(fileName);
  }

  // Initialize collage shapes
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
        <div class="option">
          <label>
            <input
              type="radio"
              name="sort"
              value="contrast"
              v-model="sortingOption"
            />
            Same face
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
