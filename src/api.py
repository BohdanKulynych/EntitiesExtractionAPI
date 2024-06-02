from flask import Flask, request, jsonify
from pdf_processing import extract_text_from_pdf, clean_text, is_real_pdf
from entity_extraction import extract_clinical_entities
from exceptions import CorruptedPDFFile
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the maximum allowed payload to 5 megabytes (16 * 1024 * 1024 bytes)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. The maximum file size is 5MB."}), 413


@app.route('/api/v1/extract', methods=['POST'])
def extract_entities_from_pdf():
    """
    Extract entities from an uploaded PDF file.

    Returns:
    JSON: Extracted clinical and drug entities.
    """
    app.logger.info("API endpoint '/api/v1/extract' called.")

    if 'file' not in request.files:
        app.logger.error("No file part in request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        app.logger.error("No file selected for upload.")
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # Secure the filename and save the file to the /tmp directory
        filename = secure_filename(file.filename)
        file_path = os.path.join("/tmp", filename)
        file.save(file_path)
        app.logger.info(f"File '{filename}' has been uploaded and saved as '{file_path}'.")

        try:
            is_real_pdf(file_path)
        except CorruptedPDFFile as e:
            app.logger.exception(f"An error occurred while processing '{filename}'.")
            return jsonify({"error": str(e)}), 500

        try:
            # Check if the file is real pdf, not renamed file
            app.logger.info(f"Checking if the real filetype is pdf...'")
            # Extract and clean text from the PDF
            text = extract_text_from_pdf(file_path).strip()
            extracted_text_len = len(text)

            # Check if the pdf file is not empty
            if extracted_text_len == 0:
                app.logger.error("No text has been detected")
                return jsonify({"error": "No text has been detected"}), 500

            cleaned_text = clean_text(text)
            app.logger.info(f"Text extracted from '{filename}' and cleaned successfully. Start entities extraction...")

            # Extract entities
            entities = {
                "clinical_entities": extract_clinical_entities(cleaned_text),
                "drug_entities": extract_clinical_entities(cleaned_text, model='en_core_med7_lg')
            }

            app.logger.info("Entities extracted successfully.")
        except Exception as e:
            app.logger.exception(f"An error occurred while processing '{filename}'.")
            return jsonify({"error": str(e)}), 500
        finally:
            # Ensure the temporary file is removed after processing
            os.remove(file_path)
            app.logger.info(f"Temporary file '{file_path}' removed.")

        return jsonify(entities), 200
    else:
        app.logger.error(f"Unsupported file type: '{file.filename}'")
        return jsonify({"error": "Unsupported file type"}), 415


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4040)
