# American Sign Language Detection

All the required files can be downloaded from here:
https://drive.google.com/drive/folders/1B-XwEg2IGBgBm4C4Uce3EwTnPae_P7zs?usp=drive_link

End-to-end project to train and deploy an "American Sign Language (ASL) image classifier" and interactive word maker tool.

## Dataset Layout

Please Download the Dataset first to use all the features properly:
https://www.kaggle.com/datasets/grassknoted/asl-alphabet

```markdown
data/
asl_alphabet_train/
A/
A1.jpg
B/
B1.jpg
...
Nothing1.jpg
Space1.jpg
Del1.jpg
asl_alphabet_test/
A_test.jpg
...
```


and put them like this:
> data/
>  asl_alphabet_train/
>    A/
>        A1.jpg
>    B/ 
>        B1.jpg
    ...
>        Nothing1.jpg
>        Space1.jpg
>        Del1.jpg
>  asl_alphabet_test/
>    A_test.jpg
    ...

> Also Run the `install_modules.bat` file 
then follow the steps below

> If your folders differ, edit paths in `src/config.py`.

## Quickstart

1) Run the app
Open the file: run.bat

OR

1) Create a venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

2) Put your dataset under ./data (If you want to change it)

3) Train
python -m src.train

4) Evaluate
python -m src.evaluate

If you want to run the program using the Local Network:
- Setup a secure connections like ngrok to access the features.

The best model and class mapping will be saved into `saved_models/`:
- 'asl_mobilenetv2.h5'
- 'class_names.json'

## Model

- Backbone: MobileNetV2 (ImageNet weights) with fine-tuning
- Input: 160×160 RGB, normalized to [-1, 1]
- Classes: 29 (A–Z, SPACE, DELETE, NOTHING)

## Config

Tune hyperparameters/paths in `src/config.py`.

## Notes & Tips

- If classes like 'M/N/S' confuse the model, add augmentation or train longer.
- Consider class-balanced sampling if you notice imbalance.
- To enable mixed precision (faster on modern GPUs), set `MIXED_PRECISION=True` in config.
- For larger images, bump `IMAGE_SIZE` (e.g., 224) but expect longer training.

## Streamlit App

- Upload a single image and get the predicted label with confidence.
- After training, the app automatically loads `saved_models/asl_mobilenetv2.h5` & `class_names.json`.

## Extended Features

- Home → Introduction and overview of how ASL works
- Upload Prediction → Upload an image and predict ASL letter (saved to history)
- Live Camera Prediction → Real-time webcam gesture recognition
- Word Maker → Capture letters in sequence to form words with dictionary meanings
- Sample Gestures → Reference images to learn ASL letters
- Quiz Game → Interactive 10-question ASL quiz
