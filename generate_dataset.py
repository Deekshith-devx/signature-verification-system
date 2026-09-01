import os
import csv
import random
import math
from PIL import Image, ImageDraw

def draw_signature_john_doe(draw):
    # J. Doe signature (looping, curves, long tail, underline)
    # Draw 'J'
    points_j = [(50, 100), (60, 60), (90, 50), (80, 120), (50, 160), (35, 150), (45, 120), (80, 100)]
    draw.line(points_j, fill="navy", width=3, joint="round")
    
    # Draw 'D'
    points_d = [(100, 120), (105, 70), (125, 60), (140, 80), (135, 110), (115, 120), (105, 115)]
    draw.line(points_d, fill="navy", width=3, joint="round")
    
    # Draw 'o' and 'e' with cursive connectors
    points_oe = [(135, 110), (145, 100), (155, 102), (150, 112), (142, 108), 
                 (160, 102), (170, 98), (175, 108), (165, 110), (185, 95), (250, 95)]
    draw.line(points_oe, fill="navy", width=3, joint="round")
    
    # Draw long swirly tail/underline
    points_underline = [(240, 95), (200, 140), (80, 150), (60, 150), (120, 142), (280, 135), (320, 130)]
    draw.line(points_underline, fill="navy", width=3, joint="round")

def draw_signature_alice_smith(draw):
    # A. Smith (sharp, elegant, angular cursive)
    # Draw 'A'
    points_a = [(60, 150), (90, 50), (110, 145), (80, 105), (120, 100)]
    draw.line(points_a, fill="black", width=3, joint="round")
    
    # Draw 'S'
    points_s = [(140, 120), (150, 75), (170, 70), (165, 95), (145, 110), (175, 125), (190, 115)]
    draw.line(points_s, fill="black", width=3, joint="round")
    
    # Draw 'm', 'i', 't', 'h' angularly
    points_mith = [(190, 115), (200, 100), (205, 115), (210, 100), (215, 115), # m
                   (225, 100), (230, 115), # i
                   (240, 80), (245, 115), # t
                   (255, 75), (258, 115), (265, 100), (275, 115), (300, 110)] # h
    draw.line(points_mith, fill="black", width=3, joint="round")
    
    # Cross the 't'
    draw.line([(232, 90), (252, 90)], fill="black", width=3)
    # Dot the 'i'
    draw.ellipse([(223, 85), (227, 89)], fill="black")

def draw_signature_robert_lee(draw):
    # R. Lee (simple text, quick scribble, dots)
    # Draw 'R'
    points_r = [(70, 130), (75, 65), (95, 60), (110, 75), (95, 90), (75, 92), (105, 130), (125, 125)]
    draw.line(points_r, fill="darkblue", width=3, joint="round")
    
    # Draw 'L'
    points_l = [(150, 60), (145, 120), (180, 125), (190, 120)]
    draw.line(points_l, fill="darkblue", width=3, joint="round")
    
    # Draw 'ee' loop
    points_ee = [(180, 125), (190, 110), (195, 125), (205, 110), (210, 125), (240, 120)]
    draw.line(points_ee, fill="darkblue", width=3, joint="round")
    
    # Add a slash and double dot at the end
    draw.line([(245, 130), (260, 110)], fill="darkblue", width=3)
    draw.ellipse([(268, 120), (272, 124)], fill="darkblue")
    draw.ellipse([(278, 120), (282, 124)], fill="darkblue")

def generate_variation(draw_func, filename, noise_level=5):
    # Create image with white background
    img = Image.new("RGBA", (400, 200), "white")
    draw = ImageDraw.Draw(img)
    
    # Wrapper around draw to add small random offsets to simulate human signing variance
    class DistortingDraw:
        def __init__(self, base_draw):
            self.base_draw = base_draw
            
        def line(self, points, fill, width, joint=None):
            distorted = []
            for pt in points:
                dx = random.uniform(-noise_level, noise_level)
                dy = random.uniform(-noise_level, noise_level)
                distorted.append((pt[0] + dx, pt[1] + dy))
            self.base_draw.line(distorted, fill=fill, width=width, joint=joint)
            
        def ellipse(self, xy, fill):
            dx = random.uniform(-noise_level, noise_level)
            dy = random.uniform(-noise_level, noise_level)
            new_xy = [(xy[0][0] + dx, xy[0][1] + dy), (xy[1][0] + dx, xy[1][1] + dy)]
            self.base_draw.ellipse(new_xy, fill=fill)

    draw_func(DistortingDraw(draw))
    
    # Convert to RGB (remove Alpha)
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3]) # paste using alpha channel
    rgb_img.save(filename, "PNG")

def main():
    print("Generating signature dataset...")
    
    # Create directories
    os.makedirs("database/signatures", exist_ok=True)
    os.makedirs("test_signatures", exist_ok=True)
    
    users = [
        {"id": "23456", "name": "John Doe", "draw": draw_signature_john_doe},
        {"id": "78901", "name": "Alice Smith", "draw": draw_signature_alice_smith},
        {"id": "11223", "name": "Robert Lee", "draw": draw_signature_robert_lee}
    ]
    
    # Generate reference and test images
    csv_rows = []
    for user in users:
        uid = user["id"]
        draw_func = user["draw"]
        
        # 1. Reference image (used in the database)
        ref_path = f"database/signatures/{uid}.png"
        generate_variation(draw_func, ref_path, noise_level=0) # no noise for base reference
        print(f"Created reference signature for {user['name']} at {ref_path}")
        
        # 2. Correct signature test image (simulates the user signing again with slight variation)
        correct_path = f"test_signatures/{uid}_correct.png"
        generate_variation(draw_func, correct_path, noise_level=3) # small noise
        print(f"Created matching test signature at {correct_path}")
        
        # 3. Forged/Incorrect signature test image (uses another user's signature styled drawing but saved as this ID's wrong signature)
        # We will use another user's drawing function
        other_user = random.choice([u for u in users if u["id"] != uid])
        wrong_path = f"test_signatures/{uid}_wrong.png"
        generate_variation(other_user["draw"], wrong_path, noise_level=4)
        print(f"Created mismatching test signature at {wrong_path}")
        
        csv_rows.append({
            "id": uid,
            "name": user["name"],
            "signature_path": ref_path
        })
        
    # Write CSV
    csv_file = "database/signatures.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "signature_path"])
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"Dataset CSV successfully created at {csv_file}")
    print("Dataset generation complete!")

if __name__ == "__main__":
    main()
