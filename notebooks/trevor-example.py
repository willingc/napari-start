# /// script
# requires-python = "==3.13.*"
# dependencies = [
#     "altair>=6.1.0",
#     "marimo>=0.23.6",
#     "napari[all]>=0.7.0",
#     "numpy>=2.3.5",
#     "polars>=1.40.1",
# ]
#
# [tool.uv]
# exclude-newer = "2026-05-19T14:04:08.618765-04:00"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")

with app.setup:
    import skimage as ski
    from scipy import ndimage as ndi
    import numpy as np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # marimo x napari

    This notebook demonstrates how to drive [napari](https://napari.org), a desktop
    image viewer, from marimo.

    napari is a Qt application — it draws native desktop windows rather than browser
    HTML, so the viewer doesn't render inline as a marimo cell output. Instead it
    lives in its own window beside the notebook, driven by marimo's reactivity
    graph.
    """)
    return


@app.function
def segment_nuclei(image, sigma):
    blurred = ski.filters.gaussian(
        image.astype(np.float32), sigma=sigma, preserve_range=True
    )
    binary = blurred > ski.filters.threshold_otsu(blurred)
    binary = ski.morphology.remove_small_holes(binary, max_size=64)
    binary = ski.morphology.remove_small_objects(binary, max_size=100)

    distance = ndi.distance_transform_edt(binary)
    peaks = ski.feature.peak_local_max(
        distance, min_distance=10, labels=binary
    )
    markers = np.zeros(distance.shape, dtype=np.int32)
    markers[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
    return ski.segmentation.watershed(-distance, markers, mask=binary).astype(
        np.int32
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `segment_nuclei` takes an intensity image and a smoothing σ, and returns a
    labelled array where each connected region is one nucleus.

    It's also a [reusable function](https://docs.marimo.io/guides/reusing_functions/):
    because marimo notebooks are plain Python files, every top-level definition
    can be imported from any other Python module.

    ```python
    # some other python file
    from my_notebook import segment_nuclei

    labels = segment_nuclei(image, sigma=1.5)
    ```

    The rest of the notebook is the rig used to design and tune this one function.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup

    A small amount of setup is needed for napari to coexist with marimo's asyncio
    loop. Copy the cell below into your own notebook — it pumps Qt events from a
    background task so the viewer stays responsive without blocking the kernel.
    """)
    return


@app.cell
def _():
    import sys
    import asyncio
    from qtpy.QtWidgets import QApplication

    # Create QApplication on the kernel main thread
    qapp = QApplication.instance() or QApplication(sys.argv)


    # Pump Qt events from marimo's asyncio loop.
    async def _qt_pump_coro():
        while True:
            qapp.processEvents()
            await asyncio.sleep(0.01)


    # Must precede any napari import
    qt_pump_task = asyncio.create_task(_qt_pump_coro())
    import napari

    return (napari,)


@app.cell
def _(napari):
    import polars as pl
    import altair as alt
    import marimo as mo

    raw = ski.data.cells3d()
    Z = 30  # in-focus nuclei plane
    nuclei_2d = raw[Z, 0]
    membranes_2d = raw[Z, 1]

    viewer = napari.current_viewer() or napari.Viewer()
    viewer.layers.clear()
    viewer.add_image(
        nuclei_2d, name="nuclei", colormap="cyan", blending="additive"
    )
    viewer.add_image(
        membranes_2d, name="membranes", colormap="magenta", blending="additive"
    )
    viewer.reset_view()
    return alt, mo, nuclei_2d, pl, viewer


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploring the segmentation

    The slider drives `segment_nuclei`, whose output is pushed into napari as a
    Labels layer and into a scatter plot of per-nucleus features.
    """)
    return


@app.cell
def _(mo):
    sigma = mo.ui.slider(
        0, 5, step=0.1, value=1.5, label="Gaussian σ", show_value=True
    )
    sigma
    return (sigma,)


@app.cell
def _(mo, nuclei_2d, sigma):
    labels = segment_nuclei(nuclei_2d, sigma.value)
    mo.md(f"**{int(labels.max())}** nuclei detected")
    return (labels,)


@app.cell
def _(labels, viewer):
    # create or update the labels in the viewer
    if "labels" in viewer.layers:
        viewer.layers["labels"].data = labels
    else:
        viewer.add_labels(labels, name="labels", opacity=0.5)
    return


@app.cell
def _(alt, df):
    alt.Chart(df).mark_circle(size=80, opacity=0.7, color="steelblue").encode(
        x=alt.X("area:Q"),
        y=alt.Y("eccentricity:Q"),
        tooltip=["label", "area", "eccentricity", "mean_intensity"],
    )
    return


@app.cell
def _(labels, nuclei_2d, pl):
    df = pl.DataFrame(
        ski.measure.regionprops_table(
            labels,
            intensity_image=nuclei_2d,
            properties=(
                "label",
                "area",
                "eccentricity",
                "mean_intensity",
                "solidity",
                "perimeter",
            ),
        )
    )
    df
    return (df,)


if __name__ == "__main__":
    app.run()

