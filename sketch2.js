
let canvasW = 512;
let canvasH = 791;
let img;

function preload() {
  img = loadImage("./creative.jpg");
}

function setup() {

  createCanvas(canvasW, canvasH);
  noStroke();
  background(0); // The whole image is black by default

  // Create a mask buffer for rectangles
  let maskBuffer = createGraphics(width, height);
  maskBuffer.noStroke();
  maskBuffer.background(0);
  for (let x = 0; x < width; x += random(2, 8)) {
    let streakHeight = random(height * 0.3, height);
    let yStart = random(-100, height);
    maskBuffer.fill(255);
    maskBuffer.rect(x, yStart, random(1, 4), streakHeight);
  }

  // Use the rectangles as a mask to reveal the image only through them
  let imgMasked = createImage(width, height);
  imgMasked.copy(img, 0, 0, img.width, img.height, 0, 0, width, height);
  imgMasked.mask(maskBuffer);
  image(imgMasked, 0, 0);

  // Horizontal slice distortions
  for (let i = 0; i < 100; i++) {
    let sliceY = floor(random(height));
    let sliceH = floor(random(4, 20));
    let offsetX = floor(random(-40, 40));
    copy(0, sliceY, width, sliceH, offsetX, sliceY, width, sliceH);
  }

  // Vertical distortions (stutter effect)
  for (let i = 0; i < 100; i++) {
    let sliceX = floor(random(width));
    let sliceW = floor(random(2, 10));
    let offsetY = floor(random(-100, 100));
    copy(sliceX, 0, sliceW, height, sliceX, offsetY, sliceW, height);
  }
}
