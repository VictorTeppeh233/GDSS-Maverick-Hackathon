# GDSS-Maverick-Hackathon
AI-Driven Image-to-Item Master Data Tool (IMDB Auto-Fill from Product Images)

# 🚀 Setup and Run Guide: GDS-Maverick AI IMDB Tool

Welcome to the AI-Driven Image-to-IMDB application! Follow these instructions to get the application running on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python 3.8+**
- **pip** (Python package installer)
- A **Google Gemini API Key**. You can get one for free from Google AI Studio.

---

## 🛠️ Installation Steps

### 1. Clone or Download the Repository
Navigate to the directory containing the project files (`app.py`, `extractor.py`, `validator.py`, etc.).

```bash
cd path/to/GDS-Maverick-Hackathon
```

### 2. Set Up a Virtual Environment (Recommended)
It is always a good practice to use a virtual environment to manage your dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS and Linux:
source venv/bin/activate
```

### 3. Install Required Dependencies
Install all necessary Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

*(This will install `streamlit`, `pandas`, `openpyxl`, `google-genai`, and `python-dotenv`.)*

---

## 🔐 Environment Configuration

The application requires your Gemini API key to communicate with Google's AI models. For security, we store this in a `.env` file instead of putting it directly in the code.

1. Inside the `GDS-Maverick-Hackathon` folder, create a new file named exactly `.env`.
2. Open the `.env` file and add your API key like this:

```env
GEMINI_API_KEY="your_actual_api_key_here"
```

> **Note:** Never commit the `.env` file to a public GitHub repository.

---

## ▶️ Running the Application

Once your dependencies are installed and your API key is set, you are ready to launch the app!

1. Make sure your virtual environment is still active.
2. Run the Streamlit server using the following command:

```bash
streamlit run app.py
```

3. Your default web browser will automatically open a new tab pointing to `http://localhost:8501`. 
4. The application is now running! Any products you process and save will automatically be written to a local `predictions.xlsx` file in the same directory.

---

## 📂 Project Structure

- **`app.py`**: The main frontend application and Streamlit UI code.
- **`extractor.py`**: Handles image preprocessing and API calls to Google's Gemini models.
- **`validator.py`**: Validates the AI output and flags low-confidence data points.
- **`.streamlit/config.toml`**: Custom aesthetic configurations (Dark theme, Electric Purple accents).
- **`predictions.xlsx`**: The master database file that is generated when you save your first item.
