import os
import csv
import cv2
import numpy as np
from PIL import Image

def check_image_size_and_similarity(correct_image_paths, student_image_path, output_folder):
    similarity_results = []
    
    for correct_image_path in correct_image_paths:
        correct_image = Image.open(correct_image_path)
        correct_width, correct_height = correct_image.size

        student_image = Image.open(student_image_path)
        student_width, student_height = student_image.size
        threshold = 95.00

        if (student_width, student_height) == (correct_width, correct_height):
            similarity_percentage = calculate_similarity_by_SIFT(correct_image_path, student_image_path)
            similarity_results.append({'Image': os.path.basename(student_image_path), 'Similarity (%)': similarity_percentage, 'Remark': similarity_percentage})
        else:
            similarity_percentage = calculate_similarity_by_ORB(correct_image_path, student_image_path)
            if similarity_percentage >= threshold:
                similarity_results.append({'Image': os.path.basename(student_image_path), 'Similarity (%)': similarity_percentage, 'Remark': 100.00})
            else:
                similarity_results.append({'Image': os.path.basename(student_image_path), 'Similarity (%)': similarity_percentage, 'Remark': similarity_percentage})

    similarity_results.sort(key=lambda x: x['Similarity (%)'], reverse=True)
    output_csv_path = os.path.join(output_folder, 'similarity_results.csv')

    write_header = not os.path.isfile(output_csv_path)
    with open(output_csv_path, 'a', newline='') as csvfile:
        fieldnames = ['Image', 'Similarity (%)', 'Remark']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        for result in similarity_results:
            writer.writerow({'Image': result['Image'], 'Similarity (%)': f"{result['Similarity (%)']:.2f}", 'Remark': f"{result['Remark']:.2f}"})

    correct_image_path_for_highlight = correct_image_paths[0]  # You may choose the correct image to highlight differences
    highlight_image_path = highlight_image_difference(correct_image_path_for_highlight, student_image_path, output_folder)

    return {'highlight_image_path': highlight_image_path}

def calculate_similarity_by_SIFT(image1_path, image2_path):
    image1 = cv2.imread(image1_path, cv2.IMREAD_COLOR)
    image2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)
    
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(image1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(image2, None)

    flann = cv2.FlannBasedMatcher_create()
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    similarity = len(good_matches) / max(len(keypoints1), len(keypoints2)) * 100
    return similarity

def resize_image(image, target_width, target_height):
    return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)

def calculate_similarity_by_ORB(image1_path, image2_path):
    image1 = cv2.imread(image1_path, cv2.IMREAD_COLOR)
    image2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)
    target_width = 700
    target_height = 550
    
    image1_resized = resize_image(image1, target_width, target_height)
    image2_resized = resize_image(image2, target_width, target_height)
    
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(image1_resized, None)
    keypoints2, descriptors2 = orb.detectAndCompute(image2_resized, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    similarity = len(matches) / max(len(keypoints1), len(keypoints2)) * 100
    return similarity

def highlight_image_difference(image1_path, image2_path, output_folder):
    org_img = image1_path
    correct_image = Image.open(image1_path)
    correct_width, correct_height = correct_image.size
    
    original_image1 = cv2.imread(image1_path)
    student_image = Image.open(image2_path)
    student_width, student_height = student_image.size

    if (student_width, student_height) == (correct_width, correct_height):
        image2 = cv2.imread(image2_path)
        difference = cv2.absdiff(original_image1, image2)
    else:
        image1 = cv2.imread(org_img, cv2.IMREAD_COLOR)
        image2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)
        target_width = 700
        target_height = 550
        
        resize_image1 = resize_image(image1, target_width, target_height)
        resize_image2 = resize_image(image2, target_width, target_height)
        cv2.imwrite(image2_path, resize_image2)
        
        image2 = cv2.imread(image2_path)
        difference = cv2.absdiff(resize_image1, image2)

    gray_difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_difference, 30, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    highlighted_image = image2.copy()
    highlighted_image[mask != 0] = [0, 0, 255]

    alpha = 0.3
    result = cv2.addWeighted(image2, 1-alpha, highlighted_image, alpha, 0)

    # highlight the differences with a red border and display a message indicating whether differences were found.
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 4)  # Increased thickness to 4

    if contours:
        message = "Differences Found"
        text_color = (0, 0, 255)
    else:
        message = "No Differences Found"
        text_color = (0, 255, 0)

    # Get the image dimensions
    height, width = result.shape[:2]
    # Calculate the text size to center it
    text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (width - text_size[0]) // 2
    text_y = 30

    cv2.putText(result, message, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)

    output_path_name = os.path.join(output_folder, os.path.basename(image2_path))
    cv2.imwrite(output_path_name, result)
    
    return output_path_name
