# sum-two-numbers

## Project Overview

`sum-two-numbers` is a simple command-line interface (CLI) application designed to quickly calculate the sum of two numbers. Built with Python, it leverages the `Click` library for robust argument parsing and a user-friendly experience.

**Key Features:**
- Accepts two numbers as input directly from the command line.
- Calculates the sum of the provided numbers.
- Outputs the calculated sum to the console.

**Target Audience:**
This script is intended for users who need a straightforward and efficient way to sum two numbers via a command-line utility.

**Technology Stack:**
- **CLI Framework:** Python with Click

## Setup Instructions

Follow these steps to set up the project locally.

### Prerequisites

Ensure you have Python 3.8 or newer installed on your system.

### 1. Clone the Repository

```bash
git clone <repository-url> # Replace <repository-url> with the actual URL
cd sum-two-numbers
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

- **On macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **On Windows (Command Prompt):**
  ```bash
  .venv\Scripts\activate.bat
  ```
- **On Windows (PowerShell):**
  ```bash
  .venv\Scripts\Activate.ps1
  ```

### 4. Install Dependencies

Install the required production dependencies:

```bash
pip install -r requirements.txt
```

For development, also install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## How to Run the Script

Once the setup is complete and your virtual environment is active, you can run the script.

The script expects two numbers as positional arguments.

```bash
python src/main.py <number1> <number2>
```

**Example:**

```bash
python src/main.py 5 10
```

**Expected Output:**

```
The sum is: 15
```

**Help Command:**

You can view the script's help message using the `--help` flag:

```bash
python src/main.py --help
```

## Development Guidelines

This project follows modern Python development practices to ensure code quality and maintainability.

### Project Structure

```
.
├── src/
│   └── main.py             # Main application logic
├── tests/
│   └── test_main.py        # Unit tests for the application
├── .venv/                  # Python virtual environment
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies (e.g., linters, testers)
└── README.md               # Project documentation
```

### Running Tests

We use `pytest` for testing. To run all tests:

```bash
pytest
```

### Linting and Formatting

`ruff` is used for linting and code formatting.

- To check for linting issues and formatting errors:
  ```bash
  ruff check .
  ```
- To automatically fix formatting errors and some linting issues:
  ```bash
  ruff format .
  ruff check . --fix
  ```

### Type Checking

`mypy` is used for static type checking to catch potential type-related bugs early.

```bash
mypy src/
```

### Contribution

Feel free to fork the repository, make improvements, and submit pull requests. Please ensure your contributions adhere to the existing code style and pass all tests and quality checks.