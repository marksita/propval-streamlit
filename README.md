# PropVal AU — Streamlit Edition

Free Australian property market valuation app. No API costs, no sign-up required.

## Deploy to Streamlit Community Cloud (free)

### 1. Push to GitHub

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/propval-streamlit.git
git push -u origin main

### 2. Deploy on Streamlit Cloud

1. Go to share.streamlit.io and sign in with GitHub
2. Click New app
3. Select your repo: YOUR_USERNAME/propval-streamlit
4. Main file path: app.py
5. Click Deploy

## Local development

pip install streamlit
streamlit run app.py
