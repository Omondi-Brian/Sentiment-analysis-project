import os
import psycopg2

def get_connection():
    return psycopg2.connect(os.environ["postgresql://sentiment_analysis_postgres_k887_user:9wBfmi5tsASZxfDHoh2l6kqDmaWs31GW@dpg-d745kduuk2gs739vmlgg-a/sentiment_analysis_postgres_k887"])
