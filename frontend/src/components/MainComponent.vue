<script setup>
import { ref, onMounted } from 'vue';

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

// Update the preview image
const updateCollagePreview = (imageSrc) => {
  selectedCollageShape.value = imageSrc;
};

// Handle photo upload
const handlePhotoUpload = (event) => {
  const files = event.target.files;
  uploadedPhotos.value = [];
  Array.from(files).forEach((file) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        uploadedPhotos.value.push(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  });
};
</script>

<template>
  <div class="main-container">
    <!-- Collage Preview -->
    <div class="collage-preview">
      <div class="collage-shape">
        <img :src="selectedCollageShape" alt="Collage Preview" />
        <p>[Image is used as the collage later on]</p>
      </div>
    </div>

    <div class="settings-panel">
      <section class="settings">
        <h2>Settings</h2>
        <label for="quantity">Number of Photos</label>
        <input
          type="range"
          id="quantity"
          min="1"
          max="100"
          v-model="quantity"
        />
        <label for="spacing">Spacing</label>
        <input type="range" id="spacing" min="0" max="50" v-model="spacing" />
      </section>

      <!-- Sorting Options -->
      <section class="sorting-options">
        <h2>Sort Photos By</h2>
        <ul>
          <li>
            <label>
              <input
                type="radio"
                name="sort"
                value="contrast"
                v-model="sortingOption"
              />
              Contrast
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
              Size
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
              Harmonious Colors
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
              Saturation
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
              Random
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

    <div class="photo-selection">
      <h2>Photos</h2>
      <input
        type="file"
        id="upload"
        multiple
        accept="image/*"
        @change="handlePhotoUpload"
      />
      <div class="photo-gallery">
        <img
          v-for="photo in uploadedPhotos"
          :key="photo"
          :src="photo"
          alt="Uploaded Photo"
        />
      </div>
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
}

.collage-preview img {
  width: 300px;
  height: auto;
  border: 2px solid #ccc;
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
</style>
