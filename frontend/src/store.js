// Import the reactive and ref functions from Vue
import { reactive } from 'vue';

// Define a reactive store to manage global state across the app
export const store = reactive({
    photoUrls: [],
    photoBlobs: [],
    apiUrl: 'http://localhost:8000',
    selectedImage: null,
});
