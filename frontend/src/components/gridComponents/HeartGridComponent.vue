<script setup>
import {ref, reactive, onMounted, defineProps} from "vue";
import {useAttrs} from "vue";
import {updateCollageItems, extractGridPositions, wait} from "@/controller/GridComponentHelper.js";
import ImageSelectionModal from "@/components/ImageSelectionModal.vue";


const attrs = useAttrs();
const items = reactive(Array(34).fill({src: null, fileName: null}));
const showModal = ref(false);
const selectedIndex = ref(null);
const componentName = "heartComponent";
const isAITurn = ref(false);
const isDisabled = ref(false);

const props = defineProps({
  userPrompt: {
    type: String,
    required: true,
  },
  imageSelectionMode: {
    type: String,
    required: true,
  },
});

const localUserPrompt = ref(props.userPrompt);


onMounted(async () => {
  await updateCollageItems(componentName, items);
});

function openImageSelection(index) {
  selectedIndex.value = index;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  selectedIndex.value = null;
}

async function removePreviewImage(index) {
  items[index] = {src: null, fileName: null};
  isAITurn.value = true;
  isDisabled.value = true;

  await wait(500);
  await updateCollageItems(componentName, items);

  isAITurn.value = false;
  isDisabled.value = false;
}

async function selectImage({src, fileName}) {
  if (selectedIndex.value !== null) {
    items[selectedIndex.value] = {src, fileName};

    isAITurn.value = true;
    isDisabled.value = true;

    await wait(2000);

    const gridContainer = document.querySelector(".rectangle-grid");
    const gridItems = document.querySelectorAll(".grid-item");
    await extractGridPositions(gridContainer, gridItems, items, componentName, localUserPrompt.value);

    await updateCollageItems(componentName, items);

    isAITurn.value = false;
    isDisabled.value = false;
  }
}

function updateUserPrompt(newPrompt) {
  localUserPrompt.value = newPrompt;
  console.log("Updated userPrompt in parent:", newPrompt);
}
</script>

<template>
  <div class="rectangle-grid-container">
    <!-- Popup AI thinking -->

    <div v-if="isAITurn" class="popup">

      <img src="../../assets/whatsnext.png" height="100" width="100"/>
      <v-progress-linear
          color="teal"
          indeterminate
          rounded
          buffer-value="10000"
          stream
      ></v-progress-linear>
      <br>
      Let me think about that...
    </div>

    <div class="rectangle-grid" v-bind="attrs">
      <div
          v-for="(item, index) in items"
          :key="index"
          class="grid-item"
          :class="{ disabled: isDisabled }">
        <!-- Show image if selected -->
        <label
            v-if="!item.src"
            class="upload-label"
            @click="!isDisabled && openImageSelection(index)"
        >
          + Select Image
        </label>
        <div v-else class="image-container">
          <img :src="item.src" alt="Bild"/>
          <button class="remove-button" @click="removePreviewImage(index)">X</button>
        </div>
      </div>
    </div>
  </div>

  <ImageSelectionModal
      :showModal="showModal"
      :selectedIndex="selectedIndex"
      :imageSelectionMode="imageSelectionMode"
      :userPrompt="localUserPrompt"
      @close-modal="closeModal"
      @select-image="selectImage"
      @update:userPrompt="updateUserPrompt"/>
</template>

<style scoped>
.rectangle-grid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  width: 1000px;
  height: 800px;
  margin: 0 auto;
}

.rectangle-grid {
  border: 1px black;
  display: block;
  position: relative;
  width: 1000px;
  height: 800px;
}

.grid-item {
  background-color: #f9f9f9;
  border: 1px dashed #ccc;
  border-radius: 8px;
  width: 80px;
  height: 80px;
  align-items: center;
  justify-content: center;
  position: absolute;
  transform: none;
  margin: 10px;
  overflow: visible;
}

.grid-item.disabled {
  pointer-events: none;
  opacity: 0.6;
  cursor: not-allowed;
}

