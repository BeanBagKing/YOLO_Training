import os
import json
from PIL import Image

# Define paths
annotations_dir = r"C:\Directory\Images\ExDark_Annno"
images_dir = r"C:\Directory\Images\ExDark"
output_file = r"C:\Directory\Images\annotations.json"

# Create output directory if not exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Initialize COCO structure
coco_data = {
    "images": [],
    "annotations": [],
    "categories": [],
}

category_map = {}  # Mapping of class names to IDs
annotation_id = 1  # Unique annotation ID across the dataset
image_id = 1  # Unique image ID across the dataset

def get_image_extensions(images_dir):
    """Enumerate all unique file extensions in the image directory."""
    extensions = set()
    for root, _, files in os.walk(images_dir):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext:  # Avoid adding empty extensions
                extensions.add(ext)
    return list(extensions)

def find_image_file(annotation_file, images_dir, relative_path, valid_extensions):
    """Attempt to find the corresponding image file based on dynamically generated extensions."""
    # Create a base_name by stripping any known extensions from the annotation file
    base_name = os.path.splitext(os.path.basename(annotation_file))[0]
    
    # Remove any extension in valid_extensions that may be part of base_name
    for ext in valid_extensions:
        if base_name.endswith(ext):
            base_name = base_name[: -len(ext)]
    
    image_dir = os.path.join(images_dir, relative_path)
    
    # Check all files in the corresponding directory for a matching base name
    if os.path.exists(image_dir):
        for file in os.listdir(image_dir):
            if os.path.splitext(file)[0] == base_name:
                return os.path.join(image_dir, file)

    # If no image file is found, print out the available files for debugging
    available_files = os.listdir(image_dir) if os.path.exists(image_dir) else []
    print(f"Available files in directory {image_dir}: {available_files}")
    
    raise FileNotFoundError(f"No corresponding image found for {annotation_file}.")



def add_category(class_name):
    """Add a category to the categories list if it doesn't exist yet."""
    if class_name not in category_map:
        category_id = len(category_map) + 1
        category_map[class_name] = category_id
        coco_data["categories"].append({
            "id": category_id,
            "name": class_name,
            "supercategory": "object",
        })

def create_coco_annotation(class_name, bbox, image_id, annotation_id):
    """Create an annotation entry for the COCO JSON."""
    category_id = category_map[class_name]
    x_min, y_min, width, height = bbox
    return {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [x_min, y_min, width, height],
        "area": width * height,
        "segmentation": [],  # No segmentation data in the current format
        "iscrowd": 0,
    }

def process_annotation_file(annotation_file, images_dir, relative_path, valid_extensions):
    global image_id, annotation_id

    # Debugging: Print the relative path and the image file being searched
    print(f"Processing annotation: {annotation_file}")
    print(f"Looking for image in: {images_dir}, relative path: {relative_path}")
    
    # Find the image file with the dynamically generated extensions
    image_file = find_image_file(annotation_file, images_dir, relative_path, valid_extensions)
    
    # Continue with existing logic...
    with open(annotation_file, 'r') as f:
        lines = f.readlines()

    # Continue with existing logic...
    with Image.open(image_file) as img:
        img_width, img_height = img.size

    # Add image data to COCO structure
    coco_data["images"].append({
        "id": image_id,
        "file_name": os.path.basename(image_file),
        "width": img_width,
        "height": img_height,
    })

    # Process each line for annotations (same as before)
    for line in lines:
        if line.startswith('%'):
            continue
        parts = line.strip().split()
        class_name = parts[0]
        x_min = int(parts[1])
        y_min = int(parts[2])
        width = int(parts[3])
        height = int(parts[4])

        # Add class to category map
        add_category(class_name)

        # Create and add the annotation
        bbox = [x_min, y_min, width, height]
        annotation = create_coco_annotation(class_name, bbox, image_id, annotation_id)
        coco_data["annotations"].append(annotation)
        annotation_id += 1

    image_id += 1


def process_directory(annotations_dir, images_dir):
    """Recursively process all annotation files and convert them to COCO format."""
    valid_extensions = get_image_extensions(images_dir)  # Get valid extensions

    for root, _, files in os.walk(annotations_dir):
        for file in files:
            if file.endswith(".txt"):
                annotation_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, annotations_dir)
                
                # Pass valid_extensions to process_annotation_file
                process_annotation_file(annotation_file, images_dir, relative_path, valid_extensions)
                print(f"Processed: {annotation_file}")



# Process the annotation directory and convert annotations
process_directory(annotations_dir, images_dir)

# Write the COCO JSON file
with open(output_file, 'w') as f:
    json.dump(coco_data, f, indent=4)

print(f"COCO annotations saved to {output_file}")
