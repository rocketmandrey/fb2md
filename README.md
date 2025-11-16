# FB2 to Markdown Converter

A fast and efficient converter for transforming FB2 (FictionBook) ebook files into Markdown format, built in Go.

## Features

- ✅ **Complete metadata extraction**: Title, authors, genres, dates, and annotations
- ✅ **Rich formatting support**: Emphasis, strong text, links, images, quotes
- ✅ **Hierarchical structure**: Properly nested sections with heading levels
- ✅ **Image extraction**: Extracts embedded base64 images to separate files
- ✅ **Clean markdown output**: Well-formatted, readable markdown
- ✅ **Fast performance**: Built in Go for speed and efficiency

## Installation

### Prerequisites

- Go 1.21 or higher

### Build from source

```bash
git clone <your-repo-url>
cd fb2epub-markdown-converter
go mod tidy
go build -o fb2md
```

## Usage

### Basic conversion

Convert an FB2 file to Markdown:

```bash
./fb2md book.fb2
```

This creates `book.md` in the same directory.

### Custom output path

Specify a custom output file:

```bash
./fb2md --output my-book.md book.fb2
```

### Extract images

Extract embedded images to a separate directory:

```bash
./fb2md --extract-images book.fb2
```

This creates `book_images/` directory with all extracted images.

### Custom images directory

Specify a custom directory for extracted images:

```bash
./fb2md --extract-images --images-dir images/my-book book.fb2
```

### Complete example

```bash
./fb2md --extract-images --output output.md --images-dir output_images input.fb2
```

### Command-line flags

```
--output, -o         Output file path (default: same as input with .md extension)
--extract-images, -i Extract embedded images to a separate directory
--images-dir         Directory to save extracted images (default: <output>_images)
--help, -h           Show help message
```

## FB2 to Markdown Mapping

The converter maps FB2 elements to Markdown as follows:

| FB2 Element | Markdown Output |
|-------------|----------------|
| `<p>` | Paragraph |
| `<emphasis>` | *italic* |
| `<strong>` | **bold** |
| `<strikethrough>` | ~~strikethrough~~ |
| `<code>` | `code` |
| `<title>` | # Heading (level based on depth) |
| `<subtitle>` | **Subtitle** |
| `<section>` | Hierarchical sections (##, ###, etc.) |
| `<epigraph>` | > Blockquote |
| `<a>` | [text](url) |
| `<image>` | ![alt](image) |
| `<empty-line>` | Blank line |

## Output Structure

A typical converted markdown file includes:

1. **Book title** - Main heading
2. **Metadata** - Authors, genres, date
3. **Annotation** - Book description/summary
4. **Content** - All sections with proper hierarchy
5. **Images** - Referenced from extracted images directory (if enabled)

## Example

### Input (FB2)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">
  <description>
    <title-info>
      <book-title>My Book</book-title>
      <author>
        <first-name>John</first-name>
        <last-name>Doe</last-name>
      </author>
    </title-info>
  </description>
  <body>
    <section>
      <title><p>Chapter 1</p></title>
      <p>This is a <emphasis>sample</emphasis> paragraph.</p>
    </section>
  </body>
</FictionBook>
```

### Output (Markdown)

```markdown
# My Book

**Authors:** John Doe

---

## Chapter 1

This is a *sample* paragraph.
```

## Supported FB2 Elements

### Metadata
- Book title
- Authors (with first, middle, last names)
- Genres
- Dates
- Annotations
- Keywords

### Content Elements
- Sections (nested)
- Titles and subtitles
- Paragraphs
- Emphasis and strong text
- Links (internal and external)
- Images (embedded and external)
- Epigraphs with authors
- Empty lines
- Code blocks
- Strikethrough text

## Technical Details

### Dependencies

- `github.com/beevik/etree` - XML parsing
- `github.com/urfave/cli/v2` - Command-line interface

### Performance

The converter is built in Go for optimal performance:
- Fast XML parsing with etree
- Efficient string building
- Minimal memory footprint
- Single-pass conversion

## Based on fb2converter

This tool was inspired by the excellent [fb2converter](https://github.com/rupor-github/fb2converter) project by rupor-github, which converts FB2 files to EPUB, MOBI, and other formats. We studied their implementation to understand the FB2 format structure and built this specialized Markdown converter.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any problems or have suggestions, please open an issue on GitHub.
