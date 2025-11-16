package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	"github.com/urfave/cli/v2"
)

func main() {
	app := &cli.App{
		Name:  "fb2md",
		Usage: "Convert FB2 (FictionBook) files to Markdown",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:    "output",
				Aliases: []string{"o"},
				Usage:   "Output file path (default: same as input with .md extension)",
			},
			&cli.BoolFlag{
				Name:    "extract-images",
				Aliases: []string{"i"},
				Usage:   "Extract embedded images to a separate directory",
				Value:   false,
			},
			&cli.StringFlag{
				Name:    "images-dir",
				Usage:   "Directory to save extracted images (default: <output>_images)",
				Value:   "",
			},
		},
		Action: func(c *cli.Context) error {
			if c.NArg() == 0 {
				return fmt.Errorf("please provide an FB2 file to convert")
			}

			inputFile := c.Args().Get(0)
			outputFile := c.String("output")

			// Default output file
			if outputFile == "" {
				ext := filepath.Ext(inputFile)
				outputFile = strings.TrimSuffix(inputFile, ext) + ".md"
			}

			imagesDir := c.String("images-dir")
			if imagesDir == "" && c.Bool("extract-images") {
				ext := filepath.Ext(outputFile)
				imagesDir = strings.TrimSuffix(outputFile, ext) + "_images"
			}

			// Convert
			converter := NewConverter()
			if err := converter.Convert(inputFile, outputFile, c.Bool("extract-images"), imagesDir); err != nil {
				return fmt.Errorf("conversion failed: %w", err)
			}

			fmt.Printf("✓ Successfully converted %s to %s\n", inputFile, outputFile)
			if c.Bool("extract-images") {
				fmt.Printf("✓ Images extracted to %s\n", imagesDir)
			}

			return nil
		},
	}

	if err := app.Run(os.Args); err != nil {
		log.Fatal(err)
	}
}
