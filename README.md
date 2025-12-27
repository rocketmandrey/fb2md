# FB2/EPUB to Markdown Converter

A powerful and flexible toolset for converting ebook files (FB2, EPUB) into clean Markdown, with additional utilities for translation improvement and publishing.

## 📂 Project Structure

- **`fb2md`** (or `main.go`): The core converter tool written in Go.
- **`books/`**: Default input directory. Place your `.fb2` or `.epub` files here.
- **`markdown/`**: Default output directory. Converted files appear here.
- **`scripts/`**: Helper Python and Shell scripts for post-processing (translation, publishing).
- **`epub/`**, **`fb2/`**: Directories for specific format processing or storage.

## 🚀 Core Tool: `fb2md`

The main converter is a high-performance Go application.

### Installation

```bash
# Run directly with Go
go run . --help

# Or build the binary
go build -o fb2md
./fb2md --help
```

### Usage Examples

**Convert a single file:**
```bash
go run . "books/my_book.epub"
```

**Convert all books in a directory:**
```bash
go run . --input-dir books --output-dir markdown
```

**Extract images:**
```bash
go run . --extract-images "books/my_book.fb2"
```

**Prevent sleep (macOS only):**
Useful for long batch conversions.
```bash
go run . --caffeinate --input-dir books
```

## 🛠 Helper Scripts (`scripts/`)

Located in the `scripts/` directory, these tools assist with specific workflows. 

**Setup:**
Install the required Python dependencies:
```bash
pip install -r scripts/requirements.txt
```

**Note:** `improve_translation.py`, `publish_telegraph.py`, and `create_epub.sh` accept file paths as arguments. 
However, `auto_insert.py` relies on specific line numbers and file paths defined within the script, so you will likely need to edit it for your specific book.

### 1. `improve_translation.py`
Uses the Anthropic (Claude) API to improve the quality of machine-translated text.
- **Features:** Fixes grammar, removes awkward calques, improves readability while preserving Markdown formatting.
- **Setup:** Requires `ANTHROPIC_API_KEY` environment variable.

### 2. `publish_telegraph.py`
Publishes a Markdown book to [Telegraph](https://telegra.ph/) as a series of linked chapters.
- **Features:** Creates a Table of Contents, splits chapters, and adds navigation (Prev/Next) links.
- **Setup:** Requires `TELEGRAPH_ACCESS_TOKEN`.

### 3. `create_epub.sh`
Converts a Markdown file back into an EPUB file using `pandoc`.
- **Usage:** Useful for generating a clean EPUB after editing/improving the Markdown.
- **Prerequisites:** Requires `pandoc`.

### 4. `auto_insert.py`
A utility to insert images at specific lines in the Markdown file found during the conversion process.

## ⚙️ Development

### Prerequisites
- Go 1.21+
- Python 3.8+ (for scripts)
- Pandoc (for `create_epub.sh`)

### Building
```bash
go build -o fb2md
```

## 📝 License
MIT License
