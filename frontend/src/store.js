import { reactive } from 'vue';

export const store = reactive({
    photoUrls: [],
    photoBlobs: [],
    galleryBlobs: [],
    apiUrl: 'http://localhost:8000'
});
