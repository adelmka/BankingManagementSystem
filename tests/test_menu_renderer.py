"""
============================================================
Menu Renderer Tests
Part 1

Coverage

• Construction
• Headers
• Footers
• Empty menu
• Single option
• Multiple options
============================================================
"""

import pytest

from application.menu_renderer import MenuRenderer

# ============================================================
# Construction
# ============================================================

def test_menu_renderer_created():

    renderer = MenuRenderer()

    assert renderer is not None

# ============================================================
# Header Rendering
# ============================================================

def test_render_header(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Banking Management System"

    )

    captured = capsys.readouterr()

    assert "Banking Management System" in captured.out


def test_header_not_empty(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Main Menu"

    )

    captured = capsys.readouterr()

    assert len(captured.out.strip()) > 0

# ============================================================
# Footer Rendering
# ============================================================

def test_render_footer(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_footer()

    captured = capsys.readouterr()

    assert captured.out is not None


def test_footer_contains_separator(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_footer()

    captured = capsys.readouterr()

    assert "-" in captured.out or "=" in captured.out

# ============================================================
# Empty Menu
# ============================================================

def test_render_empty_menu(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        []

    )

    captured = capsys.readouterr()

    assert captured.out is not None


def test_empty_menu_not_crash(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu([])

    capsys.readouterr()

# ============================================================
# Single Menu Item
# ============================================================

def test_single_option(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Create Customer",

        ]

    )

    captured = capsys.readouterr()

    assert "Create Customer" in captured.out


def test_single_option_numbering(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Create Customer",

        ]

    )

    captured = capsys.readouterr()

    assert "1" in captured.out

# ============================================================
# Multiple Menu Items
# ============================================================

def test_multiple_options(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Create Customer",

            "Open Account",

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert "Create Customer" in captured.out

    assert "Open Account" in captured.out

    assert "Exit" in captured.out


def test_multiple_option_numbers(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "A",

            "B",

            "C",

        ]

    )

    captured = capsys.readouterr()

    assert "1" in captured.out

    assert "2" in captured.out

    assert "3" in captured.out

# ============================================================
# Output Integrity
# ============================================================

def test_renderer_outputs_string(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert isinstance(

        captured.out,

        str,

    )


def test_renderer_produces_output(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert len(

        captured.out,

    ) > 0


# PART 2

# ============================================================
# Output Integrity
# ============================================================

def test_renderer_outputs_string(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert isinstance(

        captured.out,

        str,

    )


def test_renderer_produces_output(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert len(

        captured.out,

    ) > 0

# ============================================================
# Alignment
# ============================================================

def test_option_alignment(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Create Customer",

            "Deposit",

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    lines = [

        line

        for line in captured.out.splitlines()

        if line.strip()

    ]

    assert len(lines) >= 3


def test_option_number_alignment(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "One",

            "Two",

            "Three",

        ]

    )

    captured = capsys.readouterr()

    assert "1" in captured.out

    assert "2" in captured.out

    assert "3" in captured.out

# ============================================================
# Long Menu Items
# ============================================================

def test_long_option(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Create Customer With Full Personal Information",

        ]

    )

    captured = capsys.readouterr()

    assert (

        "Create Customer"

        in captured.out

    )


def test_multiple_long_options(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Open Savings Account",

            "Open Current Account",

            "Open Time Deposit Account",

        ]

    )

    captured = capsys.readouterr()

    assert (

        "Savings"

        in captured.out

    )

    assert (

        "Current"

        in captured.out

    )

    assert (

        "Time Deposit"

        in captured.out

    )

# ============================================================
# Unicode Support
# ============================================================

def test_unicode_option(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "إضافة عميل",

        ]

    )

    captured = capsys.readouterr()

    assert "إضافة عميل" in captured.out


def test_unicode_title(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        ["Exit"],

        title="القائمة الرئيسية",

    )

    captured = capsys.readouterr()

    assert "القائمة الرئيسية" in captured.out

# ============================================================
# Duplicate Items
# ============================================================

def test_duplicate_options(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Deposit",

            "Deposit",

        ]

    )

    captured = capsys.readouterr()

    assert (

        captured.out.count(

            "Deposit"

        )

        == 2

    )


def test_duplicate_numbering(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "A",

            "A",

            "A",

        ]

    )

    captured = capsys.readouterr()

    assert "1" in captured.out

    assert "2" in captured.out

    assert "3" in captured.out

# ============================================================
# Separators
# ============================================================

