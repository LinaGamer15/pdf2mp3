from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from flask import Flask, render_template, url_for, redirect, send_file, abort
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, SelectField
from werkzeug.utils import secure_filename
import os
from gtts import gTTS
from dict_languages import gTTS_languages_dict, languages
from pydub import AudioSegment

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


class FileUpload(FlaskForm):
    language = SelectField('Language', choices=languages)
    pdf_file = FileField('PDF File',
                         validators=[FileAllowed(['pdf', 'PDF'], 'PDFs only!'), FileRequired('File is empty!')])
    submit = SubmitField('Convert')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = FileUpload()
    if form.validate_on_submit():
        filename = secure_filename(form.pdf_file.data.filename)
        form.pdf_file.data.save('pdf/' + filename)
        if os.path.isfile(f'pdf/{filename}'):
            text_string = StringIO()
            with open(f'pdf/{filename}', 'rb') as file:
                parser = PDFParser(file)
                doc = PDFDocument(parser)
                rsrcmgr = PDFResourceManager()
                device = TextConverter(rsrcmgr, text_string, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.create_pages(doc):
                    interpreter.process_page(page)
            output_string = text_string.getvalue()
            # gTTS
            language_code = form.language.data.split(" - ")[1]
            if language_code in gTTS_languages_dict:
                voice = gTTS(text=output_string, lang=language_code, slow=False)
                voice.save(f'./audiobook/{filename.split(".")[0]}.mp3')
            else:
                os.system(f'espeak -v {language_code}/audiobook/{filename.split(".")[0]}.wav {output_string}')
                AudioSegment.from_wav(f'./audiobook/{filename.split(".")[0]}.wav').export(
                    f'./audiobook/{filename.split(".")[0]}.mp3', format='mp3')
                os.remove(f'./audiobook/{filename.split(".")[0]}.wav')
            return redirect(url_for('get_mp3', filename=filename))

    return render_template('index.html', form=form)


@app.route('/get-mp3/<path:filename>', methods=['GET', 'POST'])
def get_mp3(filename):
    try:
        return send_file(f'audiobook\\{filename.split(".")[0]}.mp3', mimetype='mp3',
                         attachment_filename=f'{filename.split(".")[0]}.mp3', as_attachment=True)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
