import os
from collections import Counter
from PIL import Image

def find_uncommon_image_formats(directory):
    image_formats = []
    
    # Traverse directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            try:
                # Get file extension
                _, ext = os.path.splitext(file)
                
                # Convert extension to lowercase for consistency
                ext = ext.lower()
                
                # Validate if it's an image file
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    image_formats.append(ext)
            except Exception as e:
                print(f"Error processing {file}: {e}")

    # Count occurrences of each image format
    format_counts = Counter(image_formats)
    
    # Find the least common format
    uncommon_format = min(format_counts, key=format_counts.get)
    
    # Filter out the images with the least common format
    uncommon_images = [f for f in os.listdir(directory) if f.lower().endswith(uncommon_format)]
    
    if not uncommon_images:
        print("No images found with the least common format.")
    else:
        print(f"Uncommon images with format {uncommon_format}:")
        for image in uncommon_images:
            print(image)
    
    return uncommon_format, uncommon_images
import os
import imghdr

def get_image_files(directory):
  """Returns a list of all image files in the given directory."""
  image_files = []
  for file in os.listdir(directory):
    file_path = os.path.join(directory, file)  # Get the full path to the file
    if os.path.isfile(file_path) and imghdr.what(file_path) is not None:  # Check if it's a file and if it's an image
      image_files.append(file_path)
  return image_files

def get_least_common_format(image_files):
  """Returns the least common format of the given image files."""
  image_formats = []
  for image_file in image_files:
    format_type = imghdr.what(image_file)
    if format_type is not None:
      image_formats.append(format_type)
  least_common_format = min(image_formats, key=image_formats.count)
  return least_common_format


def detect_images_in_directory(directory):
  """Detects all images in the given directory and returns a list of their paths."""
  image_files = get_image_files(directory)
  least_common_format = get_least_common_format(image_files)
  return image_files

if __name__ == '__main__':
  directory = '/media/official-biswadeb941/Biswadeb/Programming_Projects/Python_Projects/Mayabati/data/input/Images'
  image_files = detect_images_in_directory(directory)
  print(image_files)
