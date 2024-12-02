<template>
  <div class="rectangle-grid-container">
    <div class="rectangle-grid">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="grid-item"
        draggable="true"
        @dragstart="onDragStart(index)"
        @dragover.prevent
        @drop="onDrop(index)"
      >
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
            v-for="(image, i) in uploadedImages"
            :key="i"
            class="image-item"
            @click="selectImage(image)"
          >
            <img :src="image" alt="Uploaded Image" />
          </div>
        </div>
        <button @click="closeModal">Cancel</button>
      </div>
    </div>
  </div>
</template>



<script>
import { store } from "../../store.js"; // Importing image store

export default {
  name: "RectangleGrid",
  data() {
    return {
      items: Array(35).fill({ src: null }),
      draggedItemIndex: null,
      showModal: false,
      selectedIndex: null,
    };
  },
  computed: {
    uploadedImages() {
      return store.photoUrls;
    },
  },
  methods: {
    onDragStart(index) {
      this.draggedItemIndex = index;
    },

    onDrop(index) { // Reacting to image drop, either placing or preventing placement
    if (this.draggedItemIndex !== null && !this.items[index].src) {
    const draggedItem = this.items[this.draggedItemIndex];
    this.items.splice(this.draggedItemIndex, 1);
    this.items.splice(index, 0, draggedItem);
    this.draggedItemIndex = null;
  } else {
    console.log("Slot is already occupied!");
  }
}
,
    openImageSelection(index) {
      this.selectedIndex = index;
      this.showModal = true;
    },
    async selectImage(image) {
  if (this.selectedIndex !== null) {
    const scaledImage = await this.scaleImage(image);
    this.items[this.selectedIndex] = { src: scaledImage };
    this.showModal = false;
    this.selectedIndex = null;
  }
}


    ,
    closeModal() {
      this.showModal = false;
      this.selectedIndex = null;
    },
    scaleImage(imageUrl) {
      return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = 50;
        canvas.height = 50;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, 50, 50);
        resolve(canvas.toDataURL("image/jpeg", 0.8));
      };
      img.src = imageUrl;
    });
    }
  },
};

</script>



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

.grid-item:nth-child(1) { top: 10%; left: 50% }
.grid-item:nth-child(2) { top: 5%; left: 50%; }
.grid-item:nth-child(3) { top: 0%; left: 50%; }
.grid-item:nth-child(4) { top: 5%; left: 50%; }
.grid-item:nth-child(5) { top: 10%; left: 50%; }
.grid-item:nth-child(6) { top: 20%; left: 50%; }
.grid-item:nth-child(6) { top: 20%; left: 50%; }









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

</style>
