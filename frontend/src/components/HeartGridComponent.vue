<template>
  <div class="heart-grid-container">
    <div class="heart-grid">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="grid-item"
        draggable="true"
        @dragstart="onDragStart(index)"
        @dragover.prevent
        @drop="onDrop(index)"
      >
        <label v-if="!item.src" class="upload-label">
          <input type="file" accept="image/*" @change="uploadImage(index, $event)" />
          + Add image
        </label>
        <img v-else :src="item.src" alt="Bild" />
      </div>
    </div>
  </div>
</template>



<script>
export default {
  name: "HeartGrid",
  data() {
    return {
      items: [
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
        { src: null },
      ],
      draggedItemIndex: null, // Speichert den Index des gezogenen Elements
    };
  },
  methods: {
    onDragStart(index) {
      this.draggedItemIndex = index;
    },
    onDrop(index) {
      if (this.draggedItemIndex !== null) {
        // Tauscht die Position der Items
        const draggedItem = this.items[this.draggedItemIndex];
        this.items.splice(this.draggedItemIndex, 1);
        this.items.splice(index, 0, draggedItem);
        this.draggedItemIndex = null;
      }
    },
    uploadImage(index, event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();

    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Erstelle ein Canvas, um das Bild zu skalieren
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = 50;
        canvas.height = 50;

        ctx.drawImage(img, 0, 0, 50, 50);

        const resizedImage = canvas.toDataURL('image/jpeg', 0.8);
        this.items[index].src = resizedImage;
      };

      img.src = e.target.result;
    };

    reader.readAsDataURL(file);
  }
}
,
  },
};


</script>



<style scoped>
.heart-grid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  width: 600px;
  height: 600px;
  margin: 0 auto;
}

.heart-grid {
  border: 1px black;
  display: block;
  position: relative;
  width: 600px; /* Feste Breite */
  height: 600px; /* Feste Höhe */
}

.grid-item {
  background-color: #f9f9f9;
  border: 1px dashed #ccc;
  border-radius: 8px;
  width: 50px; /* Feste Breite */
  height: 50px; /* Feste Höhe */
  align-items: center;
  justify-content: center;
  position: absolute; /* Relativ zur .heart-grid */
  transform: none;
  margin: 10px;
}

.grid-item.dragover{
  -webkit-box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0,0,0,0);
box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0,0,0,0);
}

.grid-item:nth-child(1) { top: 10%; left: 50%; }
.grid-item:nth-child(2) { top: 5%; left: 40%; }
.grid-item:nth-child(3) { top: 0%; left: 30%; }
.grid-item:nth-child(4) { top: 5%; left: 20%; }
.grid-item:nth-child(5) { top: 10%; left: 10%; }
.grid-item:nth-child(6) { top: 20%; left: 12%; }
.grid-item:nth-child(7) { top: 30%; left: 14%; }
.grid-item:nth-child(8) { top: 40%; left: 22%; }
.grid-item:nth-child(9) { top: 50%; left: 30%; }
.grid-item:nth-child(10) { top: 60%; left: 40%; }
.grid-item:nth-child(11) { top: 70%; left: 50%; }
.grid-item:nth-child(12) { top: 10%; left: 50%; }
.grid-item:nth-child(13) { top: 5%; left: 60%; }
.grid-item:nth-child(14) { top: 0%; left: 70%; }
.grid-item:nth-child(15) { top: 5%; left: 80%; }
.grid-item:nth-child(16) { top: 10%; left: 90%; }
.grid-item:nth-child(17) { top: 20%; left: 88%; }
.grid-item:nth-child(18) { top: 30%; left: 86%; }
.grid-item:nth-child(19) { top: 40%; left: 78%; }
.grid-item:nth-child(20) { top: 50%; left: 70%; }
.grid-item:nth-child(21) { top: 60%; left: 60%; }
.grid-item:nth-child(22) { top: 70%; left: 50%; }
.grid-item:nth-child(23) { top: 0%; left: 70%; }
.grid-item:nth-child(24) { top: 25%; left: 30%; }
.grid-item:nth-child(25) { top: 15%; left: 22%; }
.grid-item:nth-child(26) { top: 15%; left: 35%; }
.grid-item:nth-child(27) { top: 15%; left: 62%; }
.grid-item:nth-child(28) { top: 15%; left: 75%; }
.grid-item:nth-child(29) { top: 22%; left: 50%; }
.grid-item:nth-child(30) { top: 35%; left: 50%; }
.grid-item:nth-child(31) { top: 49%; left: 50%; }
.grid-item:nth-child(32) { top: 40%; left: 78%; }
.grid-item:nth-child(33) { top: 40%; left: 35%; }
.grid-item:nth-child(34) { top: 38%; left: 62%; }
.grid-item:nth-child(35) { top: 27%; left: 69%; }



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
</style>
