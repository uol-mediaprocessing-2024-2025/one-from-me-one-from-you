# **One-From-Me-One-From-You**

Please use the detached3 branch.

## **Overview**

**One-From-Me-One-From-You** is a web-based **AI-powered collage tool** that allows users to create visually appealing collages by selecting a shape, uploading images, and using AI-assisted image placement. Users can manually arrange images or let the AI intelligently choose based on different selection modes.

## **Features**

- **Collage Creation**
  - Select from **predefined shapes**: Heart, Rectangle, Star, Hexagon, Cloud, Fish, Leaf, Triangle.
  - **Grid-Based UI** for easy image placement.
  - AI-assisted image selection with customizable **Image Selection Modes**:
    - **Face Detection** – Prioritizes images with faces.
    - **Visual Similarity** – Matches images based on colors and patterns.
    - **Textual Prompt** – AI selects images based on text descriptions.

- **Image Management**
  - Upload images and manage them in the **gallery**.
  - Store **uploaded images and saved collages** for later use.

- **Customization & Export**
  - Change collage **shape** and **image selection mode** dynamically.
  - **Download final collages** or **save them to the gallery** for future editing.
  - **Clear collage** option to start fresh.

## **Tech Stack**

### **Frontend**
- Vue.js, Vuex, Vue Router, Vuetify
- JavaScript, HTML, CSS
- html2canvas, axios

### **Backend**
- Python, FastAPI
- OpenCV, NumPy
- Uvicorn

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/one-from-me-one-from-you.git
cd one-from-me-one-from-you
 ```

### **2. Install Backend Dependencies**
```bash
pip install -r requirements.txt 
```

### **3. Install Frontend Dependencies**
```bash
npm install
```
### **4. Install Frontend Dependencies**
**Start the backend**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

**Start the frontend**:
    ```bash
    npm run serve
    ```

## API Endpoints

### **POST /saveImages**  
Saves the uploaded images to the server and encodes them using the CLIP model.

---

### **POST /update_image_selection_mode**  
Updates the image selection mode.

---

### **GET /getImages**  
Retrieves all image filenames in the `UPLOAD_DIR`.

---

### **GET /ping**  
Pings the server and generates a collage from the components.

---

### **POST /positions**  
Receives positions and component name, processes the data, and updates the component.

---

### **POST /new_selection**  
Sets a new selection for the specified component and target ID.

---

### **GET /getArray**  
Retrieves the array of data for a specific component.

---

### **POST /clearCollage**  
Clears the collage for the specified component.
