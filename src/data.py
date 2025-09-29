import tensorflow as tf

from .config import TRAIN_DIR, TEST_DIR, IMAGE_SIZE, BATCH_SIZE, VAL_SPLIT, SEED
from typing import Tuple, List, Optional

AUTOTUNE = tf.data.AUTOTUNE

# -------------------------
# Preprocessing Helpers
# -------------------------
def _standardize(x: tf.Tensor) -> tf.Tensor:
    """
    Normalize images to [-1, 1] range for MobileNetV2.
    """
    x = tf.cast(x, tf.float32) / 255.0
    return (x - 0.5) * 2.0


def _has_class_subdirs(path: str) -> bool:
    """
    Check if the given directory contains class subfolders.
    """
    if not tf.io.gfile.exists(path):
        return False
    try:
        subdirs = [
            d for d in tf.io.gfile.listdir(path)
            if tf.io.gfile.isdir(tf.io.gfile.join(path, d))
        ]
        return len(subdirs) > 0
    except Exception:
        return False

# -----------------
# Dataset Loader
# -----------------
def get_datasets() -> Tuple[
    tf.data.Dataset, 
    tf.data.Dataset, 
    Optional[tf.data.Dataset], 
    List[str]
]:
    """
    Load training, validation, and optional test datasets.

    Returns:
        train_ds (tf.data.Dataset): Preprocessed training dataset
        val_ds   (tf.data.Dataset): Preprocessed validation dataset
        test_ds  (tf.data.Dataset | None): Preprocessed test dataset if available
        class_names (list[str]): List of class labels
    """

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="int",
        validation_split=VAL_SPLIT,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="int",
        validation_split=VAL_SPLIT,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    class_names = train_ds.class_names

    test_ds = None
    if _has_class_subdirs(str(TEST_DIR)):
        test_ds = tf.keras.utils.image_dataset_from_directory(
            TEST_DIR,
            labels="inferred",
            label_mode="int",
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            shuffle=False,
        )

    # Preprocessing & caching
    def _prepare(ds: tf.data.Dataset, training: bool = False) -> tf.data.Dataset:
        ds = ds.map(lambda x, y: (_standardize(x), y), num_parallel_calls=AUTOTUNE)
        if training:
            ds = ds.shuffle(1000, seed=SEED)
        return ds.cache().prefetch(AUTOTUNE)

    train_ds = _prepare(train_ds, training=True)
    val_ds   = _prepare(val_ds, training=False)
    if test_ds is not None:
        test_ds = _prepare(test_ds, training=False)

    return train_ds, val_ds, test_ds, class_names
