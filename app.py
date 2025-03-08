import os
import subprocess
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, abort
from config import PDF_ROOT, UPDATE_TOKEN

app = Flask(__name__)

def get_directory_contents(rel_path=""):
    """Return sorted lists of subdirectories and PDF files in a given relative path."""
    abs_path = os.path.join(PDF_ROOT, rel_path)
    if not os.path.isdir(abs_path):
        abort(404)
    items = os.listdir(abs_path)
    subdirs = sorted([item for item in items if os.path.isdir(os.path.join(abs_path, item))])
    pdfs = sorted([item for item in items if item.lower().endswith('.pdf') and os.path.isfile(os.path.join(abs_path, item))])
    return subdirs, pdfs

@app.route("/")
def index():
    subdirs, pdfs = get_directory_contents("")
    return render_template("index.html", current_path="", subdirs=subdirs, pdfs=pdfs)

@app.route("/browse/<path:subpath>")
def browse(subpath):
    subdirs, pdfs = get_directory_contents(subpath)
    # Build breadcrumb links
    parts = subpath.split(os.sep)
    breadcrumbs = []
    for i in range(len(parts)):
        breadcrumb_path = os.sep.join(parts[:i+1])
        breadcrumbs.append((parts[i], breadcrumb_path))
    return render_template("directory.html",
                           current_path=subpath,
                           subdirs=subdirs,
                           pdfs=pdfs,
                           breadcrumbs=breadcrumbs)

@app.route("/pdf/<path:filepath>")
def serve_pdf(filepath):
    # Ensure the file ends with .pdf
    if not filepath.lower().endswith(".pdf"):
        abort(404)
    directory = os.path.join(PDF_ROOT, os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    if not os.path.isfile(os.path.join(directory, filename)):
        abort(404)
    return send_from_directory(directory, filename)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        # Walk through PDF_ROOT and search filenames (case-insensitive)
        for root, dirs, files in os.walk(PDF_ROOT):
            for file in files:
                if file.lower().endswith(".pdf") and query.lower() in file.lower():
                    # Create a relative path for the file to be used in links.
                    rel_dir = os.path.relpath(root, PDF_ROOT)
                    rel_path = os.path.join(rel_dir, file) if rel_dir != '.' else file
                    results.append(rel_path)
        results = sorted(results)
    return render_template("search.html", query=query, results=results)

@app.route("/update")
def update():
    # Protect update with a token (passed as ?token=...)
    token = request.args.get("token", "")
    if token != UPDATE_TOKEN:
        abort(403)
    # Change directory to the PDF_ROOT and run "git pull"
    try:
        result = subprocess.check_output(["git", "pull"], cwd=PDF_ROOT, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        result = f"Error: {e.output}"
    return f"<pre>{result}</pre>"

if __name__ == "__main__":
    # Run the built-in server (for testing on Windows)
    app.run(host="0.0.0.0", port=5000, debug=True)
