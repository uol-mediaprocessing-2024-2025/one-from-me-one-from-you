import axios from 'axios';
import { store } from '@/store.js';
import { scaleImage } from "@/controller/GridComponentHelper.js";

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

export async function fetchAndStoreComponentData(componentName, items) {
  try {
    const response = await axios.get(`${store.apiUrl}/getArray`, {
      params: { component_name: componentName },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 200 && Array.isArray(response.data)) {
      const sortedData = response.data.sort((a, b) => a[0] - b[0]);

      // Use a for...of loop instead of forEach to handle async operations
      for (const [index, item] of sortedData.entries()) {
        if (index < items.length) {
          const fileName = item[1];
          const isValidFileName = fileName && fileName !== '[]';

          let imageUrl = isValidFileName ? `${store.apiUrl}/uploaded_images/${fileName}` : null;

          // If valid image URL is present, scale it
          if (imageUrl) {
            const scaledImage = await scaleImage(imageUrl);
            imageUrl = scaledImage;
          }

          // Assign scaled image URL to the item
          items[index] = {
            src: imageUrl,
            fileName: isValidFileName ? fileName : null,
          };
        }
      }
    } else {
      console.error(`No data found for ${componentName}:`, response.data.detail || "Unknown error");
    }
  } catch (error) {
    console.error(`Error fetching data for ${componentName}:`, error);
  }
}


