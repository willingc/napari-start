import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Explore

    Everything here is prebuilt from the pieces we made: `load_data` from
    `nb01_wrangle`, the `mo.state` bridge from `nb02_interact`, and a
    `GalleryWidget` written with the fundamentals from `nb03_build`. This
    notebook is a playground.

    > For live front-end editing, launch with hot module replacement:
    >
    > ```bash
    > ANYWIDGET_HMR=1 uv run marimo edit notebooks/
    > ```
    """)
    return


@app.cell
def _():
    import pathlib

    import anywidget
    import marimo as mo
    import polars as pl
    import traitlets

    # from nb01_wrangle import load_data

    df = pl.read_parquet("./notebooks/data/artworks.parquet")
    return anywidget, df, mo, pathlib, pl, traitlets


@app.cell
def _(df, mo):
    import jscatter

    scatter = jscatter.Scatter(
        x="x", y="y", color_by="type", data=df, height=480
    )

    get_selection, set_selection = mo.state(scatter.widget.selection)
    scatter.widget.observe(
        lambda change: set_selection(change["new"]), names="selection"
    )

    scatter.widget
    return (get_selection,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The gallery

    A custom anywidget for browsing artworks. The same pieces as `nb03_build`,
    at full size:

    - `_esm` and `_css` point at **files** (`gallery.js`, `gallery.css`)
    - the DataFrame crosses to the front end as a binary **Arrow** buffer
    - a `selected` traitlet syncs clicks back to Python

    Click a card to select it, shift-click for multiple, right-click for a
    detail view.
    """)
    return


@app.cell
def _(anywidget, pathlib, pl, traitlets):
    HERE = pathlib.Path(__file__).parent

    class GalleryWidget(anywidget.AnyWidget):
        _esm = HERE / "gallery.js"
        _css = HERE / "gallery.css"
        _data = traitlets.Any(b"").tag(sync=True)
        selected = traitlets.List([]).tag(sync=True)
        page_size = traitlets.Int(60).tag(sync=True)

        def __init__(self, data: pl.DataFrame, **kwargs):
            buf = data.write_ipc(None)
            assert buf is not None
            kwargs["_data"] = buf.getvalue()
            super().__init__(**kwargs)

    return (GalleryWidget,)


@app.cell
def _(GalleryWidget, df, get_selection):
    gallery = GalleryWidget(data=df[get_selection()], page_size=20)
    gallery
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Make it yours

    With `ANYWIDGET_HMR=1`, edits to `gallery.js` and `gallery.css` show up
    **without re-running any cells**. Try it: open `gallery.css`, change the
    selected border color (`.gallery-card.selected`) or the card
    `border-radius`, and save.

    From here the widget is ours to change. What should it do next?
    """)
    return


if __name__ == "__main__":
    app.run()
