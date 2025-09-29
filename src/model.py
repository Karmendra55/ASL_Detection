import tensorflow as tf

from .config import IMAGE_SIZE, LEARNING_RATE

def build_model(num_classes: int) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    base.trainable = False 

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = inputs
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    model = tf.keras.Model(inputs, outputs)

    opt = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(optimizer=opt,
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def fine_tune(model: tf.keras.Model, base_trainable_from: int = 100):
    # Unfreeze the base model from a certain layer for fine-tuning
    base_model = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model):
            base_model = layer
            break
    if base_model is None:
        return model

    base_model.trainable = True
    for i, layer in enumerate(base_model.layers):
        layer.trainable = i >= base_trainable_from

    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-4),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model
