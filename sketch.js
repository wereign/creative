let img;

function preload() {
  img = loadImage("./creative.jpg"); // Make sure this path is correct
}

function applyGlitchEffect({
  minStreakWidth = 2,
  maxStreakWidth = 8,
  minStreakHeight = 0.3,
  maxStreakHeight = 1.0,
  maxVerticalOffset = 50,
  maxHorizontalOffset = 50,
  numSlices = 300
} = {}) {
  // Draw black rectangles to a buffer
  let rectBuffer = createGraphics(width, height);
  rectBuffer.noStroke();
  let expBase = random(1.05, 1.25);
  let x = 0;
  let streakCount = 0;
  while (x < width) {
    let streakHeight = random(height * minStreakHeight, height * maxStreakHeight);
    let yStart = random(-100, height);
    let step = minStreakWidth * Math.pow(expBase, streakCount);
    rectBuffer.fill(0, 0, 0, random(150, 255));
    rectBuffer.rect(x, yStart, step, streakHeight);
    x += step;
    streakCount++;
  }

  // Blur the buffer
  rectBuffer.filter(BLUR, 3);

  // Draw sharp rectangles to main canvas
  noStroke();
  x = 0;
  streakCount = 0;
  while (x < width) {
    let streakHeight = random(height * minStreakHeight, height * maxStreakHeight);
    let yStart = random(-100, height);
    let step = minStreakWidth * Math.pow(expBase, streakCount);
    fill(0, 0, 0, random(150, 255));
    rect(x, yStart, step, streakHeight);
    x += step;
    streakCount++;
  }

  // Composite only the blurred edges: subtract sharp from blurred, then draw result
  // (approximate: draw blurred buffer with low alpha on top)
  tint(255, 120); // semi-transparent
  image(rectBuffer, 0, 0);
  noTint();

  // Vertical Streaking
  loadPixels();
  for (let i = 0; i < numSlices; i++) {
    let x = floor(random(width));
    let w = floor(random(1, 5));
    let yOffset = floor(random(-maxVerticalOffset, maxVerticalOffset));
    copy(x, 0, w, height, x, yOffset, w, height);
  }

  // Horizontal Distortion
  loadPixels();
  for (let i = 0; i < numSlices / 2; i++) {
    let y = floor(random(height));
    let h = floor(random(1, 5));
    let xOffset = floor(random(-maxHorizontalOffset, maxHorizontalOffset));
    copy(0, y, width, h, xOffset, y, width, h);
  }
}

function setup() {
  createCanvas(img.width, img.height);
  image(img, 0, 0);
  // Apply Gaussian blur to the whole image
  // Call with default values, or customize as needed
  applyGlitchEffect();
  // filter(BLUR, 3); // You can adjust the blur amount
}
