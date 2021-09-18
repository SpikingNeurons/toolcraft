#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# https://github.com/pytorch/botorch/blob/master/scripts/parse_tutorials.py
from __future__ import annotations

import argparse
import json
import os

from pathlib import Path

import nbformat

from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from nbconvert import PythonExporter


TEMPLATE = """const CWD = process.cwd();
const React = require('react');
const Tutorial = require(`${{CWD}}/core/Tutorial.js`);
class TutorialPage extends React.Component {{
  render() {{
      const {{config: siteConfig}} = this.props;
      const {{baseUrl}} = siteConfig;
      return <Tutorial baseUrl={{baseUrl}} tutorialID="{}"/>;
  }}
}}
module.exports = TutorialPage;
"""

JS_SCRIPTS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
"""  # noqa: E501


def validate_tutorial_links(input_dir: str) -> None:
    """Checks that all .ipynb files that present are linked on the website, and vice
    versa, that any linked tutorial has an associated .ipynb file present.
    """
    with open(os.path.join(input_dir, "mapping.json")) as infile:
        tutorial_config = json.load(infile)

    tutorial_ids = {x["id"] for v in tutorial_config.values() for x in v}

    tutorials_nbs = {
        fn.name.replace(".ipynb", "")
        for fn in Path(input_dir).iterdir() if fn.suffix == ".ipynb"
    }

    missing_files = tutorial_ids - tutorials_nbs
    missing_ids = tutorials_nbs - tutorial_ids

    if missing_files:
        raise RuntimeError(
            "The following tutorials are linked on the website, but missing an "
            f"associated .ipynb file: {missing_files}.", )

    if missing_ids:
        raise RuntimeError(
            "The following tutorial files are present, but are not linked on the "
            "website: {}.".format(
                ", ".join([nbid + ".ipynb" for nbid in missing_ids]), ), )


def gen_tutorials(input_dir: str, output_dir: str) -> None:
    """Generate HTML tutorials for botorch Docusaurus site from Jupyter notebooks.
    Also create ipynb and py versions of tutorial in Docusaurus site for
    download.
    """
    with open(os.path.join(input_dir, "mapping.json")) as infile:
        tutorial_config = json.load(infile)

    # create output directories if necessary
    html_out_dir = Path(output_dir) / "_tutorials"
    files_out_dir = Path(output_dir) / "static" / "files"
    html_out_dir.mkdir(parents=True, exist_ok=True)
    files_out_dir.mkdir(parents=True, exist_ok=True)

    tutorial_ids = {x["id"] for v in tutorial_config.values() for x in v}

    for tid in tutorial_ids:
        print(f"Generating {tid} tutorial")

        # convert notebook to HTML
        ipynb_in_path = os.path.join(input_dir, f"{tid}.ipynb")
        with open(ipynb_in_path, encoding="utf8") as infile:
            nb_str = infile.read()
            nb = nbformat.reads(nb_str, nbformat.NO_CONVERT)

        # displayname is absent from notebook metadata
        nb["metadata"]["kernelspec"]["display_name"] = "python3"

        exporter = HTMLExporter()
        html, meta = exporter.from_notebook_node(nb)

        # pull out html div for notebook
        soup = BeautifulSoup(html, "html.parser")
        nb_meat = soup.find("div", {"id": "notebook-container"})
        del nb_meat.attrs["id"]
        nb_meat.attrs["class"] = ["notebook"]
        html_out = JS_SCRIPTS + str(nb_meat)

        # generate html file
        html_out_path = os.path.join(
            html_out_dir,
            f"{tid}.html",
        )
        with open(html_out_path, "w", encoding="utf8") as html_outfile:
            html_outfile.write(html_out)

        # generate JS file
        script = TEMPLATE.format(tid)
        js_out_path = os.path.join(output_dir, "pages", "tutorials",
                                   f"{tid}.js")
        Path(js_out_path).parent.mkdir(exist_ok=True, parents=True)
        with open(js_out_path, "w", encoding="utf8") as js_outfile:
            js_outfile.write(script)

        # output tutorial in both ipynb & py form
        ipynb_out_path = os.path.join(files_out_dir, f"{tid}.ipynb")
        with open(ipynb_out_path, "w", encoding="utf8") as ipynb_outfile:
            ipynb_outfile.write(nb_str)
        exporter = PythonExporter()
        script, meta = exporter.from_notebook_node(nb)
        # make sure to use python3 shebang
        script = script.replace(
            "#!/usr/bin/env python",
            "#!/usr/bin/env python3",
        )
        py_out_path = os.path.join(output_dir, "static", "files", f"{tid}.py")
        with open(py_out_path, "w", encoding="utf8") as py_outfile:
            py_outfile.write(script)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate JS, HTML, ipynb, and py files for tutorials.", )

    parser.add_argument(
        "-i",
        "--input_dir",
        metavar="path",
        required=True,
        help="Input directory for notebooks.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        metavar="path",
        required=True,
        help="Output directory in Docusaurus.",
    )
    args = parser.parse_args()
    validate_tutorial_links(args.input_dir)
    gen_tutorials(args.input_dir, args.output_dir)
