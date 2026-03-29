import pandas as pd
import numpy as np
import pickle
import os
import random  
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight  
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping  

# === CONFIGURATION ===
TRAIN_PATH = r"C:\Users\omond\Desktop\sentiment_analysis_project\sentiment-clean\backend\Data\processed\train.csv"
TEST_PATH  = r"C:\Users\omond\Desktop\sentiment_analysis_project\sentiment-clean\backend\Data\processed\test.csv"
GLOVE_PATH = "embeddings/glove.6B.100d.txt"

MAX_WORDS = 20000
MAX_LEN   = 50
EMBED_DIM = 100
EPOCHS = 10  

# Label mapping for categorical conversion
label_map = {"positive": 0, "negative": 1, "neutral": 2}

# === LOAD DATA ===
def load_data():
    train = pd.read_csv(TRAIN_PATH)
    test  = pd.read_csv(TEST_PATH)

    # Ensure clean_text exists (should already be there from preprocessing)
    if "clean_text" not in train.columns:
        train["clean_text"] = train["text"].astype(str).str.lower()
    if "clean_text" not in test.columns:
        test["clean_text"] = test["text"].astype(str).str.lower()

    # Fill NaN values
    train["clean_text"] = train["clean_text"].fillna("")
    test["clean_text"] = test["clean_text"].fillna("")

    # Ensure sentiment column exists
    if "sentiment" not in train.columns or "sentiment" not in test.columns:
        raise ValueError("❌ Sentiment column missing in dataset. Preprocessed data must include sentiment labels.")

    return train, test

# === MANUAL AUGMENTATION ===
def augment_text(text):
    synonyms = {
        'expensive': 'ghali', 'like': 'kupenda', 'good': 'poa', 'bad': 'mbaya',
        'slow': 'polepole', 'fast': 'haraka', 'reliable': 'salama', 'unreliable': 'mbaya'
    }
    words = text.split()
    for i in range(len(words)):
        word = words[i]
        if word in synonyms and random.random() < 0.3:
            words[i] = synonyms[word]
    # Random swap
    if len(words) > 3 and random.random() < 0.2:
        idx1, idx2 = random.sample(range(len(words)), 2)
        words[idx1], words[idx2] = words[idx2], words[idx1]
    return ' '.join(words)

# === BASELINE MODEL ===
def train_baseline_model(train, test):
    print("\n🔹 Training TF-IDF + Logistic Regression Baseline...")

    # Apply augmentation
    train["clean_text"] = train["clean_text"].apply(augment_text)

    vectorizer = TfidfVectorizer(max_features=7000, ngram_range=(1,2))
    X_train = vectorizer.fit_transform(train["clean_text"])
    X_test  = vectorizer.transform(test["clean_text"])

    clf = LogisticRegression(max_iter=600, class_weight="balanced")
    clf.fit(X_train, train["sentiment"])

    preds = clf.predict(X_test)

    print("\n📊 Baseline Model Results:")
    print(classification_report(test["sentiment"], preds))

    os.makedirs("models", exist_ok=True)
    with open("models/baseline_tfidf.pkl", "wb") as f:
        pickle.dump((vectorizer, clf), f)

# === LOAD GLOVE EMBEDDINGS ===
def load_glove_embeddings():
    print("\n🔹 Loading GloVe embeddings...")
    embeddings_index = {}

    with open(GLOVE_PATH, encoding="utf8") as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype="float32")
            embeddings_index[word] = coefs

    print(f"✔ Loaded {len(embeddings_index)} word vectors.")
    return embeddings_index

# === LSTM MODEL ===
def train_lstm_model(train, test, embeddings_index):
    print("\n🔹 Preparing LSTM model input...")

    # Apply augmentation
    train["clean_text"] = train["clean_text"].apply(augment_text)

    tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
    tokenizer.fit_on_texts(train["clean_text"])

    X_train = pad_sequences(tokenizer.texts_to_sequences(train["clean_text"]), maxlen=MAX_LEN)
    X_test  = pad_sequences(tokenizer.texts_to_sequences(test["clean_text"]), maxlen=MAX_LEN)

    y_train = to_categorical(train["sentiment"].map(label_map))
    y_test  = to_categorical(test["sentiment"].map(label_map))

    # Compute class weights - FIXED HERE
    unique_classes = np.unique(train["sentiment"])
    class_weights = compute_class_weight('balanced', classes=unique_classes, y=train["sentiment"])
    class_weight_dict = {label_map[cls]: weight for cls, weight in zip(unique_classes, class_weights)}

    embedding_matrix = np.zeros((MAX_WORDS, EMBED_DIM))
    word_index = tokenizer.word_index

    for word, i in word_index.items():
        if i < MAX_WORDS:
            vec = embeddings_index.get(word)
            if vec is not None:
                embedding_matrix[i] = vec

    model = Sequential([
        Embedding(MAX_WORDS, EMBED_DIM, weights=[embedding_matrix], input_length=MAX_LEN, trainable=True),  # Set trainable=True
        LSTM(128),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(3, activation='softmax')
    ])

    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.summary()

    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)  # Added

    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=64,
        verbose=1,
        class_weight=class_weight_dict,  # Added
        callbacks=[early_stopping]
    )

    print("\n📊 Evaluating LSTM Model...")
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"✔ LSTM Accuracy: {acc:.4f}")

    # Per-class report
    preds = np.argmax(model.predict(X_test), axis=1)
    true_labels = np.argmax(y_test, axis=1)
    print("\n📊 LSTM Classification Report:")
    print(classification_report(true_labels, preds, target_names=list(label_map.keys())))

    # Save models
    os.makedirs("models", exist_ok=True)
    model.save("models/lstm_model.keras")
    with open("models/tokenizer.pkl", "wb") as f:
        pickle.dump(tokenizer, f)
    with open("models/label_map.pkl", "wb") as f:
        pickle.dump(label_map, f)

# === MAIN ===
def main():
    train, test = load_data()
    train_baseline_model(train, test)
    embeddings_index = load_glove_embeddings()
    train_lstm_model(train, test, embeddings_index)

if __name__ == "__main__":
    main()