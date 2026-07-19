import marimo

__generated_with = "0.23.14"
app = marimo.App(width="compact")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A tour of marimo

    A reactive Python notebook. We'll build this up together from scratch — the
    version you're reading is just a reference to follow along with.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Reactivity
    """)
    return


@app.cell
def _():
    a = 1
    return (a,)


@app.cell
def _():
    b = 2
    return (b,)


@app.cell
def _(a, b):
    c = a + b
    c
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    marimo reads your notebook as a **dependency graph**, not a sequence of cells.
    Change `a` or `b` and `c` re-runs automatically. Cell *order* doesn't matter —
    try the **minimap** to see the graph.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Cell types
    """)
    return


@app.cell
def _():
    import polars as pl

    athletes = pl.read_parquet(
        "https://github.com/uwdata/mosaic/raw/main/data/athletes.parquet"
    )
    athletes
    return athletes, pl


@app.cell
def _(athletes, mo):
    medals = mo.sql(
        f"""
        SELECT sport, COUNT(*) AS athletes, SUM(gold) AS gold
        FROM athletes
        GROUP BY sport
        ORDER BY gold DESC
        LIMIT 10
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three cell types: **Python** (rich DataFrame viewer above), **SQL** (DuckDB,
    can query Python variables and return a DataFrame), and **Markdown** (this cell).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. UI elements

    Interacting with a UI element automatically re-runs any cell that reads its value.
    """)
    return


@app.cell
def _(mo):
    sport = mo.ui.dropdown(["all", "aquatics", "athletics", "cycling"], value="all")
    sport
    return (sport,)


@app.cell
def _(athletes, pl, sport):
    filtered = (
        athletes
        if sport.value == "all"
        else athletes.filter(pl.col("sport") == sport.value)
    )
    filtered
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Notebook or app?

    Toggle **app view** (bottom-right) to hide code and keep only outputs — still
    fully interactive. Serve it with `marimo run nb00_tour.py`.

    ## 5. Editor features to point out

    - Variables & data-sources panels
    - Dataflow view / minimap
    - Package management (auto-install on import)
    """)
    return


if __name__ == "__main__":
    app.run()
