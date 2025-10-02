# Python Chatbot - Installation Guide

## Required Dependencies

Based on the code analysis, your chatbot project requires the following Python packages:

```
customtkinter>=5.0.0
scikit-learn>=1.0.0
PyMuPDF>=1.19.0
python-docx>=0.8.11
PyPDF2>=3.0.0
```

## Installation Instructions

1. Create a `requirements.txt` file in your project directory with the content above.

2. Install all dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

## Alternative Installation (Direct pip install)

If you prefer to install packages directly without a requirements.txt file:

```
pip install customtkinter scikit-learn PyMuPDF python-docx PyPDF2
```

## Verification

After installation, you can verify that all packages are installed correctly by running:
```
pip list
```

This should show all the installed packages including the ones listed above.

## Running the Application

Once all dependencies are installed, you can run your chatbot with:
```
python main.py