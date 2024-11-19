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

const updateCollagePreview = async (imageSrc) => {
  if (selectedCollageShape.value !== imageSrc) {
    selectedCollageShape.value = imageSrc;
    return;
  }

  try {
    const formData = new FormData();
    const imageBlob = await fetch(imageSrc).then((res) => res.blob());
    formData.append("image", imageBlob);
    formData.append("number_images", quantity.value);
    formData.append("buffer", spacing.value);

    const response = await fetch("http://localhost:8000/collage-selected", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      selectedCollageShape.value = url;

      // Analysiere und erstelle Hotspots direkt in der Map
      createClickableAreas(url);
    } else {
      console.error("Fehler beim Erstellen der Collage:", response.statusText);
    }
  } catch (error) {
    console.error("Ein Fehler ist aufgetreten:", error);
  }
};

const createClickableAreas = (collageUrl) => {
  const img = new Image();
  img.src = collageUrl;
  img.crossOrigin = "Anonymous";

  img.onload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const whiteFields = [];

    // Suche nach weißen Bereichen
    for (let y = 0; y < img.height; y++) {
      for (let x = 0; x < img.width; x++) {
        const index = (y * img.width + x) * 4;
        const r = imageData.data[index];
        const g = imageData.data[index + 1];
        const b = imageData.data[index + 2];
        const a = imageData.data[index + 3];

        if (r === 255 && g === 255 && b === 255 && a === 255) {
          whiteFields.push({ x, y });
        }
      }
    }

    // Gruppiere und erstelle `<area>`-Elemente
    const uniqueFields = groupWhiteFields(whiteFields, img.width, img.height);
    renderImageMap(uniqueFields, collageUrl);
  };
};


const groupWhiteFields = (whiteFields, width, height) => {
  const uniqueFields = [];

  // Gruppiere basierend auf Pixeln zu Rechtecken
  // (Eine vereinfachte Version der Flood-Fill-Methode)
  whiteFields.forEach((field) => {
    if (!uniqueFields.some((rect) => field.x >= rect.minX && field.x <= rect.maxX && field.y >= rect.minY && field.y <= rect.maxY)) {
      uniqueFields.push({
        minX: field.x,
        minY: field.y,
        maxX: field.x + 50, // Breite des Feldes (anpassbar)
        maxY: field.y + 50, // Höhe des Feldes (anpassbar)
      });
    }
  });

  return uniqueFields;
};

const renderImageMap = (fields, collageUrl) => {
  const collageContainer = document.querySelector(".collage-container");
  collageContainer.innerHTML = ""; // Entferne alte Inhalte

  // Erstelle das Bild mit einer Map
  const img = document.createElement("img");
  img.src = collageUrl;
  img.useMap = "#collageMap";
  collageContainer.appendChild(img);

  const map = document.createElement("map");
  map.name = "collageMap";

  fields.forEach((field, index) => {
    const area = document.createElement("area");
    area.shape = "rect";
    area.coords = `${field.minX},${field.minY},${field.maxX},${field.maxY}`;
    area.href = "#"; // Platzhalter
    area.onclick = (e) => {
      e.preventDefault();
      handleUploadClick(index);
    };
    map.appendChild(area);
  });

  collageContainer.appendChild(map);
};

const handleUploadClick = (index) => {
  // Trigger den Upload für das entsprechende Feld
  const input = document.createElement("input");
  input.type = "file";
  input.accept = "image/*";

  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        console.log(`Bild für Feld ${index} hochgeladen:`, event.target.result);
        // Speichere oder verarbeite das Bild für das entsprechende Feld
      };
      reader.readAsDataURL(file);
    }
  };

  // Öffne den Dateiauswahl-Dialog
  input.click();
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
        <v-btn @click="updateCollagePreview(selectedCollageShape, quantity, spacing)">Select</v-btn>
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
</style>
