const uploadInput = document.getElementById('upload');
const photoGallery = document.getElementById('photo-gallery');
const collageShapesContainer = document.getElementById('collage-shapes-container');
const collagePreview = document.getElementById('collage-preview');

uploadInput.addEventListener('change', (event) => {
  const files = event.target.files;
  photoGallery.innerHTML = '';

  Array.from(files).forEach((file) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();

      reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        photoGallery.appendChild(img);
      };

      reader.readAsDataURL(file);
    }
  });
});

function loadCollageShapes() {
  const collageTemplatesPath = 'collage_templates/';
  const shapeFiles = ['heart.png', 'star.png', 'hexagon.png', 'cloud.png', 'fish.png', 'leaf.png',
    'rectangle.png', 'triangle.png'];

  shapeFiles.forEach((fileName) => {
    const img = document.createElement('img');
    img.src = `${collageTemplatesPath}${fileName}`;
    img.alt = fileName.split('.')[0];
    img.addEventListener('click', () => {
      updateCollagePreview(img.src);
    });
    collageShapesContainer.appendChild(img);
  });
}

function updateCollagePreview(imageSrc) {
  collagePreview.querySelector('img').src = imageSrc;
}

window.onload = loadCollageShapes;
