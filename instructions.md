uv init
uv python install 3.12
uv python pin 3.12
uv venv
.venv\Scripts\activate
python --version

mkdir data\raw
mkdir src\nlp
mkdir src\dashboard

uv add pandas numpy openpyxl streamlit textblob spacy plotly

uv pip install ntscraper
uv pip install apify-client

python src\nlp\fetch_tweets.py
python src\nlp\classify_traffic.py

streamlit run src\dashboard\app.py
