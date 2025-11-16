package main

import (
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/beevik/etree"
)

type Converter struct {
	doc           *etree.Document
	output        strings.Builder
	sectionLevel  int
	extractImages bool
	imagesDir     string
	imageCounter  int
}

func NewConverter() *Converter {
	return &Converter{
		sectionLevel: 0,
		imageCounter: 0,
	}
}

func (c *Converter) Convert(inputFile, outputFile string, extractImages bool, imagesDir string) error {
	c.extractImages = extractImages
	c.imagesDir = imagesDir

	// Parse FB2 file
	doc := etree.NewDocument()
	if err := doc.ReadFromFile(inputFile); err != nil {
		return fmt.Errorf("failed to read FB2 file: %w", err)
	}
	c.doc = doc

	// Create images directory if needed
	if c.extractImages && c.imagesDir != "" {
		if err := os.MkdirAll(c.imagesDir, 0755); err != nil {
			return fmt.Errorf("failed to create images directory: %w", err)
		}
	}

	// Find root element
	root := doc.SelectElement("FictionBook")
	if root == nil {
		return fmt.Errorf("invalid FB2 file: FictionBook element not found")
	}

	// Process description (metadata)
	if desc := root.SelectElement("description"); desc != nil {
		c.processDescription(desc)
	}

	// Process all bodies
	for _, body := range root.SelectElements("body") {
		c.processBody(body)
	}

	// Extract embedded images
	if c.extractImages {
		c.extractBinaryImages(root)
	}

	// Write output
	if err := os.WriteFile(outputFile, []byte(c.output.String()), 0644); err != nil {
		return fmt.Errorf("failed to write output file: %w", err)
	}

	return nil
}

func (c *Converter) processDescription(desc *etree.Element) {
	titleInfo := desc.SelectElement("title-info")
	if titleInfo == nil {
		return
	}

	// Book title
	if title := titleInfo.SelectElement("book-title"); title != nil {
		c.output.WriteString("# ")
		c.output.WriteString(title.Text())
		c.output.WriteString("\n\n")
	}

	// Authors
	authors := titleInfo.SelectElements("author")
	if len(authors) > 0 {
		c.output.WriteString("**Authors:** ")
		authorNames := []string{}
		for _, author := range authors {
			name := c.getAuthorName(author)
			if name != "" {
				authorNames = append(authorNames, name)
			}
		}
		c.output.WriteString(strings.Join(authorNames, ", "))
		c.output.WriteString("\n\n")
	}

	// Genres
	genres := titleInfo.SelectElements("genre")
	if len(genres) > 0 {
		c.output.WriteString("**Genres:** ")
		genreNames := []string{}
		for _, genre := range genres {
			if text := genre.Text(); text != "" {
				genreNames = append(genreNames, text)
			}
		}
		c.output.WriteString(strings.Join(genreNames, ", "))
		c.output.WriteString("\n\n")
	}

	// Annotation
	if annotation := titleInfo.SelectElement("annotation"); annotation != nil {
		c.output.WriteString("## Annotation\n\n")
		c.processElement(annotation)
		c.output.WriteString("\n\n")
	}

	// Date
	if date := titleInfo.SelectElement("date"); date != nil {
		c.output.WriteString("**Date:** ")
		c.output.WriteString(date.Text())
		c.output.WriteString("\n\n")
	}

	// Separator
	c.output.WriteString("---\n\n")
}

func (c *Converter) getAuthorName(author *etree.Element) string {
	parts := []string{}

	if firstName := author.SelectElement("first-name"); firstName != nil {
		parts = append(parts, firstName.Text())
	}
	if middleName := author.SelectElement("middle-name"); middleName != nil {
		parts = append(parts, middleName.Text())
	}
	if lastName := author.SelectElement("last-name"); lastName != nil {
		parts = append(parts, lastName.Text())
	}
	if nickname := author.SelectElement("nickname"); nickname != nil && len(parts) == 0 {
		parts = append(parts, nickname.Text())
	}

	return strings.Join(parts, " ")
}

func (c *Converter) processBody(body *etree.Element) {
	// Process body title if present
	if title := body.SelectElement("title"); title != nil {
		c.output.WriteString("\n## ")
		for _, child := range title.ChildElements() {
			c.processInlineElement(child)
		}
		c.output.WriteString("\n\n")
	}

	// Process all sections
	for _, section := range body.SelectElements("section") {
		c.processSection(section)
	}
}

func (c *Converter) processSection(section *etree.Element) {
	c.sectionLevel++
	defer func() { c.sectionLevel-- }()

	// Process section title
	if title := section.SelectElement("title"); title != nil {
		// Determine heading level (1-6 max in Markdown)
		level := c.sectionLevel + 1
		if level > 6 {
			level = 6
		}
		c.output.WriteString(strings.Repeat("#", level))
		c.output.WriteString(" ")

		// Extract all text from title
		titleText := c.extractAllText(title)
		c.output.WriteString(titleText)
		c.output.WriteString("\n\n")
	}

	// Process epigraphs
	for _, epigraph := range section.SelectElements("epigraph") {
		c.processEpigraph(epigraph)
	}

	// Process all child elements
	for _, child := range section.ChildElements() {
		switch child.Tag {
		case "title", "epigraph":
			// Already processed
		case "section":
			c.processSection(child)
		case "p":
			c.processParagraph(child)
		case "subtitle":
			c.processSubtitle(child)
		case "empty-line":
			c.output.WriteString("\n")
		case "image":
			c.processImage(child)
		default:
			c.processElement(child)
		}
	}
}

