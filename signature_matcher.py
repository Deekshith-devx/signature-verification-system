import cv2
import numpy as np
import os

def calculate_ssim(img1, img2):
    """
    Calculate Structural Similarity Index (SSIM) between two grayscale images.
    Returns a float in range [-1, 1].
    """
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    
    mu1 = np.mean(img1)
    mu2 = np.mean(img2)
    
    var1 = np.var(img1)
    var2 = np.var(img2)
    
    covar = np.mean((img1 - mu1) * (img2 - mu2))
    
    # Constants to stabilize division
    # L = 255 (dynamic range of 8-bit grayscale image)
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    
    num = (2 * mu1 * mu2 + c1) * (2 * covar + c2)
    den = (mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)
    
    return num / den

def preprocess_signature(img_path):
    """
    Reads an image, converts it to grayscale, binarizes it,
    crops it to the signature bounding box, and returns the preprocessed image.
    """
    # Read image in grayscale
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image from path: {img_path}")
        
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Binarize using Otsu's thresholding
    # Assuming signature is dark on light background.
    # We invert the binary image so that signature is white (255) and background is black (0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find all non-zero pixels (the signature strokes)
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        # Get bounding box of the signature
        x, y, w, h = cv2.boundingRect(coords)
        # Crop the image to the signature area with a small padding
        padding = 10
        y_start = max(0, y - padding)
        y_end = min(img.shape[0], y + h + padding)
        x_start = max(0, x - padding)
        x_end = min(img.shape[1], x + w + padding)
        
        # Crop from the grayscale image
        cropped = img[y_start:y_end, x_start:x_end]
    else:
        # If no signature detected (blank page), just return the original grayscale
        cropped = img
        
    # Resize to a standard size for comparison
    standard_size = (300, 150)
    resized = cv2.resize(cropped, standard_size, interpolation=cv2.INTER_AREA)
    
    return resized

def compare_signatures(ref_path, query_path, debug_out_path=None):
    """
    Compares query signature with the reference signature.
    Returns a tuple (match_percentage, is_match, details)
    """
    try:
        # Preprocess both images
        ref_proc = preprocess_signature(ref_path)
        query_proc = preprocess_signature(query_path)
        
        # 1. Calculate SSIM
        ssim_val = calculate_ssim(ref_proc, query_proc)
        # Convert SSIM range [-1, 1] to [0, 100]
        ssim_score = max(0.0, (ssim_val + 1.0) / 2.0) * 100.0
        
        # 2. Normalized Cross-Correlation (Template Matching style similarity)
        res = cv2.matchTemplate(ref_proc, query_proc, cv2.TM_CCOEFF_NORMED)
        ncc_score = max(0.0, res[0][0]) * 100.0
        
        # 3. ORB Feature Matching
        orb = cv2.ORB_create(nfeatures=500)
        kp1, des1 = orb.detectAndCompute(ref_proc, None)
        kp2, des2 = orb.detectAndCompute(query_proc, None)
        
        orb_score = 0.0
        good_matches = []
        
        if des1 is not None and des2 is not None:
            # Match descriptors using BFMatcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            
            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Keep good matches
            good_matches = [m for m in matches if m.distance < 45]
            
            # Calculate match ratio relative to the maximum possible matches
            max_possible_matches = min(len(kp1), len(kp2), 15)
            if max_possible_matches > 0:
                orb_score = min(100.0, (len(good_matches) / max_possible_matches) * 100.0)
        
        # Combined score calculation
        # SSIM captures structural similarity, NCC captures pixel alignment, ORB captures invariant keypoints.
        # Combined score is a weighted average: 40% SSIM, 30% NCC, 30% ORB
        combined_score = (0.4 * ssim_score) + (0.3 * ncc_score) + (0.3 * orb_score)
        
        # Determine match status
        # A threshold of 70% is generally good for signatures
        threshold = 70.0
        is_match = combined_score >= threshold
        
        # Create visual comparison if debug path is provided
        if debug_out_path:
            create_comparison_image(ref_proc, query_proc, kp1, kp2, good_matches, debug_out_path)
            
        details = {
            "ssim_score": round(float(ssim_score), 2),
            "ncc_score": round(float(ncc_score), 2),
            "orb_score": round(float(orb_score), 2),
            "combined_score": round(float(combined_score), 2),
            "keypoints_detected": {
                "reference": int(len(kp1)) if kp1 else 0,
                "query": int(len(kp2)) if kp2 else 0
            },
            "good_matches_count": int(len(good_matches))
        }
        
        return float(combined_score), bool(is_match), details
        
    except Exception as e:
        print(f"Error comparing signatures: {e}")
        return 0.0, False, {"error": str(e)}

def create_comparison_image(img1, img2, kp1, kp2, matches, out_path):
    """
    Generates an image showing the reference and query signatures side-by-side
    with keypoint matches drawn as lines, and saves it.
    """
    # If there are descriptors and matches, draw keypoint matches
    if len(matches) > 0 and kp1 and kp2:
        # Draw top 15 matches to keep it clean and beautiful
        matches_to_draw = matches[:15]
        comparison_img = cv2.drawMatches(
            img1, kp1, 
            img2, kp2, 
            matches_to_draw, None, 
            matchColor=(0, 255, 0), # green lines
            singlePointColor=(0, 0, 255), # red keypoints
            flags=cv2.DrawMatchesFlags_DEFAULT
        )
    else:
        # Just stack them horizontally if no matches
        comparison_img = np.hstack((img1, img2))
        comparison_img = cv2.cvtColor(comparison_img, cv2.COLOR_GRAY2BGR)
        
    # Save the output image
    cv2.imwrite(out_path, comparison_img)
