import json
import tensorflow as tf

from .config import OUTPUT_DIR, CLASS_MAP_JSON, MODEL_PATH, EPOCHS, MIXED_PRECISION
from .data import get_datasets
from .model import build_model, fine_tune

if MIXED_PRECISION:
    from keras import mixed_precision
    mixed_precision.set_global_policy('mixed_float16')

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds, test_ds, class_names = get_datasets()
    num_classes = len(class_names)

    with open(CLASS_MAP_JSON, 'w') as f:
        json.dump(class_names, f, indent=2)

    model = build_model(num_classes)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True, monitor='val_accuracy'),
        tf.keras.callbacks.ModelCheckpoint(MODEL_PATH.as_posix(), monitor='val_accuracy', save_best_only=True)
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

    model = fine_tune(model, base_trainable_from=100)
    history_ft = model.fit(train_ds, validation_data=val_ds, epochs=max(3, EPOCHS//3), callbacks=callbacks)

    # Final evaluation
    try:
        test_loss, test_acc = model.evaluate(test_ds)
        print(f"Test accuracy: {test_acc:.4f}")
    except Exception as e:
        print("No test dataset found, skipping evaluation.")

    # Saving final model
    model.save(MODEL_PATH.as_posix())

if __name__ == "__main__":
    main()
