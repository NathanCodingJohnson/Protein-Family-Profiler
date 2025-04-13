import os
from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from urllib.parse import urlencode


app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class UploadFileForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Upload File')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            print(f"File received: {file.filename}")  # Debugging statement
            # Check if the file has a valid extension
            allowed_extensions = {'.txt', '.fasta'}
            _, file_extension = os.path.splitext(file.filename)
            if file_extension.lower() in allowed_extensions:
                if hasattr(file, 'save'):  # Ensure the file is valid and has a 'save' method
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    message = "File uploaded successfully!"
                    category = "success"
                else:
                    print("File does not have a 'save' method.")  # Debugging statement
                    message = "Invalid file. Could not save."
                    category = "error"
            else:
                print("Invalid file extension.")  # Debugging statement
                message = "Invalid file type. Only .txt and .fasta files are allowed."
                category = "error"
        else:
            print("No file received.")  # Debugging statement
            message = "No valid file uploaded!"
            category = "error"
        # Redirect with message and category as query parameters
        query_params = urlencode({'message': message, 'category': category})
        return redirect(f"{request.url}?{query_params}")
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)