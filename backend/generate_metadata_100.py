#!/usr/bin/env python3
"""
Generate metadata for 100 images based on existing 18 in metadata.csv
"""
import os
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Image directory
IMG_DIR = Path("/home/mad/social-recommender/backend/data/images")
METADATA_FILE = Path("/home/mad/social-recommender/backend/data/images/metadata.csv")

# Get all image IDs from directory
all_image_ids = set()
for img_file in IMG_DIR.glob("*.jpg"):
    img_id = img_file.stem
    if img_id != "metadata":  # Skip metadata files
        all_image_ids.add(img_id)

print(f"Found {len(all_image_ids)} images in directory")

# Read existing image IDs from metadata.csv
existing_ids = set()
existing_rows = []
if METADATA_FILE.exists():
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            existing_ids.add(row['photo_id'])
            existing_rows.append(row)

print(f"Found {len(existing_ids)} images in metadata.csv")

# Find new images
new_ids = sorted(all_image_ids - existing_ids)
print(f"New images to add: {len(new_ids)}")
print(f"First 10 new IDs: {new_ids[:10]}")

# Sample photographers and locations
photographers = [
    ("anthonydam", "Anthony", "Dam"),
    ("anniespratt", "Annie", "Spratt"),
    ("davidclode", "David", "Clode"),
    ("eberhard_grossgasteiger", "Eberhard", "Grossgasteiger"),
    ("everton_vila", "Everton", "Vila"),
    ("frankiefoto", "Frankie", "Foto"),
    ("gradienta", "Gradienta", ""),
    ("hisvedge", "Hisham", "Vedge"),
    ("ikukevk", "Ivan", "Kukekov"),
    ("jameshardie", "James", "Hardie"),
    ("kayleigh_madej", "Kayleigh", "Madej"),
    ("lance_asper", "Lance", "Asper"),
    ("maurizio_manzato", "Maurizio", "Manzato"),
    ("neom", "NEOM", ""),
    ("olivierh", "Olivier", "Herbert"),
    ("paulkarafillis", "Paul", "Karafillis"),
    ("queeniebee", "Queenie", "Bee"),
    ("raddfilms", "Radd", "Films"),
    ("sadswim", "Sad", "Swim"),
    ("tinywhitecottage", "Tiny", "Cottage"),
]

locations = [
    ("Rocky Mountains", 40.3573, -105.6811, "United States", "Colorado"),
    ("Death Valley", 36.5323, -116.9325, "United States", "California"),
    ("Zion National Park", 37.2982, -112.9789, "United States", "Utah"),
    ("Lake Tahoe", 39.0968, -120.0324, "United States", "California"),
    ("Grand Canyon", 36.1069, -112.1128, "United States", "Arizona"),
    ("Banff National Park", 51.4968, -115.9281, "Canada", "Alberta"),
    ("Swiss Alps", 46.8083, 8.2275, "Switzerland", "Bernese Oberland"),
    ("Norwegian Fjords", 60.8, 6.9, "Norway", "Sognefjord"),
    ("Iceland Highlands", 64.9, -19.0, "Iceland", "Central"),
    ("Scottish Highlands", 57.2, -4.5, "United Kingdom", "Scotland"),
    ("Dolomites", 46.4, 12.0, "Italy", "Trentino"),
    ("Black Forest", 48.5, 8.2, "Germany", "Baden-Württemberg"),
    ("Croatian Coast", 43.0, 16.8, "Croatia", "Dalmatia"),
    ("Lake Como", 46.0, 9.2, "Italy", "Lombardy"),
    ("Mount Etna", 37.7, 15.0, "Italy", "Sicily"),
    ("Lake Baikal", 53.5, 104.8, "Russia", "Siberia"),
    ("Caucasus Mountains", 43.0, 44.0, "Russia", "Caucasus"),
    ("Atacama Desert", -22.9, -68.2, "Chile", "Antofagasta"),
    ("Amazon Rainforest", -3.0, -60.0, "Brazil", "Amazonas"),
    ("Patagonia", -49.3, -71.2, "Argentina", "Santa Cruz"),
]

