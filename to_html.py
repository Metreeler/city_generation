import os

def to_html(folder, output_file):
    out = \
"""<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div style="display: flex; flex-wrap: wrap;">"""
    file_names = os.listdir(folder)
    file_names = sorted(file_names)
    for filename in file_names:
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                out += """
            <div style="width: 400px;">
                <p>{}</p>
                <div style="object-fit: contain; ">
                    <img src="./assets/{}" style="width: 100%; height: 100%;"/>
                </div>
            </div>""".format(filename, filename)
        except Exception as e:
            print('Failed to add %s to html. Reason: %s' % (file_path, e))
    out += """
        </div>
    </body>
</html>"""
    with open(output_file, "w") as f:
        f.write(out)


if __name__=="__main__":
    folder = 'data/web-display/assets'
    to_html(folder, 'data/web-display/index.html')