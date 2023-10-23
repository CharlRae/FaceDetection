# Libraries
import CamReader as cr
import cv2
import numpy as np

# Sub programs
def calc_sum_table(array): # SUM TABLE WORKS
    # Returns a summed-area table from a 2D array
    # Items in the list are indexed using [row][column]

    summed_table = []

    # Iterates through every row
    for i in range(len(array)):
        # Iterates through every column
        this_row = []
        for j in range(len(array[1])):
            sum_value = 0
            # Every pixel it will do the following

            # If not on the top or left edge use normal formula
            if i > 0 and j > 0:
                sum_value += this_row[j - 1] # value to left
                sum_value += summed_table[i - 1][j] # value above
                sum_value -= summed_table[i - 1][j - 1] # value to top left
                sum_value += array[i][j] # pixel value to add to it
            # If on top edge
            elif i == 0 and j > 0:
                sum_value += this_row[j - 1] # value to left
                sum_value += array[i][j] # pixel value to add to it
            # If on left edge
            elif i > 0 and j == 0:
                sum_value += summed_table[i - 1][j] # value above
                sum_value += array[i][j] # pixel value to add to it
            # If the top left pixel
            else:
                sum_value += array[i][j] # add the pixel value
        
            this_row.append(sum_value)
        summed_table.append(this_row)
    return summed_table

def segment_area(summed_table, corner_one, corner_two): # SEGMENT AREA MAY WORK, HAS IN ALL TESTING
    # Finds the sum of an area of an array defined by a rectangle where corner_two is the bottom right and corner_one
    # is the top left

    area = 0
    # array indexes flipped to represent row and column than x and y
    if corner_one[0] > 0 and corner_one[1] > 0: # CURRENTLY ONLY WORKS FOR IF BOTTOM LEFT CORNER IS NOT ON AN EDGE
        area += summed_table[corner_two[1]][corner_two[0]] # bottom right value  
        area -= summed_table[corner_two[1]][corner_one[0] - 1] # Item to left of bottom left
        area -= summed_table[corner_one[1] - 1][corner_two[0]] # Item to top of top right
        area += summed_table[corner_one[1] - 1][corner_one[0] - 1] # Item to top left of top left
    elif corner_one[0] > 0 and corner_one[1] == 0: # If top left corner is on top edge
        area += summed_table[corner_two[1]][corner_two[0]] # bottom right value
        area -= summed_table[corner_two[1]][corner_one[0] - 1] # item to left of bottom left
    elif corner_one[0] == 0 and corner_one[1] > 0: # If top left corner is on left edge
        area += summed_table[corner_two[1]][corner_two[0]] # bottom right value
        area -= summed_table[corner_one[1] - 1][corner_two[0]] # item to top of top left
    else: # top left corner is in the top left
        area = summed_table[corner_two[1]][corner_two[0]]

    return area

def image_scan(image, scan_size, threshold):
    # Finds edge features in an image
    feature_type = ''
    feature_list = []
    sum_table = calc_sum_table(image)
    increment = scan_size - 1 # Increment must be 1 less, since adding 4 to a coord will make the box 5x5
    inverse_res = image.shape
    resolution = [inverse_res[1], inverse_res[0]]
    # Set the first scan box
    box_tl = [0, 0]
    box_br = [box_tl[0] + increment, box_tl[1] + increment]
    # Move the scan box along like a grid over the image
    for row in range(resolution[1] // scan_size):
        for column in range(resolution[0] // scan_size):
            h_contrast = area_contrast(sum_table, box_tl, box_br, 'h') # compare top and bottom halves
            v_contrast = area_contrast(sum_table, box_tl, box_br, "V") # compare left and right halves

            if h_contrast >= threshold and v_contrast >= threshold:
                feature_type = 'rectangle'
            elif h_contrast >= threshold:
                feature_type = 'h_edge'
            elif v_contrast >= threshold:
                feature_type = 'v_edge'
            else:
                feature_type = 'null'

            if feature_type != 'null':
                feature_list.append([feature_type, (box_tl[0], box_tl[1]), (box_br[0], box_br[1])]) # [type, corner 1, corner 2]

            box_tl[0] = box_br[0] + 1 # move top left corner to the right 
            box_br[0] = box_tl[0] + increment # move bottom right corner to the right
        box_tl[1] = box_br[1] + 1 # move top left corner down
        box_tl[0] = 0 # move bottom right corner to left of row
        box_br[1] = box_tl[1] + increment # move bottom right corner down
        box_br[0] = box_tl[0] + increment # move bottom right corner to left of row
    return feature_list

def area_contrast(summed_table, box_tl, box_br, direction):
    # Finds the contrast between two halves of a 2D array

    if direction == 'h': # Comparing horizontal halves

        # setting the coordinates for the 2 half boxes
        scan_size = box_br[1] - box_tl[1]
        half_size = scan_size // 2
        increment = half_size - 1

        upper_tl = box_tl
        upper_br = [box_br[0], box_tl[1] + increment]

        lower_tl = [box_tl[0], box_br[1] - increment]
        lower_br = box_br

        # calculating the difference
        top_seg_area = segment_area(summed_table, upper_tl, upper_br)
        bottom_seg_area = segment_area(summed_table, lower_tl, lower_br)
        top_seg_mean = top_seg_area / (scan_size ^ 2)
        bottom_seg_mean = bottom_seg_area / (scan_size ^ 2)
        difference = abs(top_seg_mean - bottom_seg_mean)

    else: # comparing the vertical halves

        # setting the coordinates for the 2 half boxes
        scan_size = box_br[0] - box_tl[0]
        half_size = scan_size // 2
        increment = half_size - 1

        left_tl = box_tl
        left_br = [box_tl[0] + increment, box_br[1]]

        right_tl = [box_br[0] - increment, box_tl[1]]
        right_br = box_br
        # calculating the difference
        left_seg_area = segment_area(summed_table, left_tl, left_br)
        right_seg_area = segment_area(summed_table, right_tl, right_br)
        left_seg_mean = left_seg_area / (scan_size ^ 2)
        right_seg_mean = right_seg_area / (scan_size ^ 2)
        difference = abs(left_seg_mean - right_seg_mean)

    return difference

def draw_features(image, feature_list): # Takes a list of data, structured like: ['h_edge', (342, 34), (456, 79)]
    # Draws a colour coded square around each edge feature
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
        
    for feature in feature_list:
        if feature[0] == 'rectangle':
            colour = BLUE
        elif feature[0] == 'h_edge':
            colour = GREEN
        else:
            colour = RED

        image = cv2.rectangle(image, feature[1], feature[2], colour, 1)
    
    return image

def edge_detector(show_cam):
    camera = cr.CameraDevice(0)

    while True: # Main loop
        IMAGE_SIZE = (640, 480)
        IMAGE_SIZE_C = (IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
        
        # Read and format frame
        a_frame = camera.read_frame()
        a_frame = camera.resize_image(a_frame, IMAGE_SIZE)
        a_frame = camera.grayscale_image(a_frame)
        # Scan image for features
        feature_list = (image_scan(a_frame, 4, 50))
        # Change frame format back to colour to add coloured squares
        a_frame = camera.recolour_image(a_frame)

        # Show the frame
        if show_cam:
            draw_features(a_frame, feature_list)
            camera.show_image(a_frame)
        else:
            blank_image = np.zeros(IMAGE_SIZE_C, np.uint8)
            draw_features(blank_image, feature_list)
            camera.show_image(blank_image)
        
        # Magic OpenCV stuff to make the loop work
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



# Main code
edge_detector(True) # edge_detector(show_cam)