func (c *Converter) processEpigraph(epigraph *etree.Element) {
	for _, child := range epigraph.ChildElements() {
		switch child.Tag {
		case "p":
			c.output.WriteString("> ")
			c.processInlineElement(child)
			c.output.WriteString("\n")
		case "text-author":
			c.output.WriteString(">\n> — ")
			c.processInlineElement(child)
			c.output.WriteString("\n")
		}
	}
	c.output.WriteString("\n")
}

func (c *Converter) processSubtitle(subtitle *etree.Element) {
	c.output.WriteString("**")
	c.processInlineElement(subtitle)
	c.output.WriteString("**\n\n")
}

func (c *Converter) processParagraph(p *etree.Element) {
	c.processInlineElement(p)
	c.output.WriteString("\n\n")
}

func (c *Converter) processElement(elem *etree.Element) {
	for _, child := range elem.ChildElements() {
		switch child.Tag {
		case "p":
			c.processParagraph(child)
		case "empty-line":
			c.output.WriteString("\n")
		case "section":
			c.processSection(child)
		case "subtitle":
			c.processSubtitle(child)
		case "epigraph":
			c.processEpigraph(child)
		case "image":
			c.processImage(child)
		default:
			c.processInlineElement(child)
		}
	}
}

func (c *Converter) processInlineElement(elem *etree.Element) {
	// Process text before element
	text := strings.TrimSpace(elem.Text())
	if text != "" {
		c.output.WriteString(text)
	}

	// Process child elements
	for _, child := range elem.ChildElements() {
		switch child.Tag {
		case "emphasis":
			c.output.WriteString("*")
			c.processInlineElement(child)
			c.output.WriteString("*")
		case "strong":
			c.output.WriteString("**")
			c.processInlineElement(child)
			c.output.WriteString("**")
		case "strikethrough":
			c.output.WriteString("~~")
			c.processInlineElement(child)
			c.output.WriteString("~~")
		case "code":
			c.output.WriteString("`")
			c.processInlineElement(child)
			c.output.WriteString("`")
		case "a":
			c.processLink(child)
		case "image":
			c.processImage(child)
		case "empty-line":
			c.output.WriteString("\n")
		default:
			c.processInlineElement(child)
		}

		// Process tail text after element
		tail := strings.TrimSpace(child.Tail())
		if tail != "" {
			c.output.WriteString(" ")
			c.output.WriteString(tail)
		}
	}
}

func (c *Converter) processLink(link *etree.Element) {
	href := link.SelectAttrValue("l:href", "")
	if href == "" {
		href = link.SelectAttrValue("href", "")
	}

	// Get link text - could be direct text or from child elements
	linkText := c.extractAllText(link)
	if linkText == "" {
		linkText = "Link"
	}

	c.output.WriteString("[")
	c.output.WriteString(linkText)
	c.output.WriteString("]")
	c.output.WriteString("(")
	c.output.WriteString(href)
	c.output.WriteString(")")
}

// extractAllText recursively extracts all text from an element and its children
func (c *Converter) extractAllText(elem *etree.Element) string {
	var text strings.Builder

	if elem.Text() != "" {
		text.WriteString(elem.Text())
	}

	for _, child := range elem.ChildElements() {
		text.WriteString(c.extractAllText(child))
		if child.Tail() != "" {
			text.WriteString(child.Tail())
		}
	}

	return strings.TrimSpace(text.String())
}

func (c *Converter) processImage(img *etree.Element) {
	href := img.SelectAttrValue("l:href", "")
	if href == "" {
		href = img.SelectAttrValue("href", "")
	}

	// If it's an internal reference (starts with #), it refers to a binary element
	if strings.HasPrefix(href, "#") {
		imageID := strings.TrimPrefix(href, "#")

		if c.extractImages {
			// We'll extract the actual image later
			imagePath := filepath.Join(c.imagesDir, imageID)
			c.output.WriteString(fmt.Sprintf("![%s](%s)", imageID, imagePath))
		} else {
			c.output.WriteString(fmt.Sprintf("![Image: %s]", imageID))
		}
	} else {
		c.output.WriteString(fmt.Sprintf("![Image](%s)", href))
	}
	c.output.WriteString("\n\n")
}

func (c *Converter) extractBinaryImages(root *etree.Element) error {
	for _, binary := range root.SelectElements("binary") {
		id := binary.SelectAttrValue("id", "")
		contentType := binary.SelectAttrValue("content-type", "image/jpeg")

		if id == "" {
			continue
		}

		// Decode base64 image data
		imageData := binary.Text()
		imageData = strings.TrimSpace(imageData)

		decoded, err := base64.StdEncoding.DecodeString(imageData)
		if err != nil {
			fmt.Printf("Warning: failed to decode image %s: %v\n", id, err)
			continue
		}

		// Determine file extension from content type
		ext := ".jpg"
		if strings.Contains(contentType, "png") {
			ext = ".png"
		} else if strings.Contains(contentType, "gif") {
			ext = ".gif"
		}

		// Ensure the filename has the correct extension
		filename := id
		if !strings.HasSuffix(filename, ext) {
			filename = filename + ext
		}

		// Write image file
		imagePath := filepath.Join(c.imagesDir, filename)
		if err := os.WriteFile(imagePath, decoded, 0644); err != nil {
			fmt.Printf("Warning: failed to write image %s: %v\n", id, err)
			continue
		}
	}

	return nil
}
