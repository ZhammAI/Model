# model/src/trainer.py (continued)

                },
                {
                    'trend': y_trend_test,
                    'score': y_score_test
                }
            )

            # Make predictions for detailed metrics
            predictions = self.model.model.predict({
                'text_input': X_text_test,
                'metrics_input': X_metrics_test
            })

            # Calculate detailed metrics
            trend_accuracy = np.mean(np.equal(
                np.argmax(predictions[0], axis=1),
                np.argmax(y_trend_test, axis=1)
            ))

            score_mae = np.mean(np.abs(predictions[1] - y_score_test))

            return {
                'loss': float(results[0]),
                'trend_accuracy': float(trend_accuracy),
                'score_mae': float(score_mae),
                'trend_loss': float(results[1]),
                'score_loss': float(results[2])
            }

        except Exception as e:
            self.logger.error(f"Evaluation error: {str(e)}")
            raise

    def fine_tune(self, new_data: List[Dict], learning_rate: float = 1e-5) -> Dict:
        """Fine-tune the model on new data"""
        try:
            # Prepare new data
            X_text, X_metrics, y_trend, y_score = self._prepare_data(new_data)

            # Adjust model for fine-tuning
            self.model.model.optimizer.learning_rate = learning_rate

            # Fine-tune
            history = self.model.model.fit(
                {
                    'text_input': X_text,
                    'metrics_input': X_metrics
                },
                {
                    'trend': y_trend,
                    'score': y_score
                },
                epochs=5,
                batch_size=16,
                validation_split=0.1
            )

            return {
                'history': history.history,
                'final_loss': history.history['loss'][-1]
            }

        except Exception as e:
            self.logger.error(f"Fine-tuning error: {str(e)}")
            raise