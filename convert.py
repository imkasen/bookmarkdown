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


def convert2json(content: str) -> dict:
    soup = BeautifulSoup(content, "html.parser")

    # Firefox bookmarks will provide a <H3> tag with a 'PERSONAL_TOOLBAR_FOLDER' attribute
    toolbar_dl_tag = soup.find("h3", attrs={"personal_toolbar_folder": "true"}).find_next_sibling("dl")
    dl_tag = toolbar_dl_tag.find("dl")

    dir: dict = {}
    while dl_tag:
        tmp_dir: dict = parse_folders(dl_tag)
        dir.update(tmp_dir)  # TODO: conflits that different dirs with the same name
        dl_tag = dl_tag.find_next_sibling().find("dl")

    return dir


def parse_folders(tag) -> dict:
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
    sub_dl_tag = tag.find("dl")
    dir: dict = {}

    if h3_tag:
        dir_title: str = h3_tag.text
        if sub_dl_tag:
            subdir = parse_folders(sub_dl_tag)
            dir.update(subdir)
            for a_tag in sub_dl_tag.find_next_sibling().find_all("a"):
                dir[a_tag.text] = a_tag["href"]
            return {dir_title: dir}
        else:
            for a_tag in tag.find_all("a"):
                dir[a_tag.text] = a_tag["href"]
            return {dir_title: dir}

    return dir


if __name__ == "__main__":
    input_path, output_path = parse_input()
    check_file(input_path, output_path)
    type: str = os.path.splitext(output_path.lower())[-1][1:]

    if type == "json":
        with open(input_path, "r", encoding="utf-8") as input_file, \
             open(output_path, "w", encoding="utf-8") as output_file:
            content: str = input_file.read()
            dir: dict = convert2json(content)
            json.dump(dir, output_file, ensure_ascii=False)
    elif type == "csv":
        pass
    elif type == "md":
        pass
    else:
        sys.exit("Unknown output file type!")
