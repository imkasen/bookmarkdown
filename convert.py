#!/usr/bin/env python3

import argparse
import json
import os
import sys

from bs4 import BeautifulSoup


def parse_input() -> tuple[str, str, str]:
    description: str = "A simple script which can convert brower bookmarks(a HTML file) into a Markdown file (also support CSV and JSON)."
    example: str = '''Example:\npython3 convert -i bookmarks.html -o bookmarks.md'''

    parser = argparse.ArgumentParser(description, epilog=example, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input", required=True, help="the path of HTML file")
    parser.add_argument("-o", "--output", required=True, help="the path of output file")
    args = parser.parse_args()

    return args.input, args.output


def check_file(input_path: str, output_path: str) -> None:
    _, extension = os.path.splitext(input_path)
    if not os.path.exists(input_path):
        sys.exit(f"Sorry, '{input_path}' is invalid.")
    if os.path.isfile(input_path) and not extension.lower() == ".html":
        sys.exit(f"Sorry, '{input_path}' is not a HTML file.")
    if os.path.exists(output_path) or os.path.isfile(output_path):
        sys.exit(f"Sorry, '{output_path}' already exists.")


def convert2json(content: str) -> dict | None:
    soup = BeautifulSoup(content, "html.parser")

    # Firefox bookmarks will provide a <H3> tag with a 'PERSONAL_TOOLBAR_FOLDER' attribute
    toolbar_dl_tag = soup.find("h3", attrs={"personal_toolbar_folder": "true"}).find_next_sibling("dl")
    dl_tag = toolbar_dl_tag.find("dl")

    if dl_tag:
        return parse_folders(dl_tag)

    return None


def parse_folders(tag) -> dict | None:
    """
    parse the basic folder structure, a '<h3>' folder title and multiple '<a>' bookmarks.

    ```
    <DT><H3 ...>folder title</H3>
    <DL><p>
        <DT><A href="link1" ...>bookmark1</A>
        <DT><A href="link2" ...>bookmark2</A>
    </DL><p>
    ```

    :param tag: A '<DL>' tag which contains links, use 'find_previous_sibling("h3")' to get the folder title.
    :return: dict or None
    """
    h3_tag = tag.find_previous_sibling("h3")

    if h3_tag:
        dir_title: str = h3_tag.text
        dir: dict = {}
        for a_tag in tag.find_all("a"):
            dir[a_tag.text] = a_tag["href"]
        return {dir_title: dir}

    return None


if __name__ == "__main__":
    input_path, output_path = parse_input()
    check_file(input_path, output_path)
    type: str = os.path.splitext(output_path.lower())[-1][1:]
    dir: dict | None = None

    if type == "json":
        with open(input_path, "r", encoding="utf-8") as input_file:
            content: str = input_file.read()
            dir = convert2json(content)
        if dir:
            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(dir, output_file, ensure_ascii=False)
    elif type == "csv":
        pass
    else:  # md
        pass