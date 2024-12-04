import axios from 'axios';
import { store } from '@/store.js';

export async function fetchAndStoreImages() {
  try {
    const response = await axios.get(`${store.apiUrl}/getImages`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 200 && Array.isArray(response.data.image_files)) {
      store.photoUrls = [];
      store.photoBlobs = [];

      for (const image of response.data.image_files) {
        const fullUrl = `${store.apiUrl}/uploaded_images/${image}`;
        store.photoUrls.push(fullUrl);

        const blobResponse = await axios.get(fullUrl, { responseType: 'blob' });
        store.photoBlobs.push(blobResponse.data);
      }
    } else {
      console.error("No images found:", response.data.message);
    }
  } catch (error) {
    console.error("Error fetching images:", error);
  }
}