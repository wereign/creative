import cv2
import numpy as np
import random
import os




# BGR tuples for OpenCV
YELLOW = (112, 196, 255)  # OpenCV uses BGR, so (Blue, Green, Red)
RED = (70, 87, 221)

def create_negative_mask(
    width, height, num_slices=300, rect_width=4, rect_height_ratio=0.6, min_spacing=0, max_spacing=0
):
    # Step 1: Create bars (red/yellow) on black
    color_mask = np.zeros((height, width, 3), dtype=np.uint8)
    rect_height = int(height * rect_height_ratio)
    placed_rects = []
    x = 0
    while x < width:
        y = random.randint(0, height - rect_height)
        color = RED if random.random() < 0.5 else YELLOW
        cv2.rectangle(color_mask, (x, y), (x + rect_width, y + rect_height), color, -1)
        placed_rects.append((x, y, x + rect_width, y + rect_height))
        # Determine next x position
        if min_spacing == 0 and max_spacing == 0:
            x += rect_width
        else:
            x += rect_width + random.randint(min_spacing, max_spacing)
    return color_mask


def overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)


def apply_vertical_streaking(mask, num_slices=300):
    # Works for both single channel and 3 channel
    if len(mask.shape) == 2:
        height, width = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            x = random.randint(0, width - 1)
            w = random.randint(1, 5)
            y_offset = random.randint(-100, 100)
            for y in range(height):
                for dx in range(w):
                    sx = np.clip(x + dx, 0, width - 1)
                    sy = np.clip(y, 0, height - 1)
                    ty = np.clip(y + y_offset, 0, height - 1)
                    result[ty, sx] = mask[sy, sx]
        return result
    else:
        height, width, ch = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            x = random.randint(0, width - 1)
            w = random.randint(1, 5)
            y_offset = random.randint(-100, 100)
            for y in range(height):
                for dx in range(w):
                    sx = np.clip(x + dx, 0, width - 1)
                    sy = np.clip(y, 0, height - 1)
                    ty = np.clip(y + y_offset, 0, height - 1)
                    result[ty, sx, :] = mask[sy, sx, :]
        return result


def apply_horizontal_slicing(mask, num_slices=150):
    # Works for both single channel and 3 channel
    if len(mask.shape) == 2:
        height, width = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            y = random.randint(0, height - 1)
            h = random.randint(1, 5)
            x_offset = random.randint(-50, 50)
            src_y = np.clip(y, 0, height - h)
            dest_y = src_y
            slice_ = result[src_y : src_y + h, :]
            shifted = np.roll(slice_, shift=x_offset, axis=1)
            result[dest_y : dest_y + h, :] = shifted
        return result
    else:
        height, width, ch = mask.shape
        result = mask.copy()
        for _ in range(num_slices):
            y = random.randint(0, height - 1)
            h = random.randint(1, 5)
            x_offset = random.randint(-50, 50)
            src_y = np.clip(y, 0, height - h)
            dest_y = src_y
            slice_ = result[src_y : src_y + h, :, :]
            shifted = np.roll(slice_, shift=x_offset, axis=1)
            result[dest_y : dest_y + h, :, :] = shifted
        return result


def apply_mask(image, mask):
    if mask.shape != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

    mask_3ch = cv2.merge([mask, mask, mask])
    return cv2.bitwise_and(image, mask_3ch)


def main():
    image_path = "./creative.jpg"
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    # Prepare intermediates directory
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    intermediates_dir = f"{base_name}_intermediates"
    os.makedirs(intermediates_dir, exist_ok=True)



    # Step 1: Create colored bars on black
    bars_img = create_negative_mask(width, height, num_slices=250, min_spacing=8, max_spacing=32)
    cv2.imwrite(os.path.join(intermediates_dir, "step1_bars.png"), bars_img)

    # Step 2: Add vertical and horizontal distortions to bars
    bars_v = apply_vertical_streaking(bars_img)
    cv2.imwrite(os.path.join(intermediates_dir, "step2_bars_vertical.png"), bars_v)
    bars_h = apply_horizontal_slicing(bars_v)
    cv2.imwrite(os.path.join(intermediates_dir, "step3_bars_horizontal.png"), bars_h)

    # Step 3: Make this a mask where black areas are where the image is visible
    # Create mask: where all channels are 0 (black), let image show; else show bars
    mask_black = np.all(bars_h == 0, axis=2)
    result = image.copy()
    # Where not black, show bars; where black, show image
    result[~mask_black] = bars_h[~mask_black]

    cv2.imwrite("masked_output.png", result)
    print("Saved final masked image.")


if __name__ == "__main__":
    main()
