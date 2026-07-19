import marimo

__generated_with = "0.23.14"
app = marimo.App(width="compact")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Build your own widget

    In `nb02_interact` we used `jupyter-scatter`, a widget someone else wrote. Now we
    write our own. There are two core APIs on the front end:

    - `el`, the output element in the page to render into
    - `model`, the shared state, for communicating with Python

    and **traitlets** on the Python side to declare that shared state.

    > Exercises as usual. Fill in the `TODO`s; 💡 solutions in the accordions.
    """)
    return


@app.cell
def _():
    import anywidget
    import marimo as mo
    import traitlets

    return anywidget, mo, traitlets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Hello, widget

    A widget is a Python class with `_esm`, a JavaScript module that exports a
    `render` function. The front end calls `render` whenever the widget is
    displayed:

    ```python
    class MyWidget(anywidget.AnyWidget):
        _esm = '''
        function render({ model, el }) { ... }
        export default { render };
        '''
    ```

    ### 🎯 Exercise 1 — run some JavaScript

    Use `console.log(...)` to print "Hello from anywidget!" to the browser
    console, then open the developer tools to find it (`Cmd+Option+J` on Mac,
    `Ctrl+Shift+J` on Windows/Linux). `console.log` is your `print` for the
    front end. Keep it handy for debugging.
    """)
    return


@app.cell
def _(anywidget):
    class LogWidget(anywidget.AnyWidget):
        _esm = """
        function render() {
          console.log("hello")
        }
        export default { render };
        """

    LogWidget()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 1)": mo.md(
                r"""
    ```javascript
    function render() {
      console.log("Hello from anywidget!");
    }
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 2 — put something on the screen

    Nothing displayed yet. `render` receives `el`, the widget's output element.
    Create elements with `document.createElement` and add them with
    `el.appendChild`:

    ```javascript
    const p = document.createElement("p");
    p.innerText = "Hello, anywidget";
    el.appendChild(p);
    ```

    Make an `h1` element that says "Hello, anywidget!" and append it.
    """)
    return


@app.cell
def _(anywidget):
    class HelloWidget(anywidget.AnyWidget):
        _esm = """
        function render({ el }) {
          // 🎯 TODO: create an h1 that says "Hello, anywidget!" and append it
        }
        export default { render };
        """

    HelloWidget()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 2)": mo.md(
                r"""
    ```javascript
    function render({ el }) {
      const h1 = document.createElement("h1");
      h1.innerText = "Hello, anywidget!";
      el.appendChild(h1);
    }
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 3 — state from Python

    To change that text we would have to edit the `_esm` string. Instead,
    declare shared state with a **traitlet**:

    ```python
    class Widget(anywidget.AnyWidget):
        _esm = "..."
        name = traitlets.Unicode().tag(sync=True)  # sync=True shares it
    ```

    The front end reads it through the `model`:

    ```javascript
    function render({ model, el }) {
      const name = model.get("name");
    }
    ```

    Add a `name` traitlet to the widget below and display "Hello, &lt;name&gt;!".
    """)
    return


