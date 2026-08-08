"""Tests for the current CLI MenuRenderer contract."""

from io import StringIO

import pytest

from cli.menu import MenuDefinition, MenuOption
from cli.menu_renderer import MenuRenderer


@pytest.fixture
def output():
    return StringIO()


@pytest.fixture
def renderer(output):
    return MenuRenderer(output=output, line_width=10)


class TestMenuRenderer:
    def test_constructor_retains_output_and_line_width(self, renderer, output):
        assert renderer.output is output
        assert renderer.line_width == 10

    def test_default_line_width_is_70(self):
        renderer = MenuRenderer(output=StringIO())
        assert renderer.line_width == 70

    def test_write_outputs_a_line(self, renderer, output):
        renderer._write("hello")
        assert output.getvalue() == "hello\n"

    def test_write_defaults_to_blank_line(self, renderer, output):
        renderer._write()
        assert output.getvalue() == "\n"

    def test_render_heading(self, renderer, output):
        renderer.render_heading("Title")
        assert output.getvalue() == (
            "\n"
            "==========\n"
            "  Title   \n"
            "==========\n"
        )

    def test_render_separator(self, renderer, output):
        renderer.render_separator()
        assert output.getvalue() == "----------\n"

    def test_render_menu_renders_heading_options_and_separator(self, renderer, output):
        menu = MenuDefinition(
            "Main",
            (
                MenuOption("1", "First"),
                MenuOption("2", "Second"),
                MenuOption("0", "Exit"),
            ),
        )
        renderer.render_menu(menu)
        assert output.getvalue() == (
            "\n"
            "==========\n"
            "   Main   \n"
            "==========\n"
            " 1. First\n"
            " 2. Second\n"
            " 0. Exit\n"
            "----------\n"
        )

    def test_render_menu_preserves_option_order(self, renderer, output):
        menu = MenuDefinition(
            "Menu",
            (
                MenuOption("3", "Third"),
                MenuOption("1", "First"),
                MenuOption("2", "Second"),
            ),
        )
        renderer.render_menu(menu)
        lines = output.getvalue().splitlines()
        assert lines[4:7] == [" 3. Third", " 1. First", " 2. Second"]

    @pytest.mark.parametrize(
        ("method", "prefix"),
        [
            ("info", "[INFO] "),
            ("success", "[SUCCESS] "),
            ("warning", "[WARNING] "),
            ("error", "[ERROR] "),
        ],
    )
    def test_message_renderers(self, method, prefix, renderer, output):
        getattr(renderer, method)("Operation complete")
        assert output.getvalue() == f"{prefix}Operation complete\n"

    @pytest.mark.parametrize("method", ["info", "success", "warning", "error"])
    def test_message_renderers_accept_empty_message(self, method, renderer, output):
        getattr(renderer, method)("")
        assert output.getvalue().endswith("\n")

    def test_render_table_renders_rows_and_separator(self, renderer, output):
        renderer.render_table(
            [
                ("Name", "Balance"),
                ("Adel", "100.50"),
            ]
        )
        assert output.getvalue() == (
            "Name | Balance\n"
            "Adel | 100.50\n"
            "----------\n"
        )

    def test_render_table_converts_objects_to_strings(self, renderer, output):
        renderer.render_table([(1, DecimalLike("10.50"), None)])
        assert output.getvalue() == "1 | 10.50 | None\n----------\n"

    def test_render_table_accepts_generator(self, renderer, output):
        rows = ((value,) for value in ["A", "B"])
        renderer.render_table(rows)
        assert output.getvalue() == "A\nB\n----------\n"

    def test_render_table_empty_rows_still_renders_separator(self, renderer, output):
        renderer.render_table([])
        assert output.getvalue() == "----------\n"

    def test_output_property_returns_configured_stream(self, renderer, output):
        assert renderer.output is output

    def test_line_width_property_returns_configured_width(self, renderer):
        assert renderer.line_width == 10

    def test_repr(self, renderer):
        assert repr(renderer) == "MenuRenderer(line_width=10)"

    def test_str(self, renderer):
        assert str(renderer) == "CLI Menu Renderer"

    def test_render_heading_uses_exact_line_width(self, renderer, output):
        renderer.render_heading("X")
        lines = output.getvalue().splitlines()
        assert len(lines[1]) == 10
        assert len(lines[2]) == 10
        assert len(lines[3]) == 10

    def test_render_separator_uses_exact_line_width(self, renderer, output):
        renderer.render_separator()
        assert len(output.getvalue().rstrip("\n")) == 10

    def test_render_menu_uses_exact_line_width_for_heading_and_separator(self, renderer, output):
        renderer.render_menu(MenuDefinition("X", ()))
        lines = output.getvalue().splitlines()
        assert len(lines[1]) == 10
        assert len(lines[2]) == 10
        assert len(lines[3]) == 10
        assert len(lines[4]) == 10

    def test_renderer_can_use_standard_output_stream(self):
        renderer = MenuRenderer()
        assert renderer.output is not None

    def test_renderer_can_use_custom_line_width(self):
        renderer = MenuRenderer(output=StringIO(), line_width=3)
        renderer.render_separator()
        assert renderer.output.getvalue() == "---\n"

    def test_message_renderer_preserves_internal_spacing(self, renderer, output):
        renderer.info("  spaced message  ")
        assert output.getvalue() == "[INFO]   spaced message  \n"

    def test_render_table_preserves_row_values(self, renderer, output):
        renderer.render_table([("A", "B", "C")])
        assert output.getvalue() == "A | B | C\n----------\n"

    def test_render_table_handles_single_column_rows(self, renderer, output):
        renderer.render_table([("A",), ("B",)])
        assert output.getvalue() == "A\nB\n----------\n"

    def test_render_table_handles_empty_row(self, renderer, output):
        renderer.render_table([()])
        assert output.getvalue() == "\n----------\n"

    def test_render_heading_handles_empty_title(self, renderer, output):
        renderer.render_heading("")
        lines = output.getvalue().splitlines()
        assert lines[2] == "          "


class DecimalLike:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