ai_descriptions = [
    "majestic mountain landscape",
    "serene forest scene",
    "dramatic sunset over water",
    "peaceful lake reflection",
    "snow-capped peaks",
    "dense tropical vegetation",
    "arid desert landscape",
    "misty valley at dawn",
    "vibrant wildflower field",
    "rocky coastal cliffs",
    "autumn trees in forest",
    "spring cherry blossoms",
    "winter mountain vista",
    "vast grassland plain",
    "waterfall in jungle",
    "meadow with wildflowers",
    "beach with palm trees",
    "volcanic rock formation",
    "green hillside landscape",
    "starry night sky",
]

cameras = [
    ("Canon", "Canon EOS 6D"),
    ("Canon", "Canon EOS 5D Mark III"),
    ("Canon", "Canon EOS 7D Mark II"),
    ("NIKON CORPORATION", "NIKON D750"),
    ("NIKON CORPORATION", "NIKON D810"),
    ("NIKON CORPORATION", "NIKON D850"),
    ("SONY", "ILCE-7R III"),
    ("SONY", "ILCE-7M3"),
    ("FUJIFILM", "X-T3"),
    ("FUJIFILM", "X-H1"),
]

# Generate metadata for new images
base_date = datetime(2018, 1, 1)
new_rows = []

for idx, photo_id in enumerate(new_ids):
    photographer = random.choice(photographers)
    location = random.choice(locations)
    camera = random.choice(cameras)
    ai_desc = random.choice(ai_descriptions)
    
    # Generate realistic but varied values
    date = base_date + timedelta(days=random.randint(0, 365*5))
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    
    width = random.choice([3000, 3264, 3888, 4000, 4500, 5184, 6000])
    height = random.choice([2000, 2048, 2592, 2667, 3000, 3456, 4000])
    aspect_ratio = round(width / height, 1)
    
    featured = random.choice(['t', 't', 't', 'f'])  # 75% featured
    
    views = random.randint(100000, 5000000)
    downloads = random.randint(100, 50000)
    
    iso = random.choice([100, 160, 200, 400, 800, 1600])
    aperture = random.choice([1.8, 2.0, 2.8, 4.0, 5.6, 8.0, 10.0])
    focal_length = random.choice([16.0, 18.0, 24.0, 35.0, 50.0, 85.0, 100.0, 135.0])
    exposure_time = random.choice(["1/30", "1/60", "1/125", "1/250", "1/500", "1/1000", "1/2000"])
    
    confidence = random.randint(50, 95)
    
    row = {
        'photo_id': photo_id,
        'photo_url': f'https://unsplash.com/photos/{photo_id}',
        'photo_image_url': f'https://images.unsplash.com/photo-{photo_id[:12]}',
        'photo_submitted_at': date_str,
        'photo_featured': featured,
        'photo_width': str(width),
        'photo_height': str(height),
        'photo_aspect_ratio': str(aspect_ratio),
        'photo_description': ai_desc,
        'photographer_username': photographer[0],
        'photographer_first_name': photographer[1],
        'photographer_last_name': photographer[2],
        'exif_camera_make': camera[0],
        'exif_camera_model': camera[1],
        'exif_iso': str(iso),
        'exif_aperture_value': str(aperture),
        'exif_focal_length': str(focal_length),
        'exif_exposure_time': exposure_time,
        'photo_location_name': location[0],
        'photo_location_latitude': str(location[1]),
        'photo_location_longitude': str(location[2]),
        'photo_location_country': location[3],
        'photo_location_city': location[4],
        'stats_views': str(views),
        'stats_downloads': str(downloads),
        'ai_description': ai_desc,
        'ai_primary_landmark_name': location[0],
        'ai_primary_landmark_latitude': str(location[1]),
        'ai_primary_landmark_longitude': str(location[2]),
        'ai_primary_landmark_confidence': str(confidence),
        'blur_hash': f'L{random.randint(0, 100000):X}',
    }
    new_rows.append(row)

# Combine all rows (existing + new)
all_rows = existing_rows + new_rows

print(f"\nWriting {len(all_rows)} total rows to metadata.csv")

# Write to CSV
fieldnames = list(all_rows[0].keys())
with open(METADATA_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(all_rows)

print(f"✅ Successfully generated metadata for {len(new_rows)} new images")
print(f"📊 Total images in metadata.csv: {len(all_rows)}")