@app.cell
def _(anywidget):
    class NamedWidget(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          const h1 = document.createElement("h1");
          h1.innerText = "Hello, anywidget!";
          el.appendChild(h1);
        }
        export default { render };
        """
        # 🎯 TODO: declare a `name` traitlet and use it in the front end

    NamedWidget()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 3)": mo.md(
                r"""
    ```python
    class NamedWidget(anywidget.AnyWidget):
        _esm = '''
        function render({ model, el }) {
          const h1 = document.createElement("h1");
          h1.innerText = `Hello, ${model.get("name")}!`;
          el.appendChild(h1);
        }
        export default { render };
        '''
        name = traitlets.Unicode().tag(sync=True)

    NamedWidget(name="SciPy")
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. A click counter

    So far data flows one way, Python to the front end. The counter closes the
    loop. Two new pieces:

    Listen for clicks with `addEventListener`:

    ```javascript
    btn.addEventListener("click", () => { ... });
    ```

    Send state back to Python with `model.set` and `model.save_changes`:

    ```javascript
    model.set("count", model.get("count") + 1);
    model.save_changes();
    ```

    ### 🎯 Exercise 4 — count clicks

    Turn the widget below into a button that reads "Count is &lt;count&gt;" and
    increments `count` in Python on every click.
    """)
    return


@app.cell
def _(anywidget, traitlets):
    class ClickCounter(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          const btn = document.createElement("button");
          btn.innerText = `Count is ${model.get("count")}`;
          // 🎯 TODO: increment `count` in Python when the button is clicked
          el.appendChild(btn);
        }
        export default { render };
        """
        count = traitlets.Int(0).tag(sync=True)

    click_counter = ClickCounter()
    click_counter
    return (click_counter,)


@app.cell
def _(click_counter):
    click_counter.count  # click a few times, then re-run this cell
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 4)": mo.md(
                r"""
    ```javascript
    btn.addEventListener("click", () => {
      model.set("count", model.get("count") + 1);
      model.save_changes();
    });
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 5 — respond to Python

    There is a bug. Clicks update Python, but setting `count` *from* Python does
    not update the button text. Try the slider below. Nothing happens.

    The front end needs to listen for model changes, the same events we observed
    from Python in `nb02_interact`:

    ```javascript
    model.on("change:count", () => { ... });
    ```

    Update the button text whenever `count` changes. Treat the model as the
    source of truth, and the widget stays correct no matter which side sets the
    state.
    """)
    return


@app.cell
def _(anywidget, traitlets):
    class Counter(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          const btn = document.createElement("button");
          btn.innerText = `Count is ${model.get("count")}`;
          btn.addEventListener("click", () => {
            model.set("count", model.get("count") + 1);
            model.save_changes();
          });
          // 🎯 TODO: update the text when `count` changes on the model
          el.appendChild(btn);
        }
        export default { render };
        """
        count = traitlets.Int(0).tag(sync=True)

    counter = Counter()
    counter
    return (counter,)


@app.cell
def _(mo):
    slider = mo.ui.slider(0, 100, label="Drive the counter")
    slider
    return (slider,)


@app.cell
def _(counter, slider):
    counter.count = slider.value
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 5)": mo.md(
                r"""
    ```javascript
    model.on("change:count", () => {
      btn.innerText = `Count is ${model.get("count")}`;
    });
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Style it

    `_css` takes a stylesheet. Styles apply to the whole document, so scope them
    by adding a class to `el` and writing selectors under it:
    """)
    return


@app.cell
def _(anywidget, traitlets):
    class StyledCounter(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          const btn = document.createElement("button");
          const update = () => (btn.innerText = `Count is ${model.get("count")}`);
          btn.addEventListener("click", () => {
            model.set("count", model.get("count") + 1);
            model.save_changes();
          });
          model.on("change:count", update);
          update();
          el.classList.add("styled-counter");
          el.appendChild(btn);
        }
        export default { render };
        """
        _css = """
        .styled-counter button {
          font-size: 1.25rem;
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 0.25rem;
          background-color: #ea580c;
          color: white;
        }
        .styled-counter button:hover { background-color: #9a3412; }
        """
        count = traitlets.Int(0).tag(sync=True)

    StyledCounter()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🎯 Exercise 6 — third-party libraries

    `_esm` is a standard JavaScript module, so you can import dependencies
    straight from a URL:

    ```javascript
    import confetti from "https://esm.sh/canvas-confetti@1";

    confetti();  // 🎉
    ```

    Make the counter fire confetti whenever `count` changes.

    **Bonus.** `confetti({ angle: <number> })` aims the cannon. Do something fun
    with the count.
    """)
    return


@app.cell
def _(anywidget, traitlets):
    class ConfettiCounter(anywidget.AnyWidget):
        _esm = """
        function render({ model, el }) {
          const btn = document.createElement("button");
          const update = () => (btn.innerText = `Count is ${model.get("count")}`);
          btn.addEventListener("click", () => {
            model.set("count", model.get("count") + 1);
            model.save_changes();
          });
          model.on("change:count", update);
          // 🎯 TODO: confetti on every change to `count`
          update();
          el.appendChild(btn);
        }
        export default { render };
        """
        count = traitlets.Int(0).tag(sync=True)

    ConfettiCounter()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "💡 Solution (Exercise 6)": mo.md(
                r"""
    ```javascript
    import confetti from "https://esm.sh/canvas-confetti@1";

    function render({ model, el }) {
      // ...
      model.on("change:count", () => {
        update();
        confetti({ angle: model.get("count") % 360 });
      });
      // ...
    }
    ```
    """
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Those are the fundamentals. In `nb04_explore` we put them to work on a real
    widget, a gallery for browsing the collection.
    """)
    return


if __name__ == "__main__":
    app.run()
