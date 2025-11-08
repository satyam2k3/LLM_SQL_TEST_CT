# Installation and Running Instructions

## 🛠️ Installation

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
cd crewai_nl2sql
pip install -r requirements.txt
```

## 🚀 Running the Application

### Option 1: Demo Mode (No API Key Required)
Run the architecture demonstration without any API keys:

```bash
python test_pipeline.py
```

This will show:
- Pipeline flow demonstration
- Database schema overview
- Business rules
- Available metrics

### Option 2: With OpenAI API Key
If you have an OpenAI API key:

1. Create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

2. Run the application:
```bash
python main.py
```

### Option 3: Simple Runner
Use the convenient runner script:

```bash
python run.py
```

This will:
- Check for API keys
- Offer demo mode if no key found
- Provide interactive options

## 🎯 Quick Test

To see the pipeline in action immediately:

```bash
# Demo without API key
python test_pipeline.py
# Then choose option 1 to see the full pipeline flow
```

## 🔧 Troubleshooting

### Dependency Issues
If you encounter any dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Import Errors
Make sure you're in the correct directory:
```bash
cd crewai_nl2sql
python main.py
```

### Windows PowerShell Issues
If you get execution policy errors on Windows:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
