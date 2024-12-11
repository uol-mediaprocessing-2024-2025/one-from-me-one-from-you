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

export async function fetchAndStoreComponentData(componentName, items) {
  console.log("fetchAndStoreComponentData with " + componentName);
  try {
    const response = await axios.get(`${store.apiUrl}/getArray`, {
      params: { component_name: componentName },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 200 && Array.isArray(response.data)) {
      // Sort the data by the id (the first element of each sub-array)
      const sortedData = response.data.sort((a, b) => a[0] - b[0]);

      // Update the `items` array with the fetched data
      sortedData.forEach((item, index) => {
        if (index < items.length) {
          // Check for valid file names
          const fileName = item[1];
          const isValidFileName = fileName && fileName !== '[]';

          items[index] = {
            src: isValidFileName ? `${store.apiUrl}/uploaded_images/${fileName}` : null, // Set to null if invalid
            fileName: isValidFileName ? fileName : null, // Set to null if invalid
          };
        }
      });
    } else {
      console.error(`No data found for ${componentName}:`, response.data.detail || "Unknown error");
    }
  } catch (error) {
    console.error(`Error fetching data for ${componentName}:`, error);
  }
  console.log(`Data for ${componentName}:`, items);
}

