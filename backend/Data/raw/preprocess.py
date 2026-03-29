import pandas as pd
import re, emoji, os
from sklearn.model_selection import train_test_split

# === CONFIGURATION ===
RAW_DATA_PATH = r"C:\Users\omond\Desktop\sentiment_analysis_project\sentiment-clean\backend\Data\safaricom_tweets_enhanced.csv"
OUTPUT_DIR = r"C:\Users\omond\Desktop\sentiment_analysis_project\sentiment-clean\backend\Data\processed"

# === CLEANING FUNCTION ===
def clean_text(text):
    text = str(text).lower()

    # Remove URLs, mentions, hashtags
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Convert emojis to text (😊 → :smiling_face:)
    text = emoji.demojize(text)

    return text

def main():
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ RAW FILE NOT FOUND: {RAW_DATA_PATH}")
        return
    
    print("📥 Loading raw dataset...")
    df = pd.read_csv(RAW_DATA_PATH)

    # Standardize column names from synthetic dataset
    if "Content" in df.columns:
        df.rename(columns={"Content":"text"}, inplace=True)
    if "Sentiment" in df.columns:
        df.rename(columns={"Sentiment":"sentiment"}, inplace=True)
    if "Date" in df.columns:
        df.rename(columns={"Date":"created_at"}, inplace=True)
    if "User" in df.columns:
        df.rename(columns={"User":"username"}, inplace=True)
    if "Post ID" in df.columns:
        df.rename(columns={"Post ID":"post_id"}, inplace=True)

    print("🧹 Cleaning tweets...")
    df["clean_text"] = df["text"].apply(clean_text)

    # Ensure sentiment column exists
    if "sentiment" not in df.columns:
        raise ValueError("❌ Sentiment column missing in dataset. Synthetic dataset must include sentiment labels.")

    print("✂️ Splitting into train & test sets...")
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df["sentiment"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    train.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
    test.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)

    print("✅ Preprocessing complete!")
    print(f"Training set → {train.shape} saved to {OUTPUT_DIR}/train.csv")
    print(f"Test set     → {test.shape} saved to {OUTPUT_DIR}/test.csv")

if __name__ == "__main__":
    main()
