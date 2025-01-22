
def configure_button_styles(root):
    style = root.style

    style.configure(
        "Generic.TButton",
        font=("Roboto Mono", 11),
        padding=(8, 5),
        background="#E0E0E0",
        foreground="black",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "Generic.TButton",
        background=[
            ("active", "#B3B3B3"),
            ("disabled", "gray80")
        ],
        foreground=[
            ("active", "black"),
            ("disabled", "black")
        ],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "GenerateGraph.TButton",
        font=("Roboto Mono", 11),
        padding=(8, 5),
        background="lightgreen",
        foreground="black",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "GenerateGraph.TButton",
        background=[
            ("disabled", "gray80"),
            ("active", "green")
        ],
        foreground=[
            ("disabled", "black"),
            ("active", "white")
        ],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "BrowseOrange.TButton",
        font=("Roboto Mono", 11),
        padding=(8, 5),
        background="#FFD580",
        foreground="black",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "BrowseOrange.TButton",
        background=[("active", "orange")],
        foreground=[("active", "black")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "XRemove.TButton",
        font=("Roboto Mono", 8),
        padding=(1, 1),
        background="#E3E3E3",
        foreground="black",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "XRemove.TButton",
        background=[("active", "#B0B0B0")],
        foreground=[("active", "black")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "OkButton.TButton",
        font=("Roboto Mono", 12, "normal"),
        padding=(12, 8),
        background="silver",
        foreground="black",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "OkButton.TButton",
        background=[("active", "lightgray")],
        foreground=[("active", "black")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "Settings.TButton",
        font=("Roboto Mono", 18, "normal"),
        padding=(0, 0),
        background="white",
        foreground="#D2691E",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "Settings.TButton",
        background=[("active", "white")],
        foreground=[("active", "orange")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "OptimizeOn.TButton",
        font=("Roboto Mono", 18, "normal"),
        padding=(0, 0),
        background="white",
        foreground="green",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "OptimizeOn.TButton",
        background=[("active", "white")],
        foreground=[("active", "lime")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "OptimizeOff.TButton",
        font=("Roboto Mono", 18, "normal"),
        padding=(0, 0),
        background="white",
        foreground="gray",
        anchor="center",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        focuscolor="none",
    )
    style.map(
        "OptimizeOff.TButton",
        background=[("active", "white")],
        foreground=[("active", "lightgray")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "Resolution.TButton",
        font=("Roboto Mono", 11, "normal"),
        padding=(8, 5),
        background="white",
        foreground="gray",
        anchor="center",
        borderwidth=2,
        relief="solid",
        highlightthickness=2,
        focuscolor="none"
    )
    style.map(
        "Resolution.TButton",
        background=[("active", "white")],
        foreground=[("active", "black")],
        highlightcolor=[("focus", "none"), ("!focus", "none")],
        highlightbackground=[("focus", "none"), ("!focus", "none")],
        focuscolor=[("focus", "none"), ("!focus", "none")],
        bordercolor=[("focus", "none"), ("!focus", "none")],
        relief=[("focus", "solid"), ("!focus", "solid")]
    )
    # ***********************************************************************
    style.configure(
        "InfoLabel.TLabel",
        font=("Roboto Mono", 18, "bold"),
        foreground="lightblue",
        background="white",
        anchor="center",
    )

    # ************************************************************************************************
    #                       Config UI Styles
    # ************************************************************************************************
    style.configure(
        "Config.TLabel",
        font=("Roboto Mono", 10, "normal"),
        foreground="black",
        background="white",
        anchor="w",
    )

    # -------------------- Entry Style (Config.TEntry) --------------------
    style.configure(
        "Config.TEntry",
        padding=(5, 2),
        foreground="black",
        fieldbackground="white",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        highlightcolor="none",
        insertcolor="black",
    )
    style.map(
        "Config.TEntry",
        background=[("readonly", "white"), ("disabled", "gray90")],
        foreground=[("disabled", "gray50")],
        bordercolor=[
            ("focus", "gray70"),
            ("hover", "gray70"),
            ("!focus", "gray80"),
        ],
        highlightcolor=[("focus", "none"), ("!focus", "none")]
    )

    # -------------------- Combobox Style (Config.TCombobox) --------------------

    style.configure(
        "Config.TCombobox",
        padding=(5, 2),
        foreground="black",
        background="white",
        borderwidth=0,
        relief="flat",
        highlightthickness=0,
        highlightcolor="none"
    )

    style.map(
        "Config.TCombobox",
        fieldbackground=[("readonly", "white"), ("!readonly", "white")],
        foreground=[("disabled", "gray50")],
        bordercolor=[
            ("focus invalid", "gray80"),
            ("invalid", "gray80"),
            ("focus", "gray80"),
            ("hover", "gray80"),
            ("active", "gray80"),
            ("!focus", "gray80"),
        ],
        highlightcolor=[
            ("focus invalid", "none"),
            ("invalid", "none"),
            ("focus", "none"),
            ("hover", "none"),
            ("active", "none"),
            ("!focus", "none"),
        ],
        arrowcolor=[
            ("focus", "black"),
            ("hover", "black"),
            ("active", "black"),
            ("!focus", "black"),
        ],
        background=[("focus", "white"), ("hover", "white"), ("active", "white"), ("!focus", "white")],
    )
