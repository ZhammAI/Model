# model/src/model.py

import tensorflow as tf
from transformers import DistilBertTokenizer, TFDistilBertModel
import numpy as np
from typing import Dict, List, Optional

class ZhamModel:
    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        self.bert = TFDistilBertModel.from_pretrained('distilbert-base-uncased')
        self.model = self._build_model()

    def _build_model(self):
        """Build the neural network architecture"""
        # Input layers
        text_input = tf.keras.layers.Input(shape=(128,), dtype=tf.int32, name='text_input')
        metrics_input = tf.keras.layers.Input(shape=(10,), name='metrics_input')

        # BERT text processing
        embedding = self.bert(text_input)[0]
        x = tf.keras.layers.GlobalAveragePooling1D()(embedding)
        x = tf.keras.layers.Dense(64, activation='relu')(x)

        # Process market metrics
        y = tf.keras.layers.Dense(32, activation='relu')(metrics_input)
        y = tf.keras.layers.Dropout(0.2)(y)

        # Combine text and metrics
        combined = tf.keras.layers.Concatenate()([x, y])
        combined = tf.keras.layers.Dense(64, activation='relu')(combined)
        combined = tf.keras.layers.Dropout(0.2)(combined)

        # Output layers
        trend_output = tf.keras.layers.Dense(3, activation='softmax', name='trend')(combined)
        score_output = tf.keras.layers.Dense(1, activation='sigmoid', name='score')(combined)

        model = tf.keras.Model(
            inputs=[text_input, metrics_input],
            outputs=[trend_output, score_output]
        )

        model.compile(
            optimizer='adam',
            loss={
                'trend': 'categorical_crossentropy',
                'score': 'mse'
            },
            metrics={
                'trend': 'accuracy',
                'score': 'mae'
            }
        )

        return model

    def predict(self, text: str, metrics: List[float]) -> Dict:
        """Make prediction for given text and metrics"""
        # Tokenize text
        tokens = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='tf'
        )

        # Prepare metrics
        metrics_array = np.array(metrics).reshape(1, -1)

        # Make prediction
        trends, score = self.model.predict([tokens['input_ids'], metrics_array])

        # Process results
        trend_labels = ['bearish', 'neutral', 'bullish']
        trend_idx = np.argmax(trends[0])

        return {
            'trend': trend_labels[trend_idx],
            'trend_confidence': float(trends[0][trend_idx]),
            'score': float(score[0][0]),
            'probabilities': {
                label: float(prob)
                for label, prob in zip(trend_labels, trends[0])
            }
        }

    def save_weights(self, path: str):
        """Save model weights"""
        self.model.save_weights(path)

    def load_weights(self, path: str):
        """Load model weights"""
        self.model.load_weights(path)