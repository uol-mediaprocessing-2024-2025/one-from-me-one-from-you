<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { store } from '../store'; // Import shared store to manage global state

const handleImageUpload = (event) => {
  console.log('handleImageUpload');
  const files = event.target.files; // FileList object containing all selected files
  if (files && files.length > 0) {
    for (const file of files) {
      const imageUrl = URL.createObjectURL(file); // Generate a preview URL for each file
      store.photoUrls.push(imageUrl); // Store the preview URL in the global store
      store.photoBlobs.push(file); // Store the file object (Blob) in the global store
    }
  }
};

const uploadImage = async () => {
  console.log('uploadImage');
  if (!store.photoBlobs.length) return; // Ensure there are files to upload

  try {
    for (const blob of store.photoBlobs) {
      const formData = new FormData();
      formData.append('file', blob); // Attach the blob to the form data

      // Send the request to the server
      const response = await axios.post(`${store.apiUrl}/saveImage`, formData, {
        responseType: 'blob', // Expect binary data (blob) as a response
      });

      if (response.status === 200) {
        const { message, file_path } = response.data;

        console.log('Image uploaded successfully:', message);
        console.log('Saved at:', file_path);
      } else {
        console.error('Unexpected response:', response);
      }
    }
  } catch (error) {
    console.error('Failed to upload images:', error);
  }
};


</script>

<template>
  <div class="upload-container">
    <!-- Image Preview -->
    <div v-if="store.photoUrls.length" class="image-preview-gallery">
      <h3>Uploaded Images:</h3>
      <div class="gallery">
        <div v-for="(url, index) in store.photoUrls" :key="index" class="gallery-item">
          <img :src="url" alt="Preview Image" />
        </div>
      </div>
    </div>

    <!-- File Upload and Buttons -->
    <div class="upload-actions">
      <button @click="() => $refs.fileInput.click()" class="choose-image-button">
        Choose Images
      </button>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleImageUpload"
        style="display: none;"
        multiple
      />

      <button
        @click="uploadImage"
        class="upload-image-button"
        :disabled="!store.photoBlobs.length">
        Upload Images
      </button>
    </div>
  </div>
</template>

<style scoped>
.upload-container {
  margin: 20px auto;
  text-align: center;
}

.image-preview img {
  max-width: 300px;
  margin: 10px auto;
  display: block;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.upload-actions {
  margin: 20px;
}

.choose-image-button, .upload-image-button {
  margin: 5px;
  padding: 10px 20px;
  background-color: #007BFF;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.choose-image-button:hover, .upload-image-button:hover {
  background-color: #0056b3;
}

.upload-image-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.gallery-item img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>