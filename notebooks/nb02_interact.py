import marimo

__generated_with = "0.23.14"
app = marimo.App(width="compact")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Interactivity

    In `nb01_wrangle` we built one tidy `artworks` table. Now we use marimo's
    **reactivity** with anywidget to *explore* it.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt

    from nb01_wrangle import load_data

    df = load_data()
    return alt, df, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Like traditional notebooks, marimo displays the last expression in a cell. Here we perform the aggregation in polars and plot the grouped counts with altair.
    """)
    return


@app.cell
def _(alt, df):
    counts = df.group_by("type").len().sort("len", descending=True).limit(15)

    alt.Chart(counts).mark_bar().encode(
        x=alt.X("len:Q", title="Count"),
        y=alt.Y("type:N", sort="-x", title="Type"),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 Exercise 1 — pull the constant out

    Above, `"type"` is hard-coded **twice** — in the `group_by` and in the `y`
    encoding. Pull it into a single `group_col` variable (its own cell) and use
    it in both places.

    Then change `group_col` — try `"medium"` or `"artist_nationality"` — and press ▶.
    """)
    return


@app.cell
def _():
    # 🎯 Your turn:
    # - extract hard-coded "type" into `group_col` and update plotting code
    # - try changing value to "medium"/"artist_nationality", press ▶.
    group_col = ...
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 Exercise 2 — trade the constant for a control

    Editing code to explore still means editing code. Instead:
    """)
    return


@app.cell
def _():
    # 🎯 Your turn:
    # - Make a mo.ui.dropdown of columns; point group_col at its .value
    # - Add a mo.ui.slider for how many bars to show, and use it in the chart.
    # Hint: put both controls in one cell using `mo.hstack([...])` or `mo.vstack([...])`

    _choices = ["type", "medium", "artist_nationality"]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 2)": mo.md(
                r"""
        Controls in one cell — `mo.hstack` renders them together:

        ```python
        group_dropdown = mo.ui.dropdown(
            ["type", "medium", "artist_nationality"], value="type", label="Group by"
        )
        top_k = mo.ui.slider(5, 30, value=15, label="Top K")
        mo.hstack([group_dropdown, top_k])
        ```

        Point `group_col` at the dropdown (edit the cell from Exercise 1):

        ```python
        group_col = group_dropdown.value
        ```

        And use the slider in the chart's `.head(...)`:

        ```python
        counts = df.group_by(group_col).len().sort("len", descending=True).head(top_k.value)
        ```
        """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `mo.ui.altair_chart()` — selection back to Python

    So far the UI drives Python one way. `mo.ui.altair_chart` goes the other
    direction.


    ```python

    my_chart = mo.ui.altair_chart(
        alt.Chart(...).mark_bar().encode(...)
    )
    my_chart

    ```

    ```py
    my_chart.value # reactive selection!
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 Exercise 3 — wrap your bar chart

    Take the bar chart from Exercise 1 and wrap it in `mo.ui.altair_chart(...)`.
    Display it, then read its `.value` in a **new cell** and click a bar — the
    selected rows come back to Python.
    """)
    return


@app.cell
def _():
    # 🎯 Your turn:
    # - wrap the Exercise 1 bar chart in mo.ui.altair_chart(...) and display it
    # - then, in a NEW cell, read its .value and click a bar
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 3)": mo.md(
                r"""
        ```python
        my_chart = mo.ui.altair_chart(
            alt.Chart(df.group_by(group_col).len().sort("len", descending=True))
            .mark_bar()
            .encode(
                x=alt.X("len:Q", title="Count"),
                y=alt.Y(f"{group_col}:N", sort="-x", title=group_col),
            )
        )
        my_chart
        ```

        ```python
        my_chart.value  # reactive selection!
        ```
        """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `mo.ui.matplotlib()` — same idea, more points

    `mo.ui.altair_chart` ships your data to the browser, which is great for
    aggregates but struggles with *lots of individual points*.

    Our collection has a 2-D **t-SNE embedding** of the images. For that, marimo has
    another adapter: `mo.ui.matplotlib` renders the figure server-side as a static
    image and adds a selection overlay (drag to box-select, ⇧+drag to lasso):

    ```python
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.random.randn(500)
    y = np.random.randn(500)
    plt.scatter(x, y)

    # wrap the Axes in mo.ui.matplotlib to make it reactive ⚡
    sel = mo.ui.matplotlib(plt.gca())
    sel
    ```

    ```python
    sel.value  # reactive selection
    ```
    """)
    return


@app.cell
def _(df, pl):
    import matplotlib.pyplot as plt

    # ordered largest -> smallest so we draw rarest last
    _type_order = df["type"].value_counts(sort=True)["type"].to_list()

    _palette = {
        "Print": "#4C72B0",
        "Photograph": "#DD8452",
        "Index of American Design": "#55A868",
        "Drawing": "#C44E52",
        "Portfolio": "#8172B3",
        "Sculpture": "#937860",
        "Painting": "#DA8BC3",
        "Volume": "#8C8C8C",
        "Decorative Art": "#CCB974",
        "Technical Material": "#64B5CD",
        "Time-Based Media Art": "#111111",
        "Ephemera (non-NGA)": "#E45756",
    }

    _fig, ax = plt.subplots(figsize=(6, 6), dpi=200)

    # big categories first (bottom of stack), rare last (on top)
    for _t in reversed(_type_order):
        _sub = df.filter(pl.col("type") == _t)
        ax.scatter(
            _sub["x"],
            _sub["y"],
            s=2.0,
            alpha=0.35,
            linewidths=0,
            color=_palette[_t],
            rasterized=True,
        )

    # clean framing: t-SNE axes are not meaningful
    ax.set_xticks([])
    ax.set_yticks([])
    for _spine in ax.spines.values():
        _spine.set_visible(False)
    _fig.tight_layout()
    ax.set_aspect("equal")

    ax
    return (ax,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🎯 Exercise 4 — from selection to rows

    Wrap the `ax` above in `mo.ui.matplotlib` and display it, then draw a
    selection.

    Notice: it's just the **selection geometry** (a box or lasso) — *not* your
    data. Check the [`mo.ui.matplotlib` API](https://docs.marimo.io/guides/working_with_data/plotting/#example)
    for how to map it back, and filter `df` down to the selected rows.
    """)
    return


