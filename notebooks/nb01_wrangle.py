import marimo

__generated_with = "0.23.14"
app = marimo.App(width="compact")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Wrangle

    The [National Gallery of Art](https://github.com/NationalGalleryOfArt/opendata)
    publishes its collection as a handful of CSVs. Our job: **turn them into one
    tidy table** we can explore later.

    Along the way, we'll grow a plain notebook into a reusable module and script.

    > This notebook is a set of **exercises** — fill in the `TODO`s. Solutions are
    > tucked in the 💡 accordions.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl

    NGA = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data"
    return NGA, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Meet the collection

    Four CSVs, each a different piece of the puzzle. Load one per cell and poke at it
    in the table viewer (click a column to sort, type in the search box).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `objects.csv` — one row per **artwork** (title, date, medium, type).
    """)
    return


@app.cell
def _(NGA, pl):
    objects = pl.read_csv(f"{NGA}/objects.csv", infer_schema_length=10000)
    objects
    return (objects,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `published_images.csv` — **image** URLs (IIIF thumbnails) per object.
    """)
    return


@app.cell
def _(NGA, pl):
    images = pl.read_csv(f"{NGA}/published_images.csv", infer_schema_length=10000)
    images
    return (images,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `constituents.csv` (**people**) + `objects_constituents.csv` (who did what to
    which object) — together these tell us each artwork's artist.
    """)
    return


@app.cell
def _(NGA, pl):
    constituents = pl.read_csv(f"{NGA}/constituents.csv", infer_schema_length=10000)
    obj_constituents = pl.read_csv(
        f"{NGA}/objects_constituents.csv",
        infer_schema_length=10000,
        schema_overrides={"zipcode": pl.Utf8},
    )
    constituents
    return constituents, obj_constituents


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `tsne.parquet` (**tsne**) — a 2-D map of visual similarity: each thumbnail was
    embedded with DINOv2, then reduced to x, y with t-SNE.
    """)
    return


@app.cell
def _(pl):
    tsne = pl.read_parquet(
        "https://raw.githubusercontent.com/manzt/marimo-lunch-and-learn/main/notebooks/tsne.parquet"
    )
    tsne
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Assemble one table

    Two reshaping steps are **given** — skim them. The data has several people per
    object (we keep the primary artist) and several images per object (we keep the
    primary thumbnail).
    """)
    return


@app.cell
def _(constituents, obj_constituents, pl):
    # given: one primary artist per object
    artists = (
        obj_constituents.filter(pl.col("roletype") == "artist")
        .sort("displayorder")
        .group_by("objectid")
        .first()
        .join(
            constituents.select(
                "constituentid",
                pl.col("preferreddisplayname").alias("artist"),
                pl.col("nationality").alias("artist_nationality"),
            ),
            on="constituentid",
        )
        .select("objectid", "artist", "artist_nationality")
    )
    artists
    return


@app.cell
def _(images, pl):
    # given: one primary thumbnail per object
    thumbnails = (
        images.filter((pl.col("viewtype") == "primary") & (pl.col("sequence") == 0))
        .group_by("depictstmsobjectid")
        .first()
        .select(
            pl.col("depictstmsobjectid").alias("objectid"),
            pl.col("iiifthumburl").alias("thumbnail"),
            pl.col("iiifurl").alias("iiif_url"),
            pl.col("openaccess").cast(pl.Boolean),
        )
    )
    thumbnails
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 1 — Join the tables

    `objects`, `artists`, `thumbnails`, and `tsne` all share an `objectid`. Starting
    from the `objects` selection below, chain them into one `df`:

    - attach the artist columns, then the thumbnail columns, then the `x`/`y` embedding
    - keep only artworks that actually have an image and an embedding
    """)
    return


@app.cell
def _(objects, pl):
    df = (
        objects.select(
            "objectid",
            "title",
            pl.col("displaydate").alias("date"),
            "beginyear",
            "medium",
            pl.col("classification").alias("type"),
        )
        # TODO: join `artists`, `thumbnails`, `tsne`, then drop rows with no thumbnail, x, or y
    )
    df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 1)": mo.md(
                r"""
    ```python
    df = (
        objects.select(
            "objectid", "title",
            pl.col("displaydate").alias("date"),
            "beginyear", "medium",
            pl.col("classification").alias("type"),
        )
        .join(artists, on="objectid", how="left")
        .join(thumbnails, on="objectid", how="left")
        .join(tsne, on="objectid", how="left")
        .filter(
            pl.col("thumbnail").is_not_null()
            & pl.col("x").is_not_null()
            & pl.col("y").is_not_null()
        )
        .select(pl.col("thumbnail"), pl.exclude("thumbnail")) # trick so thumbnail is first col
    )
    df
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reusable functions and classes

    So far every definition lives *inside* a cell. But we may want to *reuse* our
    pipeline in another notebook or Python script. marimo can "lift" a function or
    class out of a cell and make it a **reusable, top-level definition**. e.g.,


    ```py
    from my_notebook import my_function, MyClass
    ```

    A definition can be promoted only if it's **self-contained**. The criteria:

    - the cell holds **exactly one** function or class definition (nothing else)
    - it references **only** its own arguments, Python builtins, other reusable
      definitions, and names from the **setup cell**
    - it does **not** read variables defined by ordinary cells (no notebook state)

    When a definition breaks a rule, marimo flags it in the editor and tells you which
    fix it needs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The setup cell

    *(We'll add one together.)*

    Shared imports and constants go in a special **setup cell** that runs before every
    other cell. Whatever it defines is visible everywhere — including inside reusable
    definitions, which is how a promoted function can still reach `pl`:

    ```python
    with app.setup:
        import polars as pl
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 2 — Make three reusable definitions

    The cell below packs three definitions together, and marimo won't let you reuse
    any of them as-is. Give each its **own cell** and satisfy the criteria above — the
    in-editor hints will point the way.
    """)
    return


