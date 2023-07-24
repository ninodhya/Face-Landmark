from deepface import DeepFace

def detect_gender(image_path):
    result = DeepFace.analyze(img_path = image_path, actions = ['gender'])
    gender = result[0]["gender"]  # Perhatikan perubahan pada baris ini
    print(f'Gender: {gender}')

# Ganti 'path/to/image.jpg' dengan path ke gambar Anda
detect_gender('dataset2/22053/22053_5.png')
