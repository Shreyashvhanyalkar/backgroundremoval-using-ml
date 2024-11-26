from flask import Flask, request, render_template, send_file
from rembg import remove
from PIL import Image
import os

app = Flask(__name__)

# Create directories for original and masked images if they don't exist
os.makedirs('original', exist_ok=True)
os.makedirs('masked', exist_ok=True)

@app.route('/')
def index():
    return render_template('new.html')

@app.route('/process-images', methods=['POST'])
def process_images():
    # Check if files are uploaded
    if 'foreground' not in request.files or 'background' not in request.files:
        return "No file part", 400
    
    foreground_file = request.files['foreground']
    background_file = request.files['background']

    if foreground_file.filename == '' or background_file.filename == '':
        return "No selected file", 400

    # Save the original foreground image
    foreground_path = os.path.join('original', foreground_file.filename)
    foreground_file.save(foreground_path)

    # Remove background from the foreground image
    with open(foreground_path, 'rb') as f:
        input_img = f.read()
        subject = remove(input_img, alpha_matting=True)

    # Save the masked image
    output_path = os.path.join('masked', foreground_file.filename)
    with open(output_path, 'wb') as f:
        f.write(subject)

    # Open the background image directly from the uploaded file stream
    background_img = Image.open(background_file.stream)
    
    # Open the masked foreground image
    foreground_img = Image.open(output_path)
    
    # Resize background to match dimensions of foreground
    background_img = background_img.resize(foreground_img.size)

    # Paste the foreground onto the background
    background_img.paste(foreground_img, (0, 0), foreground_img)

    # Save final output image
    final_output_path = os.path.join('masked', 'final_image.jpg')
    background_img.save(final_output_path, format='JPEG')

    return send_file(final_output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)