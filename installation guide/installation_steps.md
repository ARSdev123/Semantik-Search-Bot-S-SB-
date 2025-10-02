# Installation Steps for Python Chatbot

## Step 1: Create requirements.txt file

Create a new file named `requirements.txt` in your project directory with the following content:

```
customtkinter>=5.0.0
scikit-learn>=1.0.0
PyMuPDF>=1.19.0
python-docx>=0.8.11
PyPDF2>=3.0.0
```

## Step 2: Install dependencies using pip

Open a terminal/command prompt in your project directory and run:

```
pip install -r requirements.txt
```

Alternatively, you can install packages individually:

```
pip install customtkinter
pip install scikit-learn
pip install PyMuPDF
pip install python-docx
pip install PyPDF2
```

## Step 3: Verify installation

After installation, verify that all packages were installed correctly:

```
pip list
```

This should show all the installed packages including:
- customtkinter
- scikit-learn
- PyMuPDF (fitz)
- python-docx
- PyPDF2

## Step 4: Test the application

Once all dependencies are installed, test your chatbot:

```
python main.py
```

If everything is installed correctly, the chatbot GUI should launch without errors.

## Troubleshooting

If you encounter any issues:

1. Make sure you're using Python 3.7 or higher
2. If you get permission errors, try using:
   ```
   pip install --user -r requirements.txt
   ```
3. If you're using a virtual environment, make sure it's activated
4. For Windows users, if PyMuPDF installation fails, you might need to install Microsoft Visual C++ Build Tools