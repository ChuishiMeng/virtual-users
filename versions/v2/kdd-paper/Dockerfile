# Dockerfile for compiling KDD paper
# Build: docker build -t kdd-paper .
# Run: docker run --rm -v $(pwd):/paper kdd-paper

FROM texlive/texlive:latest

WORKDIR /paper

# Install required packages
RUN tlmgr update --self && \
    tlmgr install acmart booktabs tikz amsmath amssymb algorithm algorithmic multirow subcaption

# Copy paper files
COPY main.tex references.bib ./

# Compile paper
RUN pdflatex -interaction=nonstopmode main.tex && \
    bibtex main && \
    pdflatex -interaction=nonstopmode main.tex && \
    pdflatex -interaction=nonstopmode main.tex

# Output will be in /paper/main.pdf
CMD ["cp", "main.pdf", "/output/"]
