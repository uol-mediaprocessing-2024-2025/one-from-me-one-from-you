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

    // Check if the response status is OK and image_files exist
    if (response.status === 200 && Array.isArray(response.data.image_files)) {
      store.photoUrls = [];
      store.photoBlobs = [];

      for (const image of response.data.image_files) {
        const fullUrl = `${store.apiUrl}/uploaded_images/${image}`;
        store.photoUrls.push(fullUrl);

        // Fetch the blob for each image
        try {
          const blobResponse = await axios.get(fullUrl, { responseType: 'blob' });
          store.photoBlobs.push(blobResponse.data);
        } catch (blobError) {
          console.error(`Failed to fetch blob for image: ${fullUrl}`, blobError);
          // Optionally, you can skip the blob or store an error placeholder
          store.photoBlobs.push(null); // Placeholder for the failed blob
        }
      }
    } else {
      console.error("No images found or invalid response format:", response.data.message);
    }
  } catch (error) {
    // Handle specific HTTP errors
    if (error.response) {
      const statusCode = error.response.status;
      if (statusCode === 404) {
        console.error("Error: The requested resource was not found (404).");
      } else {
        console.error(`Error: HTTP status ${statusCode} returned from the server.`);
      }
    } else if (error.request) {
      // Network errors or no response from the server
      console.error("Error: No response from the server. Check if the server is running and reachable.");
    } else {
      // Other errors (e.g., invalid request configuration)
      console.error("Error: Something went wrong with the request setup:", error.message);
    }
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

      for (const [index, item] of sortedData.entries()) {
        if (index < items.length) {
          const fileName = item[1];
          const isValidFileName = fileName && fileName !== '[]';

          let imageUrl = isValidFileName ? `${store.apiUrl}/uploaded_images/${fileName}` : null;

          if (imageUrl) {
            const scaledImage = await scaleImage(imageUrl);
            imageUrl = scaledImage;
          }

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


