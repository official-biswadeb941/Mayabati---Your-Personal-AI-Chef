import os
from PIL import Image

def check_picture_formats(directory):
    folder_picture_counts = {}
    odd_format_folders = []
    corrupted_folders = []

    for root, dirs, files in os.walk(directory):
        picture_count = 0
        odd_format_found = False
        corrupted_found = False
        
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                picture_count += 1
                try:
                    # Attempt to open the image file
                    img = Image.open(os.path.join(root, file))
                    img.verify()  # Check for corruption
                except (IOError, SyntaxError) as e:
                    # PIL couldn't open the image or it's corrupted
                    corrupted_found = True

                    # Print the error for debugging purposes
                    print(f"Corrupted image: {os.path.join(root, file)} - {e}")

            else:
                odd_format_found = True

        if odd_format_found:
            odd_format_folders.append(root)

        if corrupted_found:
            corrupted_folders.append(root)

        folder_picture_counts[root] = picture_count

    return folder_picture_counts, odd_format_folders, corrupted_folders

def generate_report(directory, folder_picture_counts, odd_format_folders, corrupted_folders):
    report = f"Picture Report for directory: {directory}\n\n"
    report += "Folder-wise Picture Counts:\n"
    for folder, count in folder_picture_counts.items():
        report += f"{folder}: {count} pictures\n"
    report += "\nFolders with Odd Formats:\n"
    for folder in odd_format_folders:
        report += f"{folder}\n"
    report += "\nFolders with Corrupted Pictures:\n"
    for folder in corrupted_folders:
        report += f"{folder}\n"
    return report

def save_report(report, filename):
    with open(filename, 'w') as f:
        f.write(report)
    print(f"Report saved to {filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path to check: ")
    folder_picture_counts, odd_format_folders, corrupted_folders = check_picture_formats(directory)
    report = generate_report(directory, folder_picture_counts, odd_format_folders, corrupted_folders)
    print(report)
    save_report(report, "pic-report.txt")

    #/media/official-biswadeb941/Biswadeb/Programming_Projects/Python_Projects/Mayabati/data/input/Images
