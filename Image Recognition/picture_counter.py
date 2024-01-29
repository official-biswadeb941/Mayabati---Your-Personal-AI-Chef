import os
from collections import defaultdict
from PIL import Image

def check_picture_formats(directory):
    folder_picture_counts = {}
    odd_format_images = defaultdict(list)  # Tracks images with odd formats in each folder
    corrupted_images = {}
    all_extensions = defaultdict(int)  # Track all file extensions encountered

    for root, dirs, files in os.walk(directory):
        picture_count = 0
        extensions = set()  # Track unique file extensions in each folder

        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()

            if ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp'):
                picture_count += 1
                try:
                    img = Image.open(os.path.join(root, file))
                    img.verify()
                except (IOError, SyntaxError) as e:
                    corrupted_images[os.path.join(root, file)] = str(e)

                extensions.add(ext)
                all_extensions[ext] += 1

        folder_picture_counts[root] = picture_count

        # Check for uncommon file extensions within each folder
        if len(extensions) > 1:
            for file in files:
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.bmp'):
                    odd_format_images[root].append(file)

    # Check for uncommon file extensions across the entire directory
    total_picture_count = sum(folder_picture_counts.values())
    uncommon_extensions = [ext for ext, count in all_extensions.items() if count > 0.1 * total_picture_count]
    for folder, count in folder_picture_counts.items():
        if count > 0.1 * total_picture_count:
            for file in files:
                _, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext in uncommon_extensions:
                    odd_format_images[folder].append(file)

    return folder_picture_counts, odd_format_images, corrupted_images


def generate_report(directory, folder_picture_counts, odd_format_images, corrupted_images):
    report = f"Picture Report for directory: {directory}\n\n"
    report += "Folder-wise Picture Counts:\n"
    for folder, count in folder_picture_counts.items():
        report += f"{folder}: {count} pictures\n"
    report += "\nFolders with Odd Formats:\n"
    for folder in odd_format_images:
        report += f"{folder}\n"
    report += "\nCorrupted Images:\n"
    for image_path, error in corrupted_images.items():
        report += f"{image_path} - {error}\n"
    return report

def save_report(report, filename):
    with open(filename, 'w') as f:
        f.write(report)
    print(f"Report saved to {filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path to check: ")

    # Validate directory path
    if not os.path.isdir(directory):
        print("Invalid directory path!")
    else:
        folder_picture_counts, odd_format_images, corrupted_images = check_picture_formats(directory)
        report = generate_report(directory, folder_picture_counts, odd_format_images, corrupted_images)
        print(report)
        save_report(report, "pic-report.txt")


    #/media/official-biswadeb941/Biswadeb/Programming_Projects/Python_Projects/Mayabati/data/input/Images
