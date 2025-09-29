import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import itertools

from .config import MODEL_PATH, CLASS_MAP_JSON
from .data import get_datasets
from sklearn.metrics import classification_report, confusion_matrix

def plot_confusion_matrix(cm, class_names, normalize=True, title='Confusion matrix'):
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1, keepdims=True)
        cm = np.nan_to_num(cm)

    plt.figure(figsize=(10, 10))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=90)
    plt.yticks(tick_marks, class_names)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.show()

def main():
    train_ds, val_ds, test_ds, _ = get_datasets()
    with open(CLASS_MAP_JSON, 'r') as f:
        class_names = json.load(f)

    model = tf.keras.models.load_model(MODEL_PATH.as_posix())

    eval_ds = test_ds if test_ds is not None else val_ds
    y_true, y_pred = [], []

    for batch in eval_ds:
        images, labels = batch
        preds = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(labels.numpy())

    print(classification_report(y_true, y_pred, target_names=class_names, digits=4))
    cm = confusion_matrix(y_true, y_pred)
    plot_confusion_matrix(cm, class_names, normalize=True)
