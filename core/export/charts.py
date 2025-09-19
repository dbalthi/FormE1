from pathlib import Path

def save_plotly_figure(fig, base_path: Path):
    """
    Save a Plotly figure to PNG and PDF next to each other.
    base_path: Path without extension, e.g. artifacts/charts/mychart
    """
    png_path = base_path.with_suffix(".png")
    pdf_path = base_path.with_suffix(".pdf")
    fig.write_image(png_path, scale=2)   # requires kaleido auto-installed with plotly
    fig.write_image(pdf_path)
    return png_path, pdf_path
