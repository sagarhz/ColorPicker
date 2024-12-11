import cv2
import numpy as np
import math

# Dominant colors in the Environemtn
def get_dominant_colors(image, n_colors=3):
    pixels = cv2.resize(image, (64, 64)).reshape(-1, 3)
    pixels = np.float32(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    
    # Number of pixels
    _, counts = np.unique(labels, return_counts=True)
    return palette[np.argsort(-counts)].astype(np.uint8)


# Smooth color  with dynamic blend
def create_color_field(colors, width, height, t):
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
# Sin wave patterns
    color_field = np.zeros((height, width, 3), dtype=np.float32)
    for i, color in enumerate(colors):
        phase_x = math.sin(t * 0.2 + i * 2 * math.pi / len(colors))
        phase_y = math.cos(t * 0.2 + i * 2 * math.pi / len(colors))
        wave = np.sin(2 * np.pi * (xx * phase_x + yy * phase_y) + t * 0.2) * 0.5 + 0.5
        color_field += np.outer(wave, color).reshape(height, width, 3)
    
    color_field = color_field / np.max(color_field)
    color_field = np.power(color_field, 0.7)
    
    return (color_field * 255).astype(np.uint8)


# RGB color info
def add_color_info(image, colors):
    h, w = image.shape[:2]
    info_height = 80
    info_image = np.zeros((h + info_height, w, 3), dtype=np.uint8)
    info_image[:h, :w] = image
    
    square_size = 60
    start_x = 10
    start_y = h + 10
    
    for i, color in enumerate(colors):
        cv2.rectangle(info_image, (start_x, start_y), (start_x + square_size, start_y + square_size), color.tolist(), -1)
        cv2.putText(info_image, f"RGB: {color[2]},{color[1]},{color[0]}", (start_x + square_size + 5, start_y + 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        start_x += square_size + 180
    
    return info_image

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Cannot open camera")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    _, frame = cap.read()
    height, width = frame.shape[:2]
    
    current_colors = np.zeros((3, 3), dtype=np.float32)
    t = 0

# Window    
    window_name = 'Blending Color Mood'
    cv2.namedWindow(window_name)

# Webcam    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame. Exiting ...")
            break

        dominant_colors = get_dominant_colors(frame, n_colors=3)
        
        current_colors = current_colors * 0.8 + dominant_colors * 0.2
        
        color_mood = create_color_field(current_colors.astype(np.uint8), width, height, t)
        color_mood = cv2.GaussianBlur(color_mood, (15, 15), 0)
        
        display_image = add_color_info(color_mood, dominant_colors)
        
        cv2.imshow(window_name, display_image)
        
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        t += 0.1

# Close     
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("Press Enter to exit...")
    input()