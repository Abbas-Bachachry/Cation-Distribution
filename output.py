import os
import time
import pdfkit
from jinja2 import Template
from docx import Document
from docx.shared import Pt

OUTPUT = 'OutPut/'


def create_output_dir():
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)


def create_folder():
    folder = time.strftime("%Y_%m_%d/")
    full_folder = OUTPUT + folder
    if not os.path.exists(full_folder):
        os.mkdir(full_folder)

    return full_folder


def create_name(type_):
    name = time.strftime("%H_%M_%S")
    return f'{name}.{type_}'


def save_as_html(cd_list, filename):
    # Create the HTML content with embedded styles
    with open('static/css/styles.css', 'r') as style_file:
        style = style_file.read()
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Cation Distribution</title>
    <style>
    {style}
    </style>
</head>
<body>
<div class="container">
    <div class="column">
        <table class="caption-table bordered-table">
            <caption class="left_aligned_text">Cation distribution</caption>
            <tr>
                <th>Label</th>
                <th>A site</th>
                <th>B site</th>
            </tr>
    """

    # Add rows for each item in cd_list
    for data in cd_list:
        site_a = []
        site_b = []

        for j, a in enumerate(data['site_a']):
            if a:
                site_a.append(f"{data['e_name'][j // 4]}<sup>{'3+' if j % 2 else '2+'}</sup><sub>{a}</sub>")
        for j, b in enumerate(data['site_b']):
            if b:
                site_b.append(f"{data['e_name'][j // 2]}<sup>{'3+' if j % 2 else '2+'}</sup><sub>{b}</sub>")

        html_content += f"""
        <tr>
            <td>{data['label']}</td>
            <td>[{', '.join(site_a)}]</td>
            <td>({', '.join(site_b)})</td>
        </tr>
        """

    html_content += """
        </table>
    </div>
</div>
</body>
</html>
    """

    # Save the HTML content to the file
    with open(filename, 'w') as f:
        f.write(html_content)
    print(filename, 'is saved!')


def save_as_pdf(cd_list, filename):
    try:
        # Create a simple HTML template for the PDF
        with open('templates/PDF.html', 'r') as pdf_file:
            pdf = pdf_file.read()
        template = Template(pdf)

        # Render the template with the data
        rendered_html = template.render(cd_list=cd_list, title="Cation Distribution Results")

        # Save the rendered HTML as a PDF
        pdfkit.from_string(rendered_html, filename)
        print(f"Saved PDF as {filename}")
    except OSError as e:
        if "No wkhtmltopdf executable found" in str(e):
            # Display a user-friendly error message
            error_message = """
            Error saving the table as PDF: No wkhtmltopdf executable found.

            To resolve this issue, please install wkhtmltopdf:
            1. Go to https://wkhtmltopdf.org/downloads.html
            2. Download and install the appropriate version for your operating system.
            3. Ensure that wkhtmltopdf is added to your system's PATH.

            After installing, you should be able to save the table as a PDF.
            """
            print(error_message)
            # Optionally, you can also display this message on the web page if needed
        raise e


def save_as_word(cd_list, filename):
    # Create a new Document
    doc = Document()

    # Add a title to the document
    doc.add_heading('Cation Distribution Results', 0)

    # Iterate over the cd_list and add the data to the Word document
    for cd in cd_list:
        doc.add_heading(cd.get('label', 'No Label'), level=1)

        # Add table
        table = doc.add_table(rows=1, cols=len(cd))
        table.style = 'Table Grid'

        # Add the headers (keys of the dictionary)
        hdr_cells = table.rows[0].cells
        for idx, key in enumerate(cd.keys()):
            hdr_cells[idx].text = key.capitalize()

        # Add the row data
        row_cells = table.add_row().cells
        for idx, value in enumerate(cd.values()):
            row_cells[idx].text = str(value)

    # Save the document
    try:
        doc.save(filename)
        print(f"Word document saved as {filename}")
    except Exception as e:
        print(f"Error saving Word document: {str(e)}")


def save_as_excel(cd_list, filename):
    # Implement Excel saving logic here
    pass


def save(cd_list, type_='html', name=None):
    create_output_dir()
    filename = create_folder()
    if name is None:
        name = create_name(type_)
        print(name)
    if type_.lower() == 'html':
        save_as_html(cd_list, filename + name)
    elif type_.lower() == 'pdf':
        save_as_pdf(cd_list, filename + name)
    elif type_.lower() == 'docx':
        save_as_word(cd_list, filename + name)
    elif type_.lower() == 'xlsx':
        save_as_excel(cd_list, filename + name)
    else:
        raise ValueError(f'unknown type {type_}')