@app.cell
def _():
    # 🎯 Your turn:
    # - wrap `ax` in mo.ui.matplotlib(...) and display it
    # - draw a selection, look at .value (geometry only!)
    # - use .value.get_mask(df["x"], df["y"]) to filter df to the selected rows
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 4)": mo.md(
                r"""
        ```python
        sel = mo.ui.matplotlib(ax)
        sel
        ```

        ```python
        sel.value  # BoxSelection / LassoSelection — geometry, not rows
        ```

        Every selection has a `.get_mask(x, y)` method — give it the plotted
        coordinates and it returns a boolean mask you can filter with:

        ```python
        df.filter(sel.value.get_mask(df["x"], df["y"]))
        ```
        """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## `mo.state` — the primitive underneath

    `mo.ui.altair_chart` and `mo.ui.matplotlib` both do the same trick: they take
    some **internal frontend state** (a brush, a lasso) and hook it back into
    marimo's reactivity.

    The primitive for doing that yourself is `mo.state`.

    `mo.state(initial)` returns a `(getter, setter)` pair. Call the setter from
    *anywhere* — a callback, another cell — and every cell that calls the getter
    re-runs:

    ```python
    get_value, set_value = mo.state(0)
    ```

    ```python
    set_value(42)   # e.g. inside a button's on_change
    ```

    ```python
    get_value()     # cells that read it re-run automatically
    ```
    """)
    return


@app.cell
def _(mo):
    # 🎯 Exercise 5 — a "random artwork" button
    # Complete the on_change: set the state to a random row of df
    # (hint: df.sample(1).to_dicts()[0])
    get_pick, set_pick = mo.state(None)

    shuffle = mo.ui.button(
        label="🎲 Random artwork",
        on_change=lambda _: ...,  # TODO
    )
    shuffle
    return (get_pick,)


@app.cell
def _(get_pick, mo):
    pick = get_pick()
    mo.vstack(
        [
            mo.image(pick["thumbnail"], width=240),
            mo.md(f"**{pick['title']}** — {pick['artist'] or 'unknown artist'}"),
        ]
    ) if pick else mo.md("_press the button to pull a random artwork into Python_")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 5)": mo.md(
                r"""
        ```python
        shuffle = mo.ui.button(
            label="🎲 Random artwork",
            on_change=lambda _: set_pick(df.sample(1).to_dicts()[0]),
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
    ## anywidget

    `mo.ui.altair_chart` and `mo.ui.matplotlib` are adapters that marimo ships
    for specific plotting libraries, and each decides for you what state comes
    back to Python (a selection).

    [anywidget](https://anywidget.dev) is a standard for writing custom
    interactive views and controls for notebooks. A widget is a class that
    declares the pieces of **state to share between Python and the browser** as
    attributes, plus a bit of JavaScript that renders them. The frontend reads
    and updates the same attributes, and both sides stay in sync. Because the
    standard is shared, a widget written this way works in Jupyter, marimo,
    VS Code, and elsewhere.

    Rather than ship an adapter per library, marimo supports the standard
    itself. `mo.ui.anywidget()` wraps a widget, collects its attributes, and
    listens for changes.

    [`jupyter-scatter`](https://github.com/flekschas/jupyter-scatter) is built
    on anywidget. It renders scatterplots with WebGL and handles millions of
    points.
    """)
    return


@app.cell
def _(df, mo):
    import jscatter

    scatter = jscatter.Scatter(x="x", y="y", color_by="type", data=df, height=500)
    w = mo.ui.anywidget(scatter.widget)
    w
    return jscatter, w


@app.cell
def _(w):
    w.value
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 6 — pluck one attribute

    `mo.ui.anywidget` listens to every attribute on the widget, more than a hundred
    for the scatter above. _Any_ of them changing re-runs the cells that read
    `w.value`.


    Often we only care about a few, or even just one — here it's `selection`.

    Widget attributes are observable. `.observe` registers a callback that runs
    when an attribute changes.

    ```python
    widget.observe(
        lambda change: print(change["new"]),
        names="selection",
    )
    ```

    Pair it with `mo.state` to bring just that attribute into marimo's
    reactivity.
    """)
    return


@app.cell
def _(df, jscatter, mo):
    s = jscatter.Scatter(x="x", y="y", color_by="type", data=df, height=500)

    get_selection, set_selection = mo.state(s.widget.selection)

    # 🎯 TODO: use s.widget.observe(...) so set_selection runs whenever
    # the widget's "selection" attribute changes

    s.widget
    return (get_selection,)


@app.cell
def _(df, get_selection):
    df[get_selection()]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 6)": mo.md(
                r"""
        ```python
        s.widget.observe(
            lambda change: set_selection(change["new"]), names="selection"
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
    That small pattern is the whole bridge. A widget attribute changes, an observer
    sets `mo.state`, and cells that read the getter re-run.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
