# Resume-Job Matching System

A sophisticated AI-powered system built with LangChain and LangGraph that automatically matches resumes with job descriptions using multiple specialized agents.

## 🎯 Features

- **Multi-Agent Architecture**: Three specialized agents working together
  - **Resume Agent**: Extracts and analyzes resume content from PDF files
  - **Job Description Agent**: Parses and structures job requirements
  - **Matching Agent**: Performs intelligent matching and ranking

- **Advanced PDF Processing**: Robust PDF text extraction with multiple fallback methods
- **Intelligent Skill Matching**: Uses semantic similarity and NLP techniques
- **Experience Level Assessment**: Evaluates candidate experience against job requirements
- **Comprehensive Ranking**: Provides detailed matching scores and recommendations
- **LangGraph Workflow**: Orchestrates the entire process with a visual workflow

## 🏗️ Architecture

```
📁 resume_job_matcher/
├── 🔧 config/           # Configuration and settings
├── 🤖 agents/           # Three specialized agents
├── 📊 models/           # Data models and schemas
├── 🛠️ utils/            # Utility functions
├── 🔄 workflows/        # LangGraph workflow orchestration
├── 🧪 tests/            # Comprehensive test suite
├── 📋 main.py           # Main application entry point
├── 📄 pyproject.toml    # Project configuration with uv
└── 🔒 uv.lock          # Dependency lock file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (recommended: 3.11+)
- [uv](https://docs.astral.sh/uv/) - Ultra-fast Python package installer

### 1. Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip (if you prefer)
pip install uv

# Using Homebrew (macOS)
brew install uv
```

### 2. Project Setup

```bash
# Clone the repository
git clone <repository-url>
cd resume_job_matcher

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Download required NLTK data
uv run python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

### 4. Usage

#### Command Line Interface

```bash
# Basic usage
uv run python main.py --resume path/to/resume.pdf --jobs "Job description 1" "Job description 2" "Job description 3" "Job description 4" "Job description 5"

# Using job description files
uv run python main.py -r resume.pdf -j job1.txt job2.txt job3.txt job4.txt job5.txt

# Save results to file
uv run python main.py -r resume.pdf -j job1.txt job2.txt job3.txt job4.txt job5.txt -o results.json

# Verbose output
uv run python main.py -r resume.pdf -j "job desc 1" "job desc 2" "job desc 3" "job desc 4" "job desc 5" -v
```

#### Programmatic Usage

```python
from main import ResumeJobMatcher

# Initialize the matcher
matcher = ResumeJobMatcher()

# Define job descriptions
job_descriptions = [
    "Senior Python Developer with Django experience...",
    "Data Scientist with machine learning expertise...",
    "Full Stack Developer with React and Node.js...",
    "DevOps Engineer with AWS and Docker skills...",
    "Machine Learning Engineer with TensorFlow..."
]

# Run matching process
results = matcher.process_resume_job_matching("resume.pdf", job_descriptions)

# Print formatted results
matcher.print_results(results)

# Save results
matcher.save_results_to_file(results, "matching_results.json")
```

## 🤖 Agent Details

### Resume Agent (`ResumeAgent`)
- **Purpose**: Analyzes PDF resumes and extracts structured information
- **Capabilities**:
  - PDF text extraction with fallback methods
  - Personal information extraction (name, email, phone)
  - Skills identification and categorization
  - Experience analysis and years calculation
  - Education and certification parsing

### Job Description Agent (`JobDescriptionAgent`)
- **Purpose**: Processes job descriptions and identifies requirements
- **Capabilities**:
  - Job information parsing (title, company, location)
  - Required vs. preferred skills distinction
  - Experience level determination
  - Responsibility and qualification extraction
  - Seniority level assessment

### Matching Agent (`MatchingAgent`)
- **Purpose**: Performs intelligent matching between resumes and jobs
- **Capabilities**:
  - Semantic skill matching with similarity scores
  - Experience level compatibility assessment
  - Overall compatibility scoring
  - Personalized recommendations generation
  - Job ranking and prioritization

## 🔄 Workflow Process

The LangGraph workflow orchestrates the entire matching process:

1. **📄 Resume Analysis**
   - Extract and validate PDF content
   - Parse personal and professional information
   - Structure resume data

2. **💼 Job Description Analysis**
   - Process multiple job descriptions
   - Extract requirements and preferences
   - Standardize job data format

3. **🎯 Intelligent Matching**
   - Compare skills with semantic understanding
   - Evaluate experience compatibility
   - Calculate comprehensive match scores

4. **📊 Results Generation**
   - Rank job opportunities
   - Generate detailed recommendations
   - Create actionable insights

## 📊 Output Example

```
🎯 BEST JOB MATCH FOUND!

Top Recommendation: Senior Python Developer
Company: TechCorp Inc.
Match Score: 87%
Ranking: #1

Why this is a great match:
Excellent match! You have 8/10 required skills and meet experience requirements.

Skills Matched: 8/10
Experience Match: ✅ Yes

Top 3 Job Recommendations:
1. Senior Python Developer - 87% match
2. Full Stack Developer - 76% match
3. Data Scientist - 68% match

