<script setup>
import { ref, onMounted } from 'vue';
import axios from "axios";
import HeartGridComponent from './HeartGridComponent.vue';
import RectangleGridComponent from './RectangleGridComponent.vue';
import StarGridComponent from "@/components/StarGridComponent.vue";

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
  if (imageSrc.includes('heart.png')) {
    isHeartGridVisible.value = true;
    isRectangleGridVisible.value = false;
    isStarGridVisible.value = false;
  }
  else if(imageSrc.includes('rectangle.png')){
    isRectangleGridVisible.value = true;
    isHeartGridVisible.value = false;
    isStarGridVisible.value = false;
    }
  else if(imageSrc.includes('star.png')){
    isStarGridVisible.value = true;
    isRectangleGridVisible.value = false;
    isHeartGridVisible.value = false;
    }
  else {
    isHeartGridVisible.value = false;
    isRectangleGridVisible.value = false;
    isStarGridVisible.value = false;

  }
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


const areas = ref([]);
const areaIDs = ref([]);
const currentMaxID = ref(-1);


const generateNewAreaID = () => {
  currentMaxID.value += 1;
  areaIDs.value.push(currentMaxID.value);
  return currentMaxID.value;
};

// Creating image areas for later editing
const addNewImageArea = (newAreaID, event) => {
  const newArea = {
    id: newAreaID,
    x: event.offsetX,
    y: event.offsetY,
  };
  areas.value.push(newArea);
  console.log("New area:", newArea);
  return newAreaID;
};


const openImageSelectorAndPlaceImage = async (areaID) => {
  const area = areas.value.find((area) => area.id === areaID);
  if (!area) {
    console.error(`No area found: ${areaID}.`);
    return;
  }
  const { x, y } = area;
  const sidebar = document.querySelector('.v-navigation-drawer__content'); //Getting sidebar (from App.vue)

  // Creating a modal to select and confirm image placement.
  const modal = document.createElement("div");
  modal.id = "imageSelectorModal";
  modal.style.position = "fixed";
  modal.style.top = "50%";
  modal.style.left = "50%";
  modal.style.transform = "translate(-50%, -50%)";
  modal.style.zIndex = "1000";
  modal.style.padding = "20px";
  modal.style.backgroundColor = "#fff";
  modal.style.border = "1px solid #ccc";
  modal.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
  modal.innerHTML = `
  <h3 style="color: #555555;">Select image</h3>
  <input type="file" id="imageFileInput" accept="image/*" style="color: black"/>
  <button id="confirmImageSelectionButton" style="background-color: #42b883; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px;">Place</button>
  <button id="cancelImageSelectionButton" style="background-color: #ff0000; color: white; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px;">Cancel</button>
`;
  document.body.appendChild(modal);

  document.getElementById("confirmImageSelectionButton").addEventListener("click", () => {
    const imageInput = document.getElementById("imageFileInput");
    const file = imageInput.files[0];
    if (!file) {
      alert("Select an image.");
      return;
    }

    const reader = new FileReader();
    reader.onload = function (event) {
      const collage = document.getElementById("collage-container");
      const img = document.createElement("img");
      img.src = event.target.result;
      img.style.position = "absolute";
      img.style.maxWidth = "100px";
      img.style.maxHeight = "100px";

      img.onload = () => {
        const imageWidth = img.offsetWidth;
        const imageHeight = img.offsetHeight;
        img.style.left = `${x - imageWidth / 2}px`;
        img.style.top = `${y - imageHeight / 2}px`;
        collage.appendChild(img);
      };
    };
    console.log(`Image placed at ${x}, ${y}.`);
    reader.readAsDataURL(file);
    document.body.removeChild(modal);
  });

  document.getElementById("cancelImageSelectionButton").addEventListener("click", () => {
    document.body.removeChild(modal);
  });
};

//TODO: Replace with broader vars upon full grid replacement.
const isHeartGridVisible = ref(false);
const isRectangleGridVisible = ref(false);
const isStarGridVisible = ref(false);


// Function that handles placing images on collage, takes the mouse click event to track it's coords
// TODO: Remove upon full Grid replacement
const handleCollageClick = (event) => {
  if(!isHeartGridVisible.value) {
    console.log("Collage clicked at: ", event.pageX, event.pageY);
    const area_id = generateNewAreaID();
    addNewImageArea(area_id, event);
    openImageSelectorAndPlaceImage(area_id);
  }
};

onMounted(() => {
  console.log("Component mounted.");
});



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

</script>

<template>
  <div class="main-container">
    <!-- Collage Preview -->
    <div class="collage-preview">
      <div class="collage-shape">
        <div id="collage-container" @click="handleCollageClick($event)" v-if="!isHeartGridVisible && !isRectangleGridVisible && !isStarGridVisible">
          <img :src="selectedCollageShape" alt="Collage Preview"/>
        </div>
         <!-- Shape components -->
        <HeartGridComponent v-if="isHeartGridVisible" class="heart-grid-container"/>
        <RectangleGridComponent v-if="isRectangleGridVisible" class="rectangle-grid-container"/>
        <StarGridComponent v-if="isStarGridVisible" class="star-grid-container"/>
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
          max="10"
          v-model="quantity"
        />
        <label for="spacing">Spacing</label>
        <input type="range" id="spacing" min="0" max="50" v-model="spacing" />
        <button @click="callPing">Ping Backend</button>
        <p>{{ responseMessage }}</p>
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