.grid-item.dragover {
  -webkit-box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0, 0, 0, 0);
  box-shadow: 5px 5px 15px 5px #FF8080, -9px 5px 15px 5px #FFE488, -7px -5px 15px 5px #8CFF85, 12px -5px 15px 5px #80C7FF, 12px 10px 15px 7px #E488FF, -10px 10px 15px 7px #FF616B, -10px -7px 27px 1px #8E5CFF, 5px 5px 15px 5px rgba(0, 0, 0, 0);
}

.grid-item img {
  transform: scale(1.05);
  transform-origin: center center;
}

.grid-item:nth-child(1) {
  top: 70%;
  left: 50%;
}

.grid-item:nth-child(2) {
  top: 30%;
  left: 50%;
}

.grid-item:nth-child(3) {
  top: 40%;
  left: 50%;
}

.grid-item:nth-child(4) {
  top: 50%;
  left: 50%;
}

.grid-item:nth-child(5) {
  top: 60%;
  left: 50%;
}

.grid-item:nth-child(6) {
  top: 20%;
  left: 40%;
}

.grid-item:nth-child(7) {
  top: 30%;
  left: 40%;
}

.grid-item:nth-child(8) {
  top: 40%;
  left: 40%;
}

.grid-item:nth-child(9) {
  top: 50%;
  left: 40%;
}

.grid-item:nth-child(10) {
  top: 60%;
  left: 40%;
}

.grid-item:nth-child(12) {
  top: 20%;
  left: 60%;
}

.grid-item:nth-child(13) {
  top: 30%;
  left: 60%;
}

.grid-item:nth-child(14) {
  top: 40%;
  left: 60%;
}

.grid-item:nth-child(15) {
  top: 50%;
  left: 60%;
}

.grid-item:nth-child(16) {
  top: 60%;
  left: 60%;
}

.grid-item:nth-child(17) {
  top: 20%;
  left: 30%;
}

.grid-item:nth-child(18) {
  top: 30%;
  left: 30%;
}

.grid-item:nth-child(19) {
  top: 40%;
  left: 30%;
}

.grid-item:nth-child(20) {
  top: 50%;
  left: 30%;
}

.grid-item:nth-child(21) {
  top: 10%;
  left: 30%;
}

.grid-item:nth-child(22) {
  top: 20%;
  left: 70%;
}

.grid-item:nth-child(23) {
  top: 30%;
  left: 70%;
}

.grid-item:nth-child(24) {
  top: 40%;
  left: 70%;
}

.grid-item:nth-child(25) {
  top: 50%;
  left: 70%;
}

.grid-item:nth-child(26) {
  top: 10%;
  left: 70%;
}

.grid-item:nth-child(27) {
  top: 20%;
  left: 20%;
}

.grid-item:nth-child(28) {
  top: 30%;
  left: 20%;
}

.grid-item:nth-child(29) {
  top: 40%;
  left: 20%;
}

.grid-item:nth-child(30) {
  top: 20%;
  left: 80%;
}

.grid-item:nth-child(31) {
  top: 30%;
  left: 80%;
}

.grid-item:nth-child(32) {
  top: 40%;
  left: 80%;
}

.grid-item:nth-child(33) {
  top: 30%;
  left: 10%;
}

.grid-item:nth-child(11) {
  top: 30%;
  left: 90%;
}

.grid-item:nth-child(34) {
  top: 80%;
  left: 50%;
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

.popup {
  position: absolute;
  top: calc(50% + 222px);
  left: calc(50% + 300px);
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 40px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  z-index: 2;
  width: 300px;
}

.rectangle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.remove-button {
  position: absolute;
  top: -1px;
  right: -1px;
  background-color: red;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  text-align: center;
  cursor: pointer;
  font-size: 14px;
  line-height: 18px;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.remove-button:hover {
  background-color: darkred;
}

</style>
