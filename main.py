from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import pickle
import numpy as np
import pandas as pd
import io
import datetime
import logging
import time  
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load Models 

try:
    with open("models/baseline_tfidf.pkl", "rb") as f:
        vectorizer, baseline_model = pickle.load(f)
    lstm_model = load_model("models/lstm_model.keras")

    with open("models/tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    with open("models/label_map.pkl", "rb") as f:
        label_map = pickle.load(f)
    inv_label_map = {v: k for k, v in label_map.items()}
    MAX_LEN = 50
    logger.info("Models loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    raise RuntimeError("Model loading failed.")


# Load Dataset for Analytics

try:
    DATASET = pd.read_csv(r"backend\Data\processed\train.csv")
    logger.info("Dataset loaded successfully.")
except Exception as e:
    logger.warning(f"Failed to load dataset: {e}")
    DATASET = None

app = FastAPI()

class TextInput(BaseModel):
    text: str


# Simple In-Memory Cache

CACHE = {}
CACHE_TTL = 300  

def get_cache(key):
    entry = CACHE.get(key)
    if entry and (time.time() - entry["time"] < CACHE_TTL):
        return entry["value"]
    return None

def set_cache(key, value):
    CACHE[key] = {"value": value, "time": time.time()}


# Helpers

def predict_baseline_batch(texts):
    X = vectorizer.transform(texts)
    raw_preds = baseline_model.predict(X)
    return [inv_label_map[int(r)] if not isinstance(r, str) else r for r in raw_preds]

def predict_lstm_batch(texts):
    seqs = tokenizer.texts_to_sequences(texts)
    pad = pad_sequences(seqs, maxlen=MAX_LEN)
    probs = lstm_model.predict(pad, batch_size=128, verbose=0)
    labels = [inv_label_map[int(np.argmax(p))] for p in probs]
    confs = [float(np.max(p)) for p in probs]
    return labels, confs


# A: Single Prediction

@app.post("/predict")
def predict(input: TextInput):
    baseline_pred = predict_baseline_batch([input.text])[0]
    lstm_pred, conf = predict_lstm_batch([input.text])
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "baseline_prediction": baseline_pred,
        "lstm_prediction": lstm_pred[0],
        "confidence": conf[0]
    }


# B: Bulk CSV Prediction

@app.post("/bulk_predict")
async def bulk_predict(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    possible_text_cols = ["text", "Content", "Tweet", "message"]
    text_col = next((col for col in possible_text_cols if col in df.columns), None)
    if text_col is None:
        return JSONResponse(status_code=400, content={"error": "CSV must contain a text column"})

    if text_col != "text":
        df.rename(columns={text_col: "text"}, inplace=True)

    df["baseline_prediction"] = predict_baseline_batch(df["text"].tolist())
    lstm_labels, lstm_confs = predict_lstm_batch(df["text"].tolist())
    df["lstm_prediction"] = lstm_labels
    df["confidence"] = lstm_confs

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    return StreamingResponse(buf, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bulk_predictions.csv"})


# C1: Analytics — Summary Stats

@app.get("/analytics/summary")
def analytics_summary():
    cached = get_cache("summary")
    if cached:
        return cached

    if DATASET is None or "sentiment" not in DATASET.columns:
        result = {"total": 0, "counts": {}, "percentages": {}}
    else:
        counts = DATASET["sentiment"].value_counts().to_dict()
        total = sum(counts.values())
        percentages = {k: round((v/total)*100, 2) for k, v in counts.items()} if total > 0 else {}
        result = {"total": total, "counts": counts, "percentages": percentages}

    set_cache("summary", result)
    return result


# C2: Analytics — Time Series

@app.get("/analytics/timeseries")
def analytics_timeseries():
    cached = get_cache("timeseries")
    if cached:
        return cached

    if DATASET is None or "created_at" not in DATASET.columns:
        result = []
    else:
        df = DATASET.copy()
        df["date"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
        df = df.dropna(subset=["date"])
        aggregated = df.groupby(["date", "sentiment"]).size().unstack(fill_value=0).reset_index()
        result = aggregated.to_dict(orient="records")

    set_cache("timeseries", result)
    return result


# C3: Analytics — Model Comparison

@app.get("/analytics/model_compare")
def analytics_model_compare():
    cached = get_cache("model_compare")
    if cached:
        return cached

    try:
        test_df = pd.read_csv(r"backend\Data\processed\test.csv")
    except Exception as e:
        logger.error(f"Failed to load test.csv: {e}")
        result = {
            "baseline": {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0},
            "lstm": {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0},
            "error": f"Failed to load test.csv: {str(e)}"
        }
        set_cache("model_compare", result)
        return JSONResponse(content=result, status_code=500)

    if "sentiment" not in test_df.columns or "clean_text" not in test_df.columns:
        result = {
            "baseline": {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0},
            "lstm": {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0},
            "error": "Missing sentiment or clean_text columns in test.csv"
        }
        set_cache("model_compare", result)
        return JSONResponse(content=result, status_code=400)

    test_df["clean_text"] = test_df["clean_text"].fillna("")
    true = test_df["sentiment"].tolist()

    base_preds = predict_baseline_batch(test_df["clean_text"].tolist())
    lstm_labels, _ = predict_lstm_batch(test_df["clean_text"].tolist())

    base_acc = accuracy_score(true, base_preds)
    lstm_acc = accuracy_score(true, lstm_labels)

    base_prec, base_rec, base_f1, _ = precision_recall_fscore_support(
        true, base_preds, average="weighted", zero_division=0
    )
    lstm_prec, lstm_rec, lstm_f1, _ = precision_recall_fscore_support(
        true, lstm_labels, average="weighted", zero_division=0
    )

    result = {
        "baseline": {
            "accuracy": base_acc,
            "precision": base_prec,
            "recall": base_rec,
            "f1": base_f1
        },
        "lstm": {
            "accuracy": lstm_acc,
            "precision": lstm_prec,
            "recall": lstm_rec,
            "f1": lstm_f1
        }
    }

    set_cache("model_compare", result)
    return JSONResponse(content=result)
