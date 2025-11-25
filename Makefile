install:
	@echo "Installing required packages..."
	pip install --upgrade pip
   	pip install -r requirements.txt

format:
	@echo "Formatting code with ruff..."
	ruff format .

lint:
	@echo "Linting code with ruff..."
	ruff check .