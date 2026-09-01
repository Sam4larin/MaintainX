# Engineering Decision Log

A chronological record of real bugs found, how they were diagnosed, and what fixed them. Entries are numbered in the order they were resolved, not dated — this project's development spanned multiple work sessions and exact dates aren't tracked per-fix.

---

### 1. CMAPSS test RUL target was flat per-engine instead of decreasing per-cycle

**Symptom:** XGBoost RUL regression scored strongly negative R² (-0.75 to -0.90) on the official FD001 test set, despite the same model scoring R²=0.93 on a held-out slice of training engines.

**Diagnosis:** `build_cmapss_features()` assigned a single flat RUL value (the engine's final-cycle RUL from `RUL_FD001.txt`) to every row of that test engine, rather than a per-row value that decreases as the engine progresses through its recorded cycles. Train targets correctly decreased per cycle; test targets did not — a real train/test target mismatch, not a dataset limitation. Verified against a published baseline for this exact dataset tier (RMSE ~20–22, R² ~0.71–0.75) before concluding the low score wasn't inherent to the data.

**Fix:** compute test RUL per-row as `final_cycle_rul + (max_cycle_for_engine - current_cycle)`, clipped at 125 to match train.

**Result:** RMSE went from 57.26 (R² -0.91) to 12.25 (R² 0.80) on the same test set with the same model and features — beating the published baseline.

---

### 2. `build_ai4i_features()` signature mismatch after a function-signature change

**Symptom:** `TypeError: build_ai4i_features() missing 1 required positional argument: 'raw_df'`.

**Diagnosis:** the function had been updated to accept both the cleaned dataframe and the raw (pre-cleaning) dataframe — needed to derive a human-readable `failure_type` label from flag columns (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) that get dropped during cleaning — but the pipeline's call site was never updated to pass both arguments, and was also discarding the `failure_type` return value entirely.

**Fix:** pass both dataframes at the call site; capture and merge `failure_type` back into the features dataframe, since downstream classification and anomaly-detection code expects it as a real column.

---

### 3. Regression `predict()` call included columns the model was never trained on

**Symptom:** `ValueError: feature_names mismatch` when generating the regression evaluation plot.

**Diagnosis:** the training function dropped `unit_number` and `time_in_cycles` before fitting, but the corresponding `predict()` call at the plotting step only dropped the `rul` column, still passing the two identifier columns the model had never seen.

**Fix:** drop the same three columns at the call site that training dropped when fitting.

---

### 4. Autoencoder return-value unpacking mismatch, and dropped metrics

**Symptom:** `ValueError: too many values to unpack (expected 2)`.

**Diagnosis:** `train_autoencoder()` returns three values (model, threshold, metrics), but the pipeline only unpacked two. Once fixed, a second issue surfaced: the autoencoder's metrics were never merged into the final summary — only the isolation forest's were — so the two anomaly models couldn't be compared from the summary file alone.

**Fix:** capture all three return values; namespace both anomaly models' metrics separately in the summary (`{"isolation_forest": ..., "autoencoder": ...}`).

---

### 5. Regression and LSTM metrics silently overwrote each other in the summary

**Symptom:** `summary.json`'s `regression` block showed only the LSTM's numbers; XGBoost's real result (RMSE 12.25, R² 0.80) had disappeared with no error.

**Diagnosis:** `{**reg_metrics, **lstm_metrics}` was used to merge both models' metrics dicts. Both dicts use the identical key names (`rmse`, `mae`, `r2`), so the second dict silently overwrote the first — no exception, no warning, just data loss.

**Fix:** namespace both models explicitly: `{"xgboost": reg_metrics, "lstm": lstm_metrics}`, matching the pattern already used correctly for anomaly detection.

---

### 6. `torch.manual_seed()` alone was insufficient for LSTM reproducibility

**Symptom:** the same seed produced meaningfully different R² values across repeated runs of the RUL LSTM (0.78, 0.66, -0.64, -0.25) with identical code and data.

**Diagnosis:** confirmed via PyTorch's own reproducibility documentation and multiple independently reported issues that RNN/LSTM layers can use non-deterministic algorithms internally regardless of seeding, on both CPU and GPU.

**Fix:** add `torch.use_deterministic_algorithms(True)` alongside `torch.manual_seed()`. Verified bit-identical loss curves and predictions across repeated runs after the fix. Applied to both the RUL LSTM and the sensor forecasting LSTM.

---

### 7. LSTM RUL model was collapsing to predict the mean (target/input scale mismatch)

**Symptom:** even after fixing reproducibility, the RUL LSTM's training loss dropped sharply for a few epochs, then flatlined and stopped improving.

**Diagnosis:** the flatlined loss value (~1747) was almost exactly the variance of the unscaled RUL target (1736.6) — the mathematical signature of a model that has given up and is predicting close to the constant mean. Root cause: input features were MinMax-scaled to [0, 1] by the feature pipeline, but the RUL target was left unscaled (0–125), and the mismatch caused the optimizer to overshoot into this trivial local minimum.

**Fix:** scale the RUL target to [0, 1] to match the inputs during training; rescale predictions back to real cycle units for evaluation.

**Result:** R² improved from -0.25 to 0.77–0.78 on the official test set, now genuinely competitive with XGBoost (0.80).

---

### 8. Autoencoder anomaly detection was unseeded

**Symptom:** identical code produced different precision/recall/F1 on every run (precision ranged 12.8%–23.3% across runs).

**Diagnosis:** no random seed was set anywhere in the autoencoder's training function, so PyTorch's default weight initialization and Adam's stochastic training produced a genuinely different model every run.

**Fix:** add `torch.manual_seed()`. Verified sufficient here (unlike the LSTM cases above) — bit-identical results across repeated runs.

---

### 9. Forecasting model's output width didn't match its training target

**Symptom:** `UserWarning: Using a target size (torch.Size([N, 2])) that is different to the input size (torch.Size([N, 1]))` during training — the pipeline completed without crashing, but was silently training on incorrectly broadcast, meaningless loss values.

**Diagnosis:** the model's output layer was hard-coded to predict a single value, but the training target had width 2 (a 2-cycle forecast horizon). PyTorch silently broadcasts mismatched shapes instead of raising an error.

**Fix:** made the forecast horizon an explicit shared parameter flowing into both the target-construction code and the model's output layer, so the two can't silently diverge again.

---

### 10. Forecasting model was only ever trained to predict one non-sensor value

**Symptom:** even after fixing the output-width bug above, the model's single predicted output turned out to be `operational_setting_1` — an operating condition, not a real sensor reading — because the original code took "column index 0" of the feature set as its only target.

**Fix:** redesigned the model to predict all real sensor columns (15, after low-variance filtering) simultaneously for the full forecast horizon, with output width `n_sensors × horizon` reshaped at inference time.

---

### 11. RUL target was leaking into the forecasting model's own input features

**Symptom:** the backend forecasting service required a `rul` field from callers, which no real caller could supply (RUL is what other parts of this project predict, not something available at forecast-request time).

**Diagnosis:** `_prepare_sequences()` excluded only `unit_number` and `time_in_cycles` from the feature set, not `rul` — so when trained on the full engineered feature set (which includes the RUL column), the model had silently learned to use RUL as one of its own inputs.

**Fix:** exclude `rul` from the forecasting feature set. Model input size correctly dropped from 108 to 107.

---

### 12. Forecasting summary metrics were hardcoded, disconnected from the actual model

**Symptom:** `summary.json` always showed `{"forecasting": {"samples": 1}}`, regardless of how the forecasting model actually trained or performed.

**Diagnosis:** the pipeline's summary-construction step hardcoded this value directly, rather than reading the real metrics the forecasting training function wrote to its own `metrics.json`.

**Fix:** read the actual `forecasting/metrics.json` file into the summary, matching the pattern used for every other model.

---

### 13. Backend regression and forecasting services required pre-engineered input

**Symptom:** the `/predict/rul` and `/predict/forecast` API endpoints failed on any realistic raw-sensor payload, requiring ~107 pre-computed rolling/trend columns that no real caller would have.

**Diagnosis:** both services expected callers to have already run the training-time feature engineering themselves, rather than performing it internally from raw sensor history.

**Fix:** extracted the rolling/trend/baseline-diff feature-engineering logic into a shared module (`backend/app/services/cmapss_feature_builder.py`) used by both services, so each accepts raw sensor readings and builds its own engineered features internally — verified end-to-end against real API requests with raw sensor payloads.

---

### 14. Backend anomaly-detection endpoint returned a fabricated placeholder metric

**Symptom:** the `/predict/anomaly` endpoint's `autoencoder_reconstruction_error` field was computed as `isolation_forest_score * 0.1` — a number with no relationship to the actual autoencoder model.

**Fix:** wired real autoencoder inference into the endpoint: load the trained model, compute genuine reconstruction error against the request payload, compare to the saved training-time threshold.
