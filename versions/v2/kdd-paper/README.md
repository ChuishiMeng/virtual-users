# VirtualSurvey: KDD 2026 Paper

This directory contains the LaTeX source code for the KDD 2026 submission:
**"VirtualSurvey: A Persona-Based LLM Framework for Automated Survey Research"**

## File Structure

```
kdd-paper/
├── main.tex           # Main LaTeX document
├── references.bib     # Bibliography file (BibTeX format)
├── main.pdf           # Compiled PDF (generated)
├── README.md          # This file
└── figures/           # Figure directory (if needed)
```

## Compilation Requirements

To compile this paper, you need:

1. **LaTeX Distribution** with ACM template support:
   - **MacTeX** (macOS): `brew install --cask mactex`
   - **TeX Live** (Linux): `sudo apt-get install texlive-full`
   - **MiKTeX** (Windows): Download from https://miktex.org/

2. **Required Packages** (usually included in full installation):
   - `acmart` - ACM article class
   - `booktabs` - Professional tables
   - `tikz` - Diagrams
   - `amsmath, amssymb` - Math support

## How to Compile

### Option 1: Using pdfLaTeX (Recommended)

```bash
# Compile with pdfLaTeX and BibTeX
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Option 2: Using latexmk (Automated)

```bash
latexmk -pdf main.tex
```

### Option 3: Using XeLaTeX (if needed)

```bash
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

## Paper Specifications

- **Format**: ACM SIGCONF (double column)
- **Font**: Times New Roman, 9pt
- **Page Limit**: 9-12 pages (excluding references)
- **Submission**: Anonymous (nonarchival mode)

## Notes

1. **Anonymous Submission**: The paper uses `nonarchival` option for anonymous review.
   After acceptance, remove `nonarchival` and add author information.

2. **TikZ Figures**: The system architecture figure uses TikZ for vector graphics.
   No external image files needed.

3. **Bibliography**: Uses ACM-Reference-Format style with BibTeX.

4. **Compilation Order**: Must run BibTeX between LaTeX compilations for proper citations.

## Troubleshooting

### Missing ACM Template

If `acmart.cls` is missing, download from:
https://www.acm.org/publications/proceedings-template

Or use CTAN package manager:
```bash
tlmgr install acmart
```

### Bibliography Not Showing

Make sure to run the full compilation sequence:
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Font Issues

If Times New Roman is unavailable, the system will use available serif fonts.
For exact font matching on Linux:
```bash
sudo apt-get install texlive-fonts-extra
```

## Version History

- v1.0 (2026-02-17): Initial submission version

## Contact

For questions about compilation, contact the corresponding author after de-anonymization.