Recommendations:
• Prioritize applying to Senior Python Developer - it's an excellent match!
• Consider developing these in-demand skills: Docker, Kubernetes, GraphQL
• Focus on senior and leadership positions that match your experience level.
```

## 📦 Dependency Management with uv

### Adding New Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev pytest

# Add with specific version
uv add "package-name>=1.0.0"

# Add from specific index
uv add package-name --index https://pypi.org/simple/
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name --upgrade

# Check for outdated packages
uv tree --outdated
```

### Lock File Management

```bash
# Generate/update lock file
uv lock

# Install from lock file
uv sync --frozen

# Export requirements.txt (for compatibility)
uv export --format requirements-txt --output-file requirements.txt
```

## ⚙️ Configuration

### pyproject.toml

```toml
[project]
name = "resume-job-matcher"
version = "1.0.0"
description = "AI-powered resume-job matching system with LangChain and LangGraph"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "langchain>=0.1.0",
    "langchain-openai>=0.0.5",
    "langchain-community>=0.0.10",
    "langgraph>=0.0.20",
    "PyPDF2>=3.0.1",
    "pdfplumber>=0.9.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "spacy>=3.7.2",
    "nltk>=3.8.1",
    "scikit-learn>=1.3.2",
    "openai>=1.3.0",
    "python-dotenv>=1.0.0",
    "sentence-transformers>=2.2.2",
]
requires-python = ">=3.9"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
resume-matcher = "main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[tool.black]
line-length = 100
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.9"
strict = true
```

### Environment Configuration

Key configuration options in `config/settings.py`:

```python
# Model Configuration
openai_model: str = "gpt-3.5-turbo"
temperature: float = 0.1
max_tokens: int = 2000

# Processing Configuration
min_job_descriptions: int = 5  # Minimum job descriptions required
max_job_descriptions: int = 10  # Maximum to process
similarity_threshold: float = 0.6  # Skill matching threshold

# File Processing
max_file_size_mb: int = 10
supported_formats: list = ["pdf"]
```

## 🧪 Testing

Run the comprehensive test suite with uv:

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html

# Run specific test file
uv run python tests/test_agents.py

# Run tests in parallel
uv run pytest tests/ -n auto
```

### Development Tools

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run flake8 .

# Type checking
uv run mypy .

# Run all quality checks
uv run python -m pytest && uv run black --check . && uv run isort --check . && uv run flake8 && uv run mypy
```

## 📋 Requirements

- **Python**: 3.9+ (recommended: 3.11+)
- **uv**: Latest version for dependency management
- **OpenAI API key**: Required for AI capabilities
- **System Dependencies**: 
  - For PDF processing: No additional system packages needed
  - For advanced NLP: Optional spaCy language models

### Installing spaCy Language Models

```bash
# Install English language model
uv run python -m spacy download en_core_web_sm

# Install larger model for better accuracy
uv run python -m spacy download en_core_web_lg
```

## 🔧 Development Setup

### Initial Setup

```bash
# Clone and setup
git clone <repository-url>
cd resume_job_matcher

# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Development Workflow

```bash
# Add new feature dependency
uv add new-package

# Add development tool
uv add --dev new-dev-tool

# Update dependencies
uv sync --upgrade

# Run development server/script
uv run python main.py --help
```

## 🐛 Troubleshooting

### Common Issues

1. **uv Installation Problems**
   ```bash
   # If uv command not found, ensure it's in PATH
   export PATH="$HOME/.cargo/bin:$PATH"
   
   # Or reinstall
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   uv sync
   ```

3. **Dependency Conflicts**
   ```bash
   # Check dependency tree
   uv tree
   
   # Resolve conflicts
   uv sync --refresh
   ```

4. **PDF Reading Errors**
   - Ensure PDF is not password-protected
   - Try different PDF files
   - Check file permissions

5. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Ensure model access

### Performance Optimization

```bash
# Install with compiled packages when available
uv sync --compile-bytecode

# Use faster resolver
uv add package-name --resolution=lowest-direct

# Clear cache if needed
uv cache clean
```

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY . /app
WORKDIR /app

# Install dependencies
RUN uv sync --frozen --no-cache

# Run application
CMD ["uv", "run", "python", "main.py"]
```

### Production Setup

```bash
# Install production dependencies only
uv sync --no-dev --frozen

# Set production environment
export ENVIRONMENT=production
export OPENAI_API_KEY=your_production_key

# Run application
uv run python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `uv sync`
4. Make your changes
5. Run tests and quality checks:
   ```bash
   uv run pytest
   uv run black .
   uv run isort .
   uv run flake8
   uv run mypy .
   ```
6. Update dependencies if needed: `uv add new-package`
7. Commit changes: `git commit -am 'Add feature'`
8. Push to branch: `git push origin feature-name`
9. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- Dependency management powered by [uv](https://docs.astral.sh/uv/)
- PDF processing with [PyPDF2](https://pypdf2.readthedocs.io/) and [pdfplumber](https://github.com/jsvine/pdfplumber)
- Text analysis using [scikit-learn](https://scikit-learn.org/) and [spaCy](https://spacy.io/)
- AI capabilities provided by [OpenAI](https://openai.com/)

---

**Made with ❤️ and ⚡ uv for blazing-fast development**
