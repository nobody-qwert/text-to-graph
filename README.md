## 🚀 Knowledge Graph Generator

- **Optimized Efficiency:** Leverages CSV instead of JSON, reducing output tokens for responses that are **3x faster and cheaper**.  
- **Blazing Performance:** Supports **parallel API calls**, ensuring maximum throughput and seamless scalability.  
- **Enhanced Precision:** Integrates an **external PDF extractor**, crafted in C++ for unparalleled speed and accuracy in text extraction.  
- **All-in-One Output:** Creates a **self-contained HTML file** combining graph visuals and data, making sharing and navigation effortless.

## Check Out Sample Graphs Here

[Sample Graphs](https://bizbas.com/)

## Prerequisites

- Make sure Python is installed on your system. You can download it from [python.org](https://www.python.org/).
- Ensure `pip` (Python package installer) is available by running `pip --version` in Command Prompt.

## Setup Instructions

### Step 1: Clone the Repository (if applicable)

If you're setting up from a Git repository, clone it to your local system:

```bash
git clone https://github.com/nobody-qwert/text-to-graph.git
cd text-to-graph
```

### Step 2: Create a Virtual Environment

In your project directory, create a virtual environment to isolate your project dependencies:
```
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

To activate the virtual environment, run:

```
.venv\Scripts\activate
```

Once activated, you should see the environment name (e.g., .venv) in your command prompt.
### Step 4: Install Project Dependencies

Install the required Python packages by using the requirements.txt file provided:

```
pip install -r requirements.txt
```

This command installs all dependencies listed in requirements.txt into your virtual environment.

### Additional Tips
Deactivate the virtual environment when done by simply typing:

```
deactivate
```

### Running the script in Console
Go to directory
```
cd graph_extractor\src
```

Generates graph
```
python.exe .\gui.py
```
