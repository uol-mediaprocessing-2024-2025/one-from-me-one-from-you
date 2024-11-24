<script setup>
import { ref, onMounted } from 'vue';
import axios from "axios";

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
    console.log("Shape bereits ausgewählt.");
    return;
  }
  selectedCollageShape.value = imageSrc;
}

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



// Reaktive Daten
const areas = ref([]); // Liste der Bereiche
const areaIDs = ref([]); // Vergebene Area-IDs
const currentMaxID = ref(-1); // Start-ID
const selectedAreaId = ref(null); // Aktuell ausgewählte Area-ID

// Neue Area-ID generieren
const generateNewAreaID = () => {
  currentMaxID.value += 1;
  areaIDs.value.push(currentMaxID.value);
  return currentMaxID.value;
};

// Neue Area zur Liste hinzufügen
const addNewImageArea = (newAreaID, event) => {
  const newArea = {
    id: newAreaID,
    x: event.offsetX + 277,
    y: event.offsetY + 21,
  };
  areas.value.push(newArea);
  console.log("Neue Bereichsdetails:", newArea);
  return newAreaID;
};

// Funktion: Bildauswahlfenster öffnen und Bild platzieren
const openImageSelectorAndPlaceImage = async (areaID) => {
  const area = areas.value.find((area) => area.id === areaID);
  if (!area) {
    console.error(`Keine Area mit ID ${areaID} gefunden.`);
    return;
  }

  const { x, y } = area;

  // Modal erstellen
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
    <h3>Wählen Sie ein Bild aus</h3>
    <input type="file" id="imageFileInput" accept="image/*" />
    <button id="confirmImageSelectionButton">Bild platzieren</button>
    <button id="cancelImageSelectionButton">Abbrechen</button>
  `;
  document.body.appendChild(modal);

  // Event-Listener für Bild platzieren
  document.getElementById("confirmImageSelectionButton").addEventListener("click", () => {
    const imageInput = document.getElementById("imageFileInput");
    const file = imageInput.files[0];
    if (!file) {
      alert("Bitte wählen Sie ein Bild aus.");
      return;
    }

    const reader = new FileReader();
    reader.onload = function (event) {
      const collage = document.getElementById("collage-container");
      const img = document.createElement("img");
      img.src = event.target.result;
      img.style.position = "absolute";
      img.style.left = `${x}px`;
      img.style.top = `${y}px`;
      img.style.maxWidth = "100px";
      img.style.maxHeight = "100px";
      collage.appendChild(img);
    };
    console.log(`Bild platziert bei ${x} und ${y}.`)
    reader.readAsDataURL(file);
    document.body.removeChild(modal);
  });

  // Event-Listener für Abbrechen
  document.getElementById("cancelImageSelectionButton").addEventListener("click", () => {
    document.body.removeChild(modal);
  });
};

// Funktion: Klick auf die Collage behandeln
const handleCollageClick = (event) => {
  console.log("Collage clicked at: ", event.offsetX + 277, event.offsetY + 21);
  const area_id = generateNewAreaID();
  addNewImageArea(area_id, event);
  openImageSelectorAndPlaceImage(area_id);
};

// Collage aktualisieren
const updateCollageWithPlacement = async () => {
  try {
    const response = await axios.get("http://localhost:8000/get_collage");
    const collageImage = document.getElementById("collageImage");
    collageImage.src = response.data.updated_collage_url;
    console.log("Collage aktualisiert.");
  } catch (error) {
    console.error("Fehler beim Aktualisieren der Collage:", error);
  }
};

// onMounted-Hook
onMounted(() => {
  console.log("Komponente wurde gemountet.");
});




</script>

<template>
  <div class="main-container">
    <!-- Collage Preview -->
    <div class="collage-preview">
      <div class="collage-shape">
        <div id="collage-container" @click="handleCollageClick($event)">
        <img :src="selectedCollageShape" alt="Collage Preview"/>
        </div>
        <p>[Image is used as the collage later on]</p>
        <v-btn>Select</v-btn>
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

.collage-container {
  position: relative;
  width: 100%;
  height: auto;
  overflow: hidden;
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
