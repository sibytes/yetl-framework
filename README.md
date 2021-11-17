<img src="https://img.shields.io/badge/Python-v3.8-blue">

# YETL Framework - It's for Spark!

**Y**et another **ETL** **F**ramework for Spark


https://yetl-framework.readthedocs.io/en/latest/

# Development Setup

Create virual environment and install dependencies for local development:

```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install --editable .
```

# Configuration & Authentication

Azure databricks allows the following authentication methods:


# Build

Build python wheel:
```
python setup.py sdist bdist_wheel
```

There is a CI build configured for this repo that builds on main origin and publishes to PyPi.

# Test

Dependencies for testing:
```
pip install --editable .
```

Run tests:
```
pytest
```

Test Coverage:
```
pytest --cov=autobricks --cov-report=html
```

View the report in a browser:
```
./htmlcov/index.html
```