@app.cell
def _(pl, x):
    class Foo:
        pass

    def bar(x):
        return x

    def baz():
        return pl.DataFrame({x: [10, 20, 30]})

    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 2)": mo.md(
                r"""
    Move the shared import to a **setup cell**:

    ```python
    import polars as pl
    ```

    Then, one definition per cell:

    ```python
    class Foo:
        pass
    ```

    ```python
    def bar(x):
        return x
    ```

    ```python
    def baz():
        # a literal column name — not a notebook variable
        return pl.DataFrame({"x": [10, 20, 30]})
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 3 — Fold the pipeline into reusable `load_data`

    Combine the loading + joining from parts 1–2 into the body of a single
    `load_data()` function. Make sure `load_data()` is a **reusable function**.
    """)
    return


@app.cell
def _(pl):
    def load_data() -> pl.DataFrame:
        # TODO: load the CSVs, do the joins, and return the tidy table
        pass

    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 3)": mo.md(
                r"""
    ```python
    def load_data():
        # defined inside so the function is self-contained (reusable)
        NGA = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data"
        objects = pl.read_csv(f"{NGA}/objects.csv", infer_schema_length=10000)
        constituents = pl.read_csv(f"{NGA}/constituents.csv", infer_schema_length=10000)
        obj_constituents = pl.read_csv(
            f"{NGA}/objects_constituents.csv",
            infer_schema_length=10000,
            schema_overrides={"zipcode": pl.Utf8},
        )
        images = pl.read_csv(f"{NGA}/published_images.csv", infer_schema_length=10000)
        tsne = pl.read_parquet(
            "https://raw.githubusercontent.com/manzt/marimo-lunch-and-learn/main/notebooks/tsne.parquet"
        )

        artists = (
            obj_constituents.filter(pl.col("roletype") == "artist")
            .sort("displayorder").group_by("objectid").first()
            .join(
                constituents.select(
                    "constituentid",
                    pl.col("preferreddisplayname").alias("artist"),
                    pl.col("nationality").alias("artist_nationality"),
                ),
                on="constituentid",
            )
            .select("objectid", "artist", "artist_nationality")
        )
        thumbnails = (
            images.filter((pl.col("viewtype") == "primary") & (pl.col("sequence") == 0))
            .group_by("depictstmsobjectid").first()
            .select(
                pl.col("depictstmsobjectid").alias("objectid"),
                pl.col("iiifthumburl").alias("thumbnail"),
                pl.col("iiifurl").alias("iiif_url"),
                pl.col("openaccess").cast(pl.Boolean),
            )
        )
        return (
            objects.select(
                "objectid", "title",
                pl.col("displaydate").alias("date"),
                "beginyear", "medium",
                pl.col("classification").alias("type"),
            )
            .join(artists, on="objectid", how="left")
            .join(thumbnails, on="objectid", how="left")
            .join(tsne, on="objectid", how="left")
            .filter(
                pl.col("thumbnail").is_not_null()
                & pl.col("x").is_not_null()
                & pl.col("y").is_not_null()
            )
            .select(pl.col("thumbnail"), pl.exclude("thumbnail"))  # thumbnail first
        )
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Cache — remember expensive work

    `load_data` re-downloads 100k rows over the network each time the kernel
    restarts. marimo's cache fixes that. It's **content-addressed**, meaning that
    marimo keys the result on its understanding of your code and the data it reads,
    not just the arguments.
    """)
    return


@app.cell
def _(mo):
    import time

    @mo.persistent_cache
    def expensive(n):
        time.sleep(1)
        return n * n

    # slow the first time; instant on re-run — even after a restart
    expensive(12)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 4 — Cache `load_data`

    Add `@mo.persistent_cache` to `load_data()`, then call it. Run once, **kill and
    restart the kernel**, and watch it come back instantly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 4)": mo.md(
                r"""
    ```python
    @mo.persistent_cache
    def load_data():
        ...  # same body
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Now it's a script

    marimo notebooks are **Python programs** with deterministic execution semantics
    based on dataflow. Let's turn this notebook into a data pipeline script.

    ### 🎯 Exercise 5 — Add a cell / run as a script

    Add a cell writing our tidy dataframe to disk as a parquet file:
    """)
    return


@app.cell
def _():
    print("Writing artworks.parquet to disk...")
    # TODO, call our function and write the contents to disk
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    then kill the notebook and run as a script:

    ```bash
    uv run notebooks/nb01_wrangle.py
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
