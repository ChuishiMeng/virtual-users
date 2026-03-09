# Using Overleaf to Compile This Paper

## Quick Start

1. **Create Overleaf Project**
   - Go to https://www.overleaf.com
   - Click "New Project" → "Upload Project"
   - Upload `kdd-paper.zip` (see below)

2. **Or Copy Files Manually**
   - Create new blank project
   - Upload `main.tex` and `references.bib`
   - Replace default content

## Prepare Files for Overleaf

Run this command to create a zip file:

```bash
cd research/virtual-users/kdd-paper
zip -r kdd-paper.zip main.tex references.bib README.md
```

## Overleaf Settings

### Compiler Settings
- **Menu** (top left) → **Settings**
- **Compiler**: pdfLaTeX
- **Main document**: main.tex

### ACM Template Setup

Overleaf has the ACM template built-in, but you may need to add `acmart.cls`:

**Option 1: Use Built-in (Recommended)**
- The `acmart` package is available on Overleaf by default
- No additional setup needed

**Option 2: Manual Upload**
- Download from: https://www.acm.org/publications/proceedings-template
- Upload `acmart.cls` to your project

## Compilation Steps in Overleaf

1. Click "Recompile" button
2. Wait for compilation (usually 30-60 seconds)
3. Download PDF using "Download PDF" button

## Troubleshooting

### Error: acmart.cls not found

Solution: Add this to your preamble (before `\begin{document}`):

```latex
\usepackage{acmart}
```

Or upload the `acmart.cls` file manually.

### Bibliography Not Showing

1. Make sure `references.bib` is uploaded
2. Recompile twice (BibTeX needs two passes)
3. Check for BibTeX errors in the log

### Package Errors

If you see package errors, try:
1. Clear cached files: Menu → "Delete cached files"
2. Recompile

## Alternative: Quick LaTeX Online

If Overleaf is slow, try:
- **Papeeria**: https://papeeria.com
- **CoCalc**: https://cocalc.com

Both support ACM templates.

## Sharing the Project

To share with collaborators:
1. Click "Share" button
2. Enter email addresses
3. Set permissions (View/Edit)

## Version Control

Overleaf auto-saves. To version locally:
1. Menu → "Download Project as Zip"
2. Or enable GitHub sync (Menu → Sync with GitHub)

## Checklist Before Submission

- [ ] Page count: 9-12 pages
- [ ] All figures rendered correctly
- [ ] References compiled
- [ ] No warnings in log
- [ ] Anonymous author information
- [ ] Keywords included
- [ ] Abstract 150-200 words

## Need Help?

- Overleaf Documentation: https://www.overleaf.com/learn
- ACM Template Guide: https://www.acm.org/publications/proceedings-template
- LaTeX Help: https://en.wikibooks.org/wiki/LaTeX

## Estimated Compilation Time

- **First compile**: 1-2 minutes
- **Subsequent**: 30-60 seconds
- **With errors**: 2-5 minutes (debugging)
