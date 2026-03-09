#!/bin/bash
# Compilation script for KDD paper
# Run from the kdd-paper directory

set -e

echo "=== Compiling VirtualSurvey Paper ==="

# Method 1: Direct compilation (if pdflatex is available)
if command -v pdflatex &> /dev/null; then
    echo "Using pdflatex..."
    pdflatex -interaction=nonstopmode main.tex
    bibtex main
    pdflatex -interaction=nonstopmode main.tex
    pdflatex -interaction=nonstopmode main.tex
    echo "✓ Compilation complete: main.pdf"

# Method 2: Docker compilation
elif command -v docker &> /dev/null; then
    echo "Using Docker..."
    docker build -t kdd-paper .
    mkdir -p output
    docker run --rm -v "$(pwd)/output:/output" kdd-paper
    mv output/main.pdf main.pdf
    echo "✓ Compilation complete: main.pdf"

else
    echo "❌ No LaTeX compiler found!"
    echo ""
    echo "Please use one of these options:"
    echo "1. Install TeX Live or MacTeX"
    echo "2. Use Overleaf (https://www.overleaf.com)"
    echo "3. Use Docker with the provided Dockerfile"
    exit 1
fi

# Check page count
if [ -f main.pdf ]; then
    if command -v pdfinfo &> /dev/null; then
        pages=$(pdfinfo main.pdf | grep "Pages:" | awk '{print $2}')
        echo ""
        echo "=== Page Count ==="
        echo "Total pages: $pages"
        if [ $pages -ge 9 ] && [ $pages -le 12 ]; then
            echo "✓ Page count OK (target: 9-12 pages excluding references)"
        else
            echo "⚠ Warning: Page count outside target range"
        fi
    fi
fi

echo ""
echo "=== Next Steps ==="
echo "1. Review main.pdf"
echo "2. Check all figures and tables"
echo "3. Verify references"
echo "4. Submit to KDD 2026"
