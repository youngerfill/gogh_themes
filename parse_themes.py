#! /usr/bin/env python3

import argparse
import re
from html.parser import HTMLParser


def extract_color(s):
    s_list = s.split(":")
    if s_list and len(s_list) > 1:
        result = re.search(r"^.*rgb\(([0-9]+), ([0-9]+), ([0-9]+)\);$", s_list[1])
        if result:
            return "#%02x%02x%02x" % tuple(int(e) for e in result.group(1, 2, 3))

    return "#fa17ed"


def print_theme(theme):
    if theme is not None:
        print("####################")
        print(f"# {theme.name}")

        for index, color in enumerate(theme.colors):
            print(f'export LOCAL_DWM_COLOR_{index:02}="{color}"')

        print(f'export LOCAL_DWM_BG_COLOR="{theme.bg_color}"')
        print('export LOCAL_DWM_FG_COLOR="$LOCAL_DWM_COLOR_07"')
        print('export LOCAL_DWM_CURSOR_COLOR="$LOCAL_DWM_COLOR_15"')
        print('export LOCAL_DWM_REV_CURSOR_COLOR="$LOCAL_DWM_COLOR_08"')
        print()


class Theme:
    def __init__(self) -> None:
        self.name = ""
        self.bg_color = ""
        self.colors = []


class HtmlTag:
    def __init__(self, name, attrs) -> None:
        self.name = name
        self.attrs = attrs.copy() if attrs else None
        self.data = ""


class TerminalNode:
    def __init__(self) -> None:
        self.stack = []

    def push_tag(self, name, attrs) -> None:
        self.stack.append(HtmlTag(name, attrs))

    def pop_tag(self) -> HtmlTag:
        return self.stack.pop()


class MyHtmlParser(HTMLParser):
    def __init__(self):
        self.theme = None
        self.terminal_node = None
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs) -> None:
        if attrs and len(attrs) > 0 and attrs[0] == ("class", "terminal"):
            self.theme = Theme()
            self.terminal_node = TerminalNode()

        if self.terminal_node is not None:
            self.terminal_node.push_tag(tag, attrs)

            if attrs and len(attrs) > 0 and self.theme is not None:
                # Extract BG color
                if attrs[0] == ("class", "body"):
                    self.theme.bg_color = extract_color(attrs[1][1])

                # Extract terminal color
                if tag == "p" and attrs[0][0] == "style":
                    self.theme.colors.append(extract_color(attrs[0][1]))

    def handle_endtag(self, tag) -> None:
        if self.terminal_node is not None:
            self.terminal_node.pop_tag()

            if len(self.terminal_node.stack) == 0:
                print_theme(self.theme)
                self.terminal_node = None
                self.theme = None

    def handle_data(self, data) -> None:
        if self.theme is not None and self.terminal_node is not None:
            if self.terminal_node.stack[-1].attrs == [("class", "bar__title")]:
                self.theme.name = data


def arguments():
    parser = argparse.ArgumentParser(
        description="Parse themes from Gogh page and write them to a JSON file"
    )
    parser.add_argument("--file", required=False, default="index.html")

    return parser.parse_args()


def tests():

    test_strings = ["background-color: rgb(31, 29, 69);", "color: rgb(189, 0, 19);"]

    for test_string in test_strings:
        hex_color = extract_color(test_string)
        # assert hex_color is not None
        print(f"{test_string=}")
        print(f"{hex_color=}")
        print("")


def main():
    # tests()
    # return

    args = arguments()
    parser = MyHtmlParser()
    print(f"{args.file=}")
    with open(args.file, "r") as file:
        html_content = file.read()
        parser.feed(html_content)


if __name__ == "__main__":
    main()
