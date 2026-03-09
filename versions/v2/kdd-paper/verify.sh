#!/bin/bash
# Verification script for KDD paper project

echo "=== Verifying KDD 2026 Paper Project ==="
echo ""

errors=0

# Check main files
echo "📁 Checking main files..."
for file in main.tex references.bib; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file MISSING"
        errors=$((errors+1))
    fi
done

# Check documentation
echo ""
echo "📚 Checking documentation..."
for file in README.md OVERLEAF.md SUMMARY.md CHECKLIST.md INDEX.md compile.sh; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file MISSING"
        errors=$((errors+1))
    fi
done

# Check LaTeX structure
echo ""
echo "🔍 Checking LaTeX structure..."
if grep -q "\\\\begin{document}" main.tex; then
    echo "  ✓ Document structure OK"
else
    echo "  ✗ Document structure broken"
    errors=$((errors+1))
fi

# Check sections
echo ""
echo "📖 Checking sections..."
sections="Introduction|Related Work|Preliminaries|Method|Experiments|Results|Discussion|Conclusion"
for section in Introduction "Related Work" Preliminaries Method Experiments Results Discussion Conclusion; do
    if grep -q "section{$section}" main.tex; then
        echo "  ✓ $section section present"
    else
        echo "  ✗ $section section MISSING"
        errors=$((errors+1))
    fi
done

# Check tables
echo ""
echo "📊 Checking tables..."
table_count=$(grep -c "\\\\begin{table}" main.tex)
if [ $table_count -ge 3 ]; then
    echo "  ✓ $table_count tables found (need ≥3)"
else
    echo "  ✗ Only $table_count tables (need ≥3)"
    errors=$((errors+1))
fi

# Check figures
echo ""
echo "🎨 Checking figures..."
if grep -q "\\\\begin{figure}" main.tex || grep -q "tikzpicture" main.tex; then
    echo "  ✓ Figure(s) present"
else
    echo "  ⚠ No figures found (may be OK)"
fi

# Check bibliography
echo ""
echo "📖 Checking bibliography..."
if [ -f references.bib ] && [ -s references.bib ]; then
    bib_entries=$(grep -c "@" references.bib)
    echo "  ✓ $bib_entries bibliography entries"
else
    echo "  ✗ Bibliography missing or empty"
    errors=$((errors+1))
fi

# Check citations
echo ""
echo "🔗 Checking citations..."
if grep -q "\\\\cite{" main.tex; then
    cite_count=$(grep -o "\\\\cite{[^}]*}" main.tex | wc -l)
    echo "  ✓ $cite_count citations in text"
else
    echo "  ⚠ No citations found"
fi

# Summary
echo ""
echo "=== Verification Summary ==="
if [ $errors -eq 0 ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Compile PDF: ./compile.sh"
    echo "2. Or use Overleaf: See OVERLEAF.md"
    echo "3. Review output: Check page count (9-12)"
    exit 0
else
    echo "❌ $errors error(s) found"
    echo "Please fix missing files/sections before submission"
    exit 1
fi