def test_separator_rendering(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_separator()

    captured = capsys.readouterr()

    assert (

        "=" in captured.out

        or

        "-" in captured.out

    )


def test_separator_not_empty(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_separator()

    captured = capsys.readouterr()

    assert len(

        captured.out.strip()

    ) > 0

# ============================================================
# Dynamic Menu Generation
# ============================================================

def test_dynamic_menu(

    capsys,

):

    options = [

        f"Option {i}"

        for i in range(10)

    ]

    renderer = MenuRenderer()

    renderer.render_menu(

        options,

    )

    captured = capsys.readouterr()

    assert "Option 0" in captured.out

    assert "Option 9" in captured.out


def test_dynamic_menu_count(

    capsys,

):

    options = [

        f"Item {i}"

        for i in range(20)

    ]

    renderer = MenuRenderer()

    renderer.render_menu(

        options,

    )

    captured = capsys.readouterr()

    assert (

        captured.out.count(

            "Item"

        )

        == 20

    )

# ============================================================
# Styling Consistency
# ============================================================

def test_header_footer_together(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Bank"

    )

    renderer.render_footer()

    captured = capsys.readouterr()

    assert "Bank" in captured.out


def test_complete_menu_render(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Main"

    )

    renderer.render_menu(

        [

            "Deposit",

            "Withdraw",

            "Exit",

        ]

    )

    renderer.render_footer()

    captured = capsys.readouterr()

    assert "Deposit" in captured.out

    assert "Withdraw" in captured.out

    assert "Exit" in captured.out


# PART 3

# ============================================================
# None Handling
# ============================================================

def test_none_menu():

    renderer = MenuRenderer()

    with pytest.raises(

        ValueError

    ):

        renderer.render_menu(

            None

        )


def test_none_title(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ],

        title=None,

    )

    captured = capsys.readouterr()

    assert "Exit" in captured.out

# ============================================================
# Invalid Menu Items
# ============================================================

def test_non_string_option(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            123,

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert "123" in captured.out


def test_object_option(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            object(),

        ]

    )

    captured = capsys.readouterr()

    assert len(

        captured.out

    ) > 0

# ============================================================
# Repeated Rendering
# ============================================================

def test_render_same_menu_multiple_times(

    capsys,

):

    renderer = MenuRenderer()

    menu = [

        "Deposit",

        "Withdraw",

        "Exit",

    ]

    for _ in range(20):

        renderer.render_menu(

            menu,

        )

    captured = capsys.readouterr()

    assert (

        captured.out.count(

            "Deposit"

        )

        == 20

    )


def test_render_headers_multiple_times(

    capsys,

):

    renderer = MenuRenderer()

    for i in range(10):

        renderer.render_header(

            f"Menu {i}"

        )

    captured = capsys.readouterr()

    assert "Menu 9" in captured.out

# ============================================================
# Large Menus
# ============================================================

def test_render_100_options(

    capsys,

):

    renderer = MenuRenderer()

    menu = [

        f"Option {i}"

        for i in range(100)

    ]

    renderer.render_menu(

        menu,

    )

    captured = capsys.readouterr()

    assert (

        "Option 99"

        in captured.out

    )


def test_large_menu_numbering(

    capsys,

):

    renderer = MenuRenderer()

    menu = [

        f"Item {i}"

        for i in range(100)

    ]

    renderer.render_menu(

        menu,

    )

    captured = capsys.readouterr()

    assert "100" in captured.out

# ============================================================
# Empty States
# ============================================================

def test_empty_header(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header("")

    captured = capsys.readouterr()

    assert captured.out is not None


def test_empty_footer(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_footer()

    captured = capsys.readouterr()

    assert captured.out is not None

# ============================================================
# Lifecycle
# ============================================================

def test_renderer_reusable(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Main"

    )

    renderer.render_menu(

        [

            "Deposit",

        ]

    )

    renderer.render_footer()

    renderer.render_header(

        "Reports"

    )

    renderer.render_menu(

        [

            "Summary",

        ]

    )

    renderer.render_footer()

    captured = capsys.readouterr()

    assert "Reports" in captured.out


def test_renderer_stateless(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "A",

        ]

    )

    renderer.render_menu(

        [

            "B",

        ]

    )

    captured = capsys.readouterr()

    assert "A" in captured.out

    assert "B" in captured.out

# ============================================================
# Integrity
# ============================================================

def test_complete_render_cycle(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_header(

        "Bank"

    )

    renderer.render_separator()

    renderer.render_menu(

        [

            "Customer",

            "Accounts",

            "Transactions",

            "Reports",

            "Exit",

        ]

    )

    renderer.render_footer()

    captured = capsys.readouterr()

    assert "Customer" in captured.out

    assert "Accounts" in captured.out

    assert "Transactions" in captured.out

    assert "Reports" in captured.out

    assert "Exit" in captured.out


def test_renderer_output_not_empty(

    capsys,

):

    renderer = MenuRenderer()

    renderer.render_menu(

        [

            "Exit",

        ]

    )

    captured = capsys.readouterr()

    assert len(

        captured.out.strip()

    ) > 0

