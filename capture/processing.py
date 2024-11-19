import cv2
import numpy as np
import pyautogui

class ImageReadError(Exception):
    """Exception raised when the image could not be read."""
    pass

class NoContoursDetectedError(Exception):
    """Exception raised when no contours are detected in the image."""
    pass

class ContourCalculationError(Exception):
    """Exception raised when contour moments calculation fails."""
    pass

def find_largest_spot_by_color(image, rgb_color):
    lower_color_bound = np.maximum(rgb_color - 10, 0)
    upper_color_bound = np.minimum(rgb_color + 10, 255)
    mask = cv2.inRange(image, lower_color_bound, upper_color_bound)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise NoContoursDetectedError("No contours found in the image for the specified color range.")
    
    largest_contour = max(contours, key=cv2.contourArea)
    
    moments = cv2.moments(largest_contour)
    if moments["m00"] == 0:
        raise ContourCalculationError("Zero division error in contour moments calculation")
        
    centroid_x = int(moments["m10"] / moments["m00"])
    centroid_y = int(moments["m01"] / moments["m00"]) 

    return (centroid_x, centroid_y)

def click_on_color_spot(image_path):
    (x_cord, y_cord) = find_colors_in_photo(image_path)
    pyautogui.click(x_cord, y_cord)

def find_colors_in_photo(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if image is None:
        raise ImageReadError(f"Failed to read image from the path: {image_path}")
    
    (image_height, image_width) = image.shape[:2]
    (width_scale, height_scale) = calculate_scale([image_width, image_height], pyautogui.size())

    colors = [
        np.array([182, 86, 238]), # Purple
        np.array([57, 190, 86]), # Green
        np.array([248, 65, 58]), # Red
        np.array([44, 127, 255]), # Blue
        np.array([253, 128, 31]), # Orange    
    ]
    centroid_coordinates = None
    for color in colors:
        try:
            centroid_coordinates = find_largest_spot_by_color(image, color) 
            if centroid_coordinates is not None:
                print(f"Contur found for specified color: {color} - {centroid_coordinates}")
                (coordinates_width, coordinates_height) = centroid_coordinates
                centroid_coordinates = (width_scale * coordinates_width, height_scale * coordinates_height)
                print(f"Fixed coordinates: {centroid_coordinates}")
                break
        except NoContoursDetectedError:
            print(f"No conturs found for specified color: {color}")
        except ContourCalculationError:
            print(f"Contour calculation error for specified color: {color}")

    return centroid_coordinates

def calculate_scale(original_size, target_size):
    width_scale = target_size[0] / original_size[0]
    height_scale = target_size[1] / original_size[1]
    return (width_scale, height_scale)
    