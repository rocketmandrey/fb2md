#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and print output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        return False
    print(result.stdout)
    return True

def convert_to_markdown(input_path, output_dir):
    """Convert ebook to markdown using the Go tool."""
    # Assuming running from project root
    # Determine if we should use the Go tool (FB2/EPUB) or Pandoc (others)
    suffix = Path(input_path).suffix.lower()
    base_name = Path(input_path).stem # Define base_name here, as it's used in both branches
    
    md_file = None # Initialize md_file to None

    if suffix in ['.fb2', '.epub']:
        cmd = ["go", "run", ".", "--output-dir", str(output_dir), str(input_path)]
        print(f"Converting {input_path} to Markdown using fb2md...")
        if run_command(cmd):
            # fb2md naming convention: filename without ext + .md
            # Go tool doesn't replace spaces in filename, only separators.
            # So if input is "books/My Book.epub", output is "markdown/My Book.md"
            md_file = Path(output_dir) / f"{base_name}.md"
            if md_file.exists():
                print(f"✓ Markdown created: {md_file}")
                return md_file
            else:
                print(f"Warning: fb2md ran, but expected output file {md_file} not found. Falling back to Pandoc.")
        else:
            print(f"Warning: fb2md failed for {input_path}. Falling back to Pandoc.")
    
    # Fallback to Pandoc for other formats (or if fb2md failed, or if suffix not .fb2/.epub)
    print(f"Attempting conversion with Pandoc for {input_path}...")
    md_file = Path(output_dir) / f"{base_name}.md" # Re-define md_file for pandoc output
    cmd = ["pandoc", str(input_path), "--to", "markdown", "--output", str(md_file)]
    # Optional: Extract media if possible? Pandoc handles it differently.
    # cmd.extend(["--extract-media", str(output_dir)]) 
    
    if run_command(cmd):
         if md_file.exists():
            print(f"✓ Markdown created (via Pandoc): {md_file}")
            return md_file
            
    print(f"Error: Failed to convert {input_path}")
    return None

def translate_markdown(md_file, context):
    """Improve translation using the python script."""
    print(f"Improving translation for {md_file}...")
    cmd = ["python3", "scripts/improve_translation.py", str(md_file), "--context", context]
    if run_command(cmd):
        print(f"✓ Translation improved.")
        return True
    return False

def convert_to_epub(md_file, output_dir):
    """Convert Markdown to EPUB using pandoc."""
    output_epub = Path(output_dir) / f"{md_file.stem}.epub"
    print(f"Generating EPUB: {output_epub}")
    
    # Simple metadata creation (optional, could be improved)
    cmd = [
        "pandoc", str(md_file),
        "--from", "markdown",
        "--to", "epub3",
        "--toc",
        "--output", str(output_epub)
    ]
    if run_command(cmd):
        print(f"✓ EPUB created: {output_epub}")
        return True
    return False

def convert_to_fb2(md_file, output_dir):
    """Convert Markdown to FB2 using pandoc."""
    output_fb2 = Path(output_dir) / f"{md_file.stem}.fb2"
    print(f"Generating FB2: {output_fb2}")
    
    cmd = [
        "pandoc", str(md_file),
        "--from", "markdown",
        "--to", "fb2",
        "--output", str(output_fb2)
    ]
    if run_command(cmd):
        print(f"✓ FB2 created: {output_fb2}")
        return True
    return False

def publish_to_telegraph(md_file):
    """Publish to Telegraph."""
    print(f"Publishing to Telegraph...")
    cmd = ["python3", "scripts/publish_telegraph.py", str(md_file)]
    if run_command(cmd):
        print(f"✓ Published to Telegraph.")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Unified eBook Converter & Processor")
    parser.add_argument("input_file", help="Path to input book (FB2, EPUB, or any Pandoc-supported format)")
    parser.add_argument("--translate", action="store_true", help="Improve translation using AI")
    parser.add_argument("--context", default="General", help="Context for translation (e.g. 'Science Fiction', 'Business')")
    parser.add_argument("--to-epub", action="store_true", help="Generate EPUB output")
    parser.add_argument("--to-fb2", action="store_true", help="Generate FB2 output")
    parser.add_argument("--to-telegraph", action="store_true", help="Publish to Telegraph")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    # Directories
    project_root = Path.cwd() # Assume running from root
    markdown_dir = project_root / "markdown"
    output_dir = project_root / "output"
    
    markdown_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # 1. Convert to Markdown
    md_file = convert_to_markdown(input_path, markdown_dir)
    if not md_file:
        sys.exit(1)
        
    # 2. Translate (Optional)
    if args.translate:
        translate_markdown(md_file, args.context)
        
    # 3. Output Formats
    if args.to_epub:
        convert_to_epub(md_file, output_dir)
        
    if args.to_fb2:
        convert_to_fb2(md_file, output_dir)
        
    if args.to_telegraph:
        publish_to_telegraph(md_file)
        
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
