import tensorflow as tf

from pathlib import Path
from typing import Tuple, List

def load_datasets(
    data_dir: str | Path,
    img_size: Tuple[int, int] = (64, 64),
    batch_size: int = 32,
    val_split: float = 0.2,
    seed: int = 123
) -> Tuple[tf.data.Dataset, tf.data.Dataset, List[str]]:
    """
    Load image datasets for training & validation using a directory structure.

    Args:
        data_dir (str | Path): Root folder containing class subdirectories.
        img_size (tuple): Target size for images (width, height).
        batch_size (int): Number of images per batch.
        val_split (float): Fraction of data reserved for validation.
        seed (int): Random seed for reproducibility.

    Returns:
        (train_ds, val_ds, class_names)
        - train_ds (tf.data.Dataset): Training dataset
        - val_ds   (tf.data.Dataset): Validation dataset
        - class_names (list[str]): List of class names
    """

    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"❌ Dataset directory not found: {data_dir}")

    if not (0.0 < val_split < 1.0):
        raise ValueError("val_split must be between 0 and 1 (e.g., 0.2 for 20%).")

    # Training dataset
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="training",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size
    )

    # Validation dataset
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="validation",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size
    )

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds   = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, train_ds.class_names
