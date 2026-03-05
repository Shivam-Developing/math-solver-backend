#!/usr/bin/env bash
set -e

echo "Python version: $(python --version)"

pip install -r requirements.txt

python -c "
import os, requests, pix2tex

save_dir = os.path.join(os.path.dirname(pix2tex.__file__), 'model', 'checkpoints')
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, 'weights.pth')

if not os.path.exists(save_path):
    print('Downloading pix2tex weights...')
    url = 'https://github.com/lukas-blecher/LaTeX-OCR/releases/download/v0.0.1/weights.pth'
    r = requests.get(url, stream=True, timeout=300)
    with open(save_path, 'wb') as f:
        for chunk in r.iter_content(65536):
            if chunk: f.write(chunk)
    print('Weights downloaded!')
else:
    print('Weights already exist.')
"
