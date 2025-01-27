<script setup>
import { ref, watch } from 'vue';
import { defineProps, defineEmits } from "vue";
import { store } from "@/store.js";
import { scaleImage } from "@/controller/GridComponentHelper.js";
import { useRouter } from 'vue-router';

const router = useRouter();

const props = defineProps({
  showModal: {
    type: Boolean,
    required: true,
  },
  selectedIndex: {
    type: Number,
    required: true,
  },
  imageSelectionMode: {
    type: String,
    required: true,
  },
  userPrompt: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["close-modal", "select-image", "update:userPrompt"]);
const isDone = ref(false);
const localUserPrompt = ref(props.userPrompt);
const selectedImage = ref(null);

watch(props.userPrompt, (newValue) => {
  localUserPrompt.value = newValue;
  console.log('userPrompt changed:', newValue);
});

function closeModal() {
  isDone.value = false;
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

    if (props.imageSelectionMode !== 'style') {
      closeModal();
    } else {
      isDone.value = true;
    }
  }
}

function handleImageClick(image) {
  if (props.imageSelectionMode !== 'style') {
    selectImage(image);
  } else {
    selectedImage.value = image;
    isDone.value = true; // Set isDone to true to show the text field and button
  }
}

function handleDone() {
  if (props.imageSelectionMode === 'style' && selectedImage.value) {
    selectImage(selectedImage.value);
  }
  emit("update:userPrompt", localUserPrompt.value);
  isDone.value = false;
  closeModal();
  console.log('userPrompt on button click:', localUserPrompt.value);
}

const goToUploadPage = () => {
  router.push('/uploadImage'); // Navigate to the upload image page
};
</script>

<template>
  <div v-if="showModal" class="image-selection-modal">
    <div class="modal-content">
      <button class="close-button" @click="closeModal">×</button>

      <div v-if="!isDone">
        <h3>Select an Image</h3>

        <!-- Message when no images are available -->
        <div v-if="store.photoUrls.length === 0 && store.galleryBlobs.length === 0" class="no-images-container">
          <p>No images to display. Please upload some images.</p>
          <v-btn @click="goToUploadPage" color="primary" class="upload-button">
            Upload Images
          </v-btn>
        </div>

        <!-- Image list if images are available -->
        <div v-else class="image-list">
          <div
              v-for="(image, i) in store.photoUrls"
              :key="i"
              class="image-item"
              @click="handleImageClick(image)"
          >
            <img :src="image" alt="Uploaded Image"/>
          </div>
        </div>
      </div>

<div v-else-if="imageSelectionMode === 'style'" class="style-mode-container">
  <div class="horizontal-layout">
    <img src="../assets/whatsnext.png" alt="Selected Image" class="robot"/>
    <v-text-field class="prompt-text-field"
      v-model="localUserPrompt"
      label="What image should I place next?"
      clearable
    ></v-text-field>
  </div>
  <v-btn @click="handleDone" color="primary" class="done-button">
    Confirm
  </v-btn>
</div>
    </div>
  </div>
</template>

<style scoped>
.no-images-container {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2rem;
  color: #555;
}

.upload-button {
  margin-top: 15px;
}

.upload-button:hover {
  background-color: #0056b3;
}

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
  font-family: 'Arial', sans-serif;
  font-size: 2rem;
  font-weight: bold;
  color: black;
  text-align: center;
  margin-bottom: 30px;
  text-transform: uppercase;
  letter-spacing: 2px;
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
  background-color: #ff3b30;
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
  background-color: #d22a1e;
  transform: scale(1.2);
}

.close-button:focus {
  outline: none;
}

.done-button {
  margin-top: 15px;
}

.done-button:hover {
  background-color: #0056b3;
}

.style-mode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.robot {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
}

.prompt-text-field {
  width: 400px;
}

<style scoped>
.style-mode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.horizontal-layout {
  display: flex;
  align-items: center;
  gap: 10px;
}

.robot {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.prompt-text-field {
  width: 300px;
  height: 50px;
}
</style>
