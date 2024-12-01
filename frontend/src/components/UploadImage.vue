<script setup>
import axios from 'axios';
import { store } from '../store';
import { ref } from 'vue';

const successMessage = ref('');

const handleImageUpload = (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    for (const file of files) {
      const imageUrl = URL.createObjectURL(file);
      store.photoUrls.push(imageUrl);
      store.photoBlobs.push(file);
    }
  }
};

const uploadImage = async () => {
  if (!store.photoBlobs.length)
    return;

  try {
    const formData = new FormData();

    store.photoBlobs.forEach((blob, index) => {
      const fileExtension = blob.type.split('/')[1];
      const filename = `image_${index + 1}.${fileExtension}`;
      formData.append('files', blob, filename);
    });

    const response = await axios.post(`${store.apiUrl}/saveImages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.status === 200) {
      const { message, file_paths } = response.data;

      console.log('Images uploaded successfully:', message);
      console.log('Saved at:', file_paths);

      successMessage.value = 'Images uploaded successfully!';
    } else {
      console.error('Unexpected response:', response);
    }
  } catch (error) {
    console.error('Failed to upload images:', error);
  }
};
</script>

<template>
  <div class="upload-container">

    <div v-if="successMessage" class="success-message">
      <p>{{ successMessage }}</p>
    </div>

    <!-- Image Preview -->
    <div v-if="store.photoUrls.length && !successMessage" class="image-preview-gallery">
      <h3>Preview Images:</h3>
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

.success-message {
  color: green;
  font-size: 18px;
  margin-bottom: 20px;
}

.upload-container {
  margin: 20px auto;
  text-align: center;
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

.gallery {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  overflow-x: auto;
}

.gallery-item {
  flex: 0 0 auto;
}

.gallery-item img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>