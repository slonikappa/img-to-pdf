#!/usr/bin/env python3
"""
Cross-Platform Image to PDF Converter
Converts all images from a specified folder into a single PDF file.

Requirements: 
  - pip install Pillow (required)
  - pip install natsort (optional)
"""

import os
import sys
from pathlib import Path
import argparse

def check_pillow():
    """Check if Pillow is installed and provide installation instructions."""
    try:
        from PIL import Image
        return True
    except ImportError:
        print("Error: Pillow library is required but not installed.")
        print("\nTo install Pillow:")
        print("  pip install Pillow")
        print("\nOr if using conda:")
        print("  conda install pillow")
        return False

def get_image_files(folder_path):
    """Get all image files from the specified folder."""
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    image_files = []
    
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return []
    
    # Find all image files
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            image_files.append(file_path)
    
    # Sort files naturally (handles numbers properly: 1, 2, 10, 11, ...)
    try:
        # Use natsort if available (more robust)
        from natsort import natsorted, ns
        image_files = natsorted(image_files, key=lambda x: x.name, alg=ns.IGNORECASE)
    except ImportError:
        # Fallback to custom natural sort implementation
        import re
        
        def natural_sort_key(path):
            """Convert filename into list of string and number chunks for proper sorting."""
            def convert(text):
                return int(text) if text.isdigit() else text.lower()
            return [convert(c) for c in re.split('([0-9]+)', path.name)]
        
        image_files.sort(key=natural_sort_key)
    return image_files

def convert_images_to_pdf(image_folder, output_pdf="images.pdf"):
    """Convert all images in folder to a single PDF file."""
    
    if not check_pillow():
        return False
    
    from PIL import Image
    
    image_files = get_image_files(image_folder)
    
    if not image_files:
        print(f"No supported image files found in '{image_folder}'")
        print("Supported formats: JPG, JPEG, PNG, BMP, TIFF, TIF, WebP, GIF")
        return False
    
    print(f"Found {len(image_files)} image files")
    
    try:
        # Convert images to PIL Image objects
        images = []
        
        for i, img_path in enumerate(image_files, 1):
            print(f"Processing {i:2d}/{len(image_files)}: {img_path.name}")
            
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB if necessary (handles PNG transparency, CMYK, etc.)
                    if img.mode not in ('RGB', 'L'):  # L is grayscale
                        if img.mode == 'RGBA':
                            # Handle transparency by adding white background
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = rgb_img
                        else:
                            img = img.convert('RGB')
                    
                    # Create a copy to avoid issues with file handles
                    img_copy = img.copy()
                    images.append(img_copy)
                
            except Exception as e:
                print(f"Warning: Could not process {img_path.name}: {e}")
                continue
        
        if not images:
            print("No images could be processed successfully.")
            return False
        
        # Ensure output directory exists
        output_path = Path(output_pdf)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as PDF
        print(f"\nSaving PDF: {output_pdf}")
        images[0].save(
            output_pdf,
            save_all=True,
            append_images=images[1:],
            format='PDF',
            resolution=100.0,
            quality=85
        )
        
        # Show file size
        file_size = output_path.stat().st_size
        if file_size > 1024 * 1024:  # > 1MB
            print(f"Successfully created '{output_pdf}' ({file_size / (1024*1024):.1f} MB) with {len(images)} pages")
        else:
            print(f"Successfully created '{output_pdf}' ({file_size / 1024:.1f} KB) with {len(images)} pages")
        
        return True
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Convert images from a folder to PDF',
        epilog='Example: python img2pdf.py C:\\Photos -o vacation.pdf'
    )
    parser.add_argument('folder', help='Path to the folder containing images')
    parser.add_argument('-o', '--output', default='images.pdf', 
                       help='Output PDF filename (default: images.pdf)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show more detailed output')
    
    args = parser.parse_args()
    
    # Handle both forward and backslashes on Windows
    folder_path = Path(args.folder).resolve()
    output_path = Path(args.output).resolve()
    
    print("=" * 60)
    print("Image to PDF Converter")
    print("=" * 60)
    print(f"Input folder:  {folder_path}")
    print(f"Output PDF:    {output_path}")
    print("-" * 60)
    
    if args.verbose:
        print(f"Python version: {sys.version}")
        print(f"Operating system: {os.name}")
        print(f"Current directory: {Path.cwd()}")
        print("-" * 60)
    
    success = convert_images_to_pdf(folder_path, output_path)
    
    if success:
        print("\n✓ Conversion completed successfully!")
        if os.name == 'nt':  # Windows
            print(f"You can find your PDF at: {output_path}")
        else:
            print(f"PDF saved to: {output_path}")
    else:
        print("\n✗ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
