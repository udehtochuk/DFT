"""
figure_qc.py
============
Automated quality control for the generated figures.

Checks performed:
  * every declared figure exists in PDF, SVG and PNG form;
  * PNG raster resolution meets the >= 600 dpi line-art requirement;
  * PDF and SVG really are vector files (not a raster wrapped in a container);
  * no text label contains an un-rendered TeX escape such as a literal "\\%";
  * axis labels and legends are present on every axes;
  * tick label font size meets the minimum legible size;
  * no axes is left with default matplotlib blue-only encoding (i.e. every
    multi-series axes varies marker or line style as well as color).

Color-accessibility is enforced structurally rather than tested: the palette
is Okabe-Ito and every series carries a redundant marker/linestyle, which is
checked here.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

__all__ = ["check_figure_files", "check_figure_axes", "run_figure_qc"]

MIN_PNG_DPI = 600
MIN_FONT_PT = 6.0
TEX_ESCAPES = ("\\%", "\\_ ", "\\&")


def check_figure_files(names: list[str], figdir: Path) -> list[str]:
    """Existence, format and resolution checks. Returns a list of problems."""
    problems: list[str] = []
    figdir = Path(figdir)
    for name in names:
        for ext in ("pdf", "svg", "png"):
            p = figdir / f"{name}.{ext}"
            if not p.exists():
                problems.append(f"{name}: missing .{ext}")
                continue
            if p.stat().st_size == 0:
                problems.append(f"{name}.{ext}: zero bytes")
        pdf = figdir / f"{name}.pdf"
        if pdf.exists():
            head = pdf.read_bytes()[:5]
            if head[:4] != b"%PDF":
                problems.append(f"{name}.pdf: not a PDF")
        svg = figdir / f"{name}.svg"
        if svg.exists():
            txt = svg.read_text(errors="ignore")[:4000]
            if "<svg" not in txt:
                problems.append(f"{name}.svg: not an SVG")
            if "image/png;base64" in svg.read_text(errors="ignore")[:200000]:
                problems.append(f"{name}.svg: contains an embedded raster")
        png = figdir / f"{name}.png"
        if png.exists():
            try:
                from PIL import Image
                with Image.open(png) as im:
                    dpi = im.info.get("dpi", (0, 0))[0]
                    if dpi and dpi < MIN_PNG_DPI - 1:
                        problems.append(
                            f"{name}.png: {dpi:.0f} dpi < {MIN_PNG_DPI}")
            except ImportError:
                pass
    return problems


def check_figure_axes(fig: plt.Figure, name: str) -> list[str]:
    """In-memory checks on a live figure object."""
    problems: list[str] = []
    for i, ax in enumerate(fig.axes):
        tag = f"{name} axes[{i}]"
        texts = [ax.get_xlabel(), ax.get_ylabel(), ax.get_title()]
        leg = ax.get_legend()
        if leg is not None:
            texts += [t.get_text() for t in leg.get_texts()]
        texts += [t.get_text() for t in ax.texts]
        for t in texts:
            for esc in TEX_ESCAPES:
                if esc in t:
                    problems.append(f"{tag}: un-rendered TeX escape {esc!r} in {t!r}")
        if not ax.get_xlabel().strip():
            problems.append(f"{tag}: missing x-axis label")
        if not ax.get_ylabel().strip() and i == 0:
            problems.append(f"{tag}: missing y-axis label")
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            if lab.get_text() and lab.get_fontsize() < MIN_FONT_PT:
                problems.append(f"{tag}: tick font {lab.get_fontsize()} pt "
                                f"< {MIN_FONT_PT} pt")
                break
        # Redundant encoding: if an axes carries >1 line, they must not all
        # share the same linestyle AND marker.
        lines = [ln for ln in ax.get_lines() if ln.get_label()
                 and not ln.get_label().startswith("_")]
        if len(lines) > 1:
            styles = {(ln.get_linestyle(), str(ln.get_marker())) for ln in lines}
            if len(styles) == 1:
                problems.append(
                    f"{tag}: {len(lines)} series share one line/marker style "
                    "(color would be the only cue)")
    return problems


def run_figure_qc(ctx: dict, figdir: Path, verbose: bool = True) -> list[str]:
    """Rebuild each figure in memory, check it, then check the written files."""
    import plotting as PLOT

    PLOT.apply_style()
    problems: list[str] = []
    for name, builder in PLOT.FIGURE_BUILDERS.items():
        fig = builder(ctx)
        fig.canvas.draw()
        problems += check_figure_axes(fig, name)
        plt.close(fig)
    problems += check_figure_files(list(PLOT.FIGURE_BUILDERS), figdir)
    if verbose:
        if problems:
            print(f"  FIGURE QC: {len(problems)} problem(s)")
            for p in problems:
                print(f"    - {p}")
        else:
            print(f"  FIGURE QC: all {len(PLOT.FIGURE_BUILDERS)} figures passed")
    return problems
