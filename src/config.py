from pathlib import Path

# ----------
# PATHS
# ----------
DATA_ROOT      = Path("data")   # Root folder
TRAIN_DIR      = DATA_ROOT / "asl_alphabet_train"
TEST_DIR       = DATA_ROOT / "asl_alphabet_test"

OUTPUT_DIR     = Path("saved_models")
CLASS_MAP_JSON = OUTPUT_DIR / "class_names.json"
MODEL_PATH     = OUTPUT_DIR / "asl_mobilenetv2.h5"

# ------------------------
# TRAINING HYPERPARAMETERS
# ------------------------
IMAGE_SIZE     = (160, 160)     # Input resolution for MobileNetV2
BATCH_SIZE     = 32
EPOCHS         = 15
LEARNING_RATE  = 1e-3
VAL_SPLIT      = 0.1            # Fraction of train data for validation
SEED           = 42             # For reproducibility

# -----------------
# DATA AUGMENTATION
# ----------------
ROTATION       = 0.08           # Random rotation range (~8%)
WIDTH_SHIFT    = 0.08
HEIGHT_SHIFT   = 0.08
ZOOM_RANGE     = 0.10
H_FLIP         = True           # Random horizontal flip

# --------------
# MISC SETTINGS
# --------------
MIXED_PRECISION = False         # Set True if GPU supports Automatic Mixed Precision (AMP)
