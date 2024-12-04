<script setup>
import { store } from "@/store.js";
import axios from "axios";
import { ref, reactive } from "vue";
import { fetchAndStoreImages } from '@/controller/SynchronizeImages.js';
import { defineProps, useAttrs} from 'vue';

// To supress vue warnings
defineProps([]);
const attrs = useAttrs();

// Reactive variables
const items = reactive(Array(35).fill({ src: null, fileName: null }));
const showModal = ref(false);
const selectedIndex = ref(null);

function openImageSelection(index) {
  fetchAndStoreImages();
  selectedIndex.value = index;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  selectedIndex.value = null;
}

async function selectImage(image) {
  console.log("selectImage");
  if (selectedIndex.value !== null) {
    const scaledImage = await scaleImage(image);
    const fileName = image.split("/").pop();
    items[selectedIndex.value] = {
      src: scaledImage,
      fileName: fileName,
    };
  closeModal();
  }
}

function scaleImage(imageUrl) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = 50;
      canvas.height = 50;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, 50, 50);
      resolve(canvas.toDataURL("image/jpeg", 0.8));
    };
    img.onerror = (err) => {
      reject(new Error(`Failed to load image: ${err.message}`));
    };
    img.src = imageUrl;
  });
}


async function extractGridPositions() {
  const gridContainer = document.querySelector(".rectangle-grid");
  const gridItems = document.querySelectorAll(".grid-item");
  const containerRect = gridContainer.getBoundingClientRect();
  let positions = [];

  gridItems.forEach((item, index) => {
    const itemRect = item.getBoundingClientRect();
    const positionData = {
      id: index + 1,
      top: itemRect.top - containerRect.top,
      left: itemRect.left - containerRect.left,
      fileName: items[index].fileName || null,
    };

    positions.push(positionData);
  });

    // Sorting, starting at top left
  positions.sort((a, b) => {
    if (a.left === b.left) {
      return a.top - b.top;
    }
    return a.left - b.left;
  });

  const formData = new FormData();
  formData.append("positions", JSON.stringify(positions));

  try {
    const response = await fetch(`${store.apiUrl}/positions`, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    console.log("Response from backend:", result);
  } catch (error) {
    console.error("Error sending grid with file names:", error);
  }
}

</script>

<template>
  <div class="rectangle-grid-container">
    <div class="rectangle-grid" v-bind="attrs">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="grid-item">

        <!-- Show image if selected -->
        <label v-if="!item.src" class="upload-label" @click="openImageSelection(index)">
          + Select Image
        </label>
        <img v-else :src="item.src" alt="Bild" />
      </div>
    </div>

    <!-- Modal for image picking -->
    <div v-if="showModal" class="image-selection-modal">
      <div class="modal-content">
        <h3>Select an Image</h3>
        <div class="image-list">
          <div
            v-for="(image, i) in store.photoUrls"
            :key="i"
            class="image-item"
            @click="selectImage(image)">
            <img :src="image" alt="Uploaded Image" />
          </div>
        </div>
        <button @click="closeModal">Cancel</button>
      </div>
    </div>
  </div>

  <v-btn @click="extractGridPositions">Send to backend </v-btn>

</template>

<style scoped>
.rectangle-grid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  width: 600px;
  height: 600px;
  margin: 0 auto;
}

.rectangle-grid {
  border: 1px black;
  display: block;
  position: relative;
  width: 600px;
  height: 600px;
}

.grid-item {
  background-color: #f9f9f9;
  border: 1px dashed #ccc;
  border-radius: 8px;
  width: 50px;
  height: 50px;
  align-items: center;
  justify-content: center;
  position: absolute;
  transform: none;
  margin: 10px;
}

.grid-item.dragover{
  -webkit-box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0,0,0,0);
box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0,0,0,0);
}

.upload-label {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #888;
  cursor: pointer;
  text-align: center;
}

.upload-label input {
  visibility: hidden;
  display: none;
}

.image-selection-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  width: 300px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
  justify-content: center;
}

.image-item {
  width: 50px;
  height: 50px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.image-item img {
  max-width: 100%;
  max-height: 100%;
}

.modal-content button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.modal-content button:hover {
  background-color: #0056b3;
}

.grid-item:nth-child(1) { top: 20%; left: 50%; }
.grid-item:nth-child(2) { top: 30%; left: 50%; }
.grid-item:nth-child(3) { top: 40%; left: 50%; }
.grid-item:nth-child(4) { top: 50%; left: 50%; }
.grid-item:nth-child(5) { top: 60%; left: 50%; }

.grid-item:nth-child(6) { top: 25%; left: 60%; }
.grid-item:nth-child(7) { top: 35%; left: 60%; }
.grid-item:nth-child(8) { top: 45%; left: 60%; }
.grid-item:nth-child(9) { top: 55%; left: 60%; }

.grid-item:nth-child(10) { top: 30%; left: 70%; }
.grid-item:nth-child(11) { top: 40%; left: 70%; }
.grid-item:nth-child(12) { top: 50%; left: 70%; }

.grid-item:nth-child(13) { top: 40%; left: 80%; }

.grid-item:nth-child(14) { top: 25%; left: 40%; }
.grid-item:nth-child(15) { top: 35%; left: 40%; }
.grid-item:nth-child(16) { top: 45%; left: 40%; }
.grid-item:nth-child(17) { top: 55%; left: 40%; }

.grid-item:nth-child(18) { top: 30%; left: 30%; }
.grid-item:nth-child(19) { top: 40%; left: 30%; }
.grid-item:nth-child(20) { top: 50%; left: 30%; }

.grid-item:nth-child(20) { top: 10%; left: 50%; }
.grid-item:nth-child(21) { top: 70%; left: 50%; }

.grid-item:nth-child(22) { top: 15%; left: 60%; }
.grid-item:nth-child(23) { top: 65%; left: 60%; }

.grid-item:nth-child(24) { top: 20%; left: 70%; }
.grid-item:nth-child(25) { top: 60%; left: 70%; }

.grid-item:nth-child(26) { top: 30%; left: 80%; }
.grid-item:nth-child(27) { top: 50%; left: 80%; }

.grid-item:nth-child(28) { top: 40%; left: 90%; }

.grid-item:nth-child(29) { top: 50%; left: 30%; }

.grid-item:nth-child(30) { top: 60%; left: 10%; }
.grid-item:nth-child(31) { top: 50%; left: 20%; }
.grid-item:nth-child(32) { top: 60%; left: 20%; }

.grid-item:nth-child(33) { top: 30%; left: 20%; }
.grid-item:nth-child(34) { top: 20%; left: 20%; }
.grid-item:nth-child(35) { top: 20%; left: 10%; }





</style>
