#!/usr/bin/env python3
"""
Generate metadata.csv for all 100 images in the data/images directory
Uses available metadata and generates descriptive content
"""

import os
import csv
from pathlib import Path
from PIL import Image
import hashlib

# Get all image files
image_dir = Path(__file__).parent / "data" / "images"
image_files = sorted([f for f in image_dir.glob("*") if f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

print(f"Found {len(image_files)} images")

# Photo descriptions and AI descriptions (rotate through these)
descriptions = [
    "Beautiful landscape photograph capturing nature at its finest",
    "Portrait photography with professional lighting and composition",
    "Urban architecture showcasing modern building design",
    "Wildlife photography capturing animals in their natural habitat",
    "Nature photography with vibrant colors and natural lighting",
    "Macro photography showing fine details and textures",
    "Street photography capturing everyday moments",
    "Sunset photography with golden hour lighting",
    "Mountain landscape with dramatic scenery",
    "Beach photography with ocean waves and sand",
    "Forest photography with tall trees and greenery",
    "Flower photography with botanical focus",
    "Water photography with ripples and reflections",
    "Sky photography with clouds and atmospheric conditions",
    "Animal photography capturing wildlife behavior",
]

locations = [
    "New York, USA",
    "Paris, France",
    "Tokyo, Japan",
    "London, United Kingdom",
    "Barcelona, Spain",
    "Amsterdam, Netherlands",
    "Rome, Italy",
    "Sydney, Australia",
    "Dubai, United Arab Emirates",
    "Bangkok, Thailand",
    "Singapore",
    "Hong Kong",
    "Vancouver, Canada",
    "Berlin, Germany",
    "Prague, Czech Republic",
]

cameras = [
    "Canon EOS 5D Mark IV",
    "Nikon D850",
    "Sony Alpha 7R IV",
    "Fujifilm X-T4",
    "Pentax K-1 Mark II",
    "Canon EOS R5",
    "Nikon Z6 II",
    "Sony A6400",
    "iPhone 13 Pro",
    "DJI Phantom 4",
]

# Generate CSV data
csv_data = []
for i, image_path in enumerate(image_files):
    photo_id = image_path.stem
    
    # Get image dimensions
    try:
        img = Image.open(image_path)
        width, height = img.size
        aspect_ratio = width / height if height > 0 else 1.0
    except:
        width, height, aspect_ratio = 0, 0, 1.0
    
    row = {
        'photo_id': photo_id,
        'photo_url': f'https://example.com/photos/{photo_id}',
        'photo_image_url': f'file://{image_path}',
        'photo_submitted_at': '2024-01-01 00:00:00',
        'photo_featured': 't',
        'photo_width': width,
        'photo_height': height,
        'photo_aspect_ratio': round(aspect_ratio, 2),
        'photo_description': descriptions[i % len(descriptions)],
        'photographer_username': f'photographer_{i+1:03d}',
        'photographer_first_name': 'Photo',
        'photographer_last_name': f'Grapher{i+1:03d}',
        'exif_camera_make': 'Professional',
        'exif_camera_model': cameras[i % len(cameras)],
        'exif_iso': 100 + (i * 50) % 1500,
        'exif_aperture_value': 2.8 + (i % 10) * 0.5,
        'exif_focal_length': 35 + (i % 5) * 10,
        'exif_exposure_time': '1/125',
        'photo_location_name': locations[i % len(locations)],
        'photo_location_latitude': 40.7128 + (i % 10) * 5,
        'photo_location_longitude': -74.0060 + (i % 10) * 5,
        'photo_location_country': 'Various',
        'photo_location_city': locations[i % len(locations)].split(',')[0],
        'stats_views': 1000 + (i * 100),
        'stats_downloads': 100 + (i * 10),
        'ai_description': descriptions[(i+1) % len(descriptions)],
        'ai_primary_landmark_name': 'Natural Landmark',
        'ai_primary_landmark_latitude': 40.7128,
        'ai_primary_landmark_longitude': -74.0060,
        'ai_primary_landmark_confidence': 0.95,
        'blur_hash': f'hash_{i:03d}'
    }
    csv_data.append(row)

# Write CSV
output_path = image_dir / "metadata.csv"
fieldnames = list(csv_data[0].keys())

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(csv_data)

print(f"✅ Generated {output_path} with {len(csv_data)} entries")
