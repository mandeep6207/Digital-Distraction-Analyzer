# Digital Distraction Analyzer

A lightweight Flask web app for estimating daily digital distraction from screen time, social media use, productive hours, and app switching.

## Features

- Distraction Score from 0 to 100
- Focus level classification
- Dynamic insights and suggestions
- Pie chart for time distribution
- Bar chart for productivity vs distraction
- Bootstrap 5 dashboard UI

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Test

```bash
python -m unittest discover -s tests
```
