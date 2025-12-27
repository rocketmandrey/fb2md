package main

import (
	"fmt"
	"io/fs"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/urfave/cli/v2"
)

var caffeinateCmd *exec.Cmd

func main() {
	app := &cli.App{
		Name:  "fb2md",
		Usage: "Convert FB2/EPUB ebook files to Markdown",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:    "output",
				Aliases: []string{"o"},
				Usage:   "Output file path (only valid when converting a single file)",
			},
			&cli.StringFlag{
				Name:    "output-dir",
				Usage:   "Directory to store converted markdown files",
				Value:   "markdown",
			},
			&cli.StringFlag{
				Name:    "input-dir",
				Usage:   "Directory to scan for ebook files when no explicit inputs are provided",
				Value:   "books",
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
			&cli.BoolFlag{
				Name:    "caffeinate",
				Aliases: []string{"c"},
				Usage:   "Prevent system sleep during conversion (macOS only)",
				Value:   false,
			},
		},
		Action: func(c *cli.Context) error {
			// Prevent system sleep if flag is set
			if c.Bool("caffeinate") {
				if err := preventSleep(); err != nil {
					log.Printf("Warning: failed to prevent sleep: %v", err)
				} else {
					defer cleanupCaffeinate()
					// Handle signals to ensure cleanup
					sigChan := make(chan os.Signal, 1)
					signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
					go func() {
						<-sigChan
						cleanupCaffeinate()
						os.Exit(0)
					}()
				}
			}
			inputs := c.Args().Slice()
			if len(inputs) == 0 {
				inputs = []string{c.String("input-dir")}
			}

			if len(inputs) > 1 && c.String("output") != "" {
				return fmt.Errorf("--output can only be used when converting a single file")
			}

			if c.String("images-dir") != "" && len(inputs) > 1 {
				return fmt.Errorf("--images-dir can only be used when converting a single file")
			}

			outputDir := c.String("output-dir")
			if outputDir == "" {
				outputDir = "."
			}

			if err := os.MkdirAll(outputDir, 0755); err != nil {
				return fmt.Errorf("failed to create output directory: %w", err)
			}

			totalConverted := 0
			for _, inputPath := range inputs {
				info, err := os.Stat(inputPath)
				if err != nil {
					return fmt.Errorf("failed to stat %s: %w", inputPath, err)
				}

				if info.IsDir() {
					if c.String("images-dir") != "" && c.Bool("extract-images") {
						return fmt.Errorf("--images-dir can only be used when converting a single file")
					}

					converted, err := processDirectory(inputPath, outputDir, c.Bool("extract-images"), c.String("images-dir"))
					if err != nil {
						return err
					}
					totalConverted += converted
					continue
				}

				outPath := c.String("output")
				if outPath == "" {
					base := strings.TrimSuffix(filepath.Base(inputPath), filepath.Ext(inputPath))
					outPath = filepath.Join(outputDir, base+".md")
				}

				if err := processSingleFile(inputPath, outPath, c.Bool("extract-images"), c.String("images-dir")); err != nil {
					return err
				}
				totalConverted++
			}

			fmt.Printf("✓ Converted %d file(s) to markdown in %s\n", totalConverted, outputDir)
			return nil
		},
	}

	if err := app.Run(os.Args); err != nil {
		log.Fatal(err)
	}
}

func processDirectory(dir, outputDir string, extractImages bool, imagesDirFlag string) (int, error) {
	var converted int

	err := filepath.WalkDir(dir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}

		if !isSupportedExtension(path) {
			return nil
		}

		outPath := buildOutputPath(dir, path, outputDir)
		if err := processSingleFile(path, outPath, extractImages, imagesDirFlag); err != nil {
			return err
		}
		converted++
		return nil
	})

	return converted, err
}

func processSingleFile(inputPath, outputPath string, extractImages bool, imagesDir string) error {
	ext := strings.ToLower(filepath.Ext(inputPath))

	switch ext {
	case ".fb2":
		converter := NewConverter()
		if imagesDir == "" && extractImages {
			ext := filepath.Ext(outputPath)
			imagesDir = strings.TrimSuffix(outputPath, ext) + "_images"
		}

		if err := converter.Convert(inputPath, outputPath, extractImages, imagesDir); err != nil {
			return fmt.Errorf("conversion failed for %s: %w", inputPath, err)
		}
	case ".epub":
		epubConverter := NewEpubConverter()
		if err := epubConverter.Convert(inputPath, outputPath); err != nil {
			return fmt.Errorf("conversion failed for %s: %w", inputPath, err)
		}
	default:
		return fmt.Errorf("unsupported file extension: %s", ext)
	}

	fmt.Printf("✓ %s -> %s\n", inputPath, outputPath)
	return nil
}

func isSupportedExtension(path string) bool {
	ext := strings.ToLower(filepath.Ext(path))
	return ext == ".fb2" || ext == ".epub"
}

func buildOutputPath(rootDir, filePath, outputDir string) string {
	rel, err := filepath.Rel(rootDir, filePath)
	if err != nil {
		rel = filepath.Base(filePath)
	}

	withoutExt := strings.TrimSuffix(rel, filepath.Ext(rel))
	safeName := strings.ReplaceAll(withoutExt, string(filepath.Separator), "_")

	return filepath.Join(outputDir, safeName+".md")
}

func preventSleep() error {
	caffeinateCmd = exec.Command("caffeinate", "-d", "-i", "-m", "-s", "-u")
	if err := caffeinateCmd.Start(); err != nil {
		return fmt.Errorf("failed to start caffeinate: %w", err)
	}
	return nil
}

func cleanupCaffeinate() {
	if caffeinateCmd != nil && caffeinateCmd.Process != nil {
		caffeinateCmd.Process.Kill()
		caffeinateCmd.Wait()
	}
}
