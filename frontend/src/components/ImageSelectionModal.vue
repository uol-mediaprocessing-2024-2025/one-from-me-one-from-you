<script setup>
import { defineProps, defineEmits } from "vue";
import { store } from "@/store.js";
import { scaleImage } from "@/controller/GridComponentHelper.js";

const props = defineProps({
  showModal: {
    type: Boolean,
    required: true,
  },
  selectedIndex: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close-modal", "select-image"]);

function closeModal() {
  emit("close-modal");
}

async function selectImage(image) {
  if (props.selectedIndex !== null) {
    const fileName = image.split("/").pop();
    const scaledImage = await scaleImage(image);

    emit("select-image", {
      index: props.selectedIndex,
      src: scaledImage,
      fileName: fileName,
    });

    emit("close-modal");
  }
}
</script>

<template>
  <div v-if="showModal" class="image-selection-modal">
    <div class="modal-content">
      <button class="close-button" @click="closeModal">×</button>
      <h3>Select an Image</h3>
      <div class="image-list">
        <div
          v-for="(image, i) in store.photoUrls"
          :key="i"
          class="image-item"
          @click="selectImage(image)"
        >
          <img :src="image" alt="Uploaded Image" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-selection-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  width: 80%;
  max-width: 800px;
  max-height: 80%;
  overflow-y: auto;
  position: relative;
}

h3 {
  font-family: 'Arial', sans-serif; /* Clean, simple font */
  font-size: 2rem;
  font-weight: bold;
  color: black; /* Solid black color */
  text-align: center;
  margin-bottom: 30px;
  text-transform: uppercase; /* Optional: Adds emphasis with uppercase letters */
  letter-spacing: 2px; /* Optional: Adds a bit more space between letters */
}

.image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 20px;
  margin-top: 20px;
  justify-items: center;
  padding: 0 10px;
}

.image-item {
  width: 100%;
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 8px;
  transition: transform 0.2s ease, border 0.2s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.image-item:hover {
  transform: scale(1.1);
  border: 2px solid #007bff;
}

.image-item img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  object-fit: cover;
}

.close-button {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: #ff3b30; /* Red background */
  border: none;
  color: white;
  font-size: 2rem;
  font-weight: bold;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.close-button:hover {
  background-color: #d22a1e; /* Darker red when hovered */
  transform: scale(1.2);
}

.close-button:focus {
  outline: none;
}
</style>
