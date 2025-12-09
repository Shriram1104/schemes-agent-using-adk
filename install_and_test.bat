@echo off
echo ========================================
echo Google ADK Scheme Assistant Setup
echo ========================================
echo.

echo Step 1: Installing Google ADK and dependencies...
pip install google-adk
pip install google-cloud-aiplatform
pip install google-cloud-discoveryengine
pip install pydantic
pip install python-dotenv
pip install fastapi
pip install uvicorn

echo.
echo Step 2: Checking installation...
python -c "import google.adk; print('✓ google-adk installed')"
python -c "import google.cloud.aiplatform; print('✓ google-cloud-aiplatform installed')"
python -c "import google.cloud.discoveryengine_v1; print('✓ google-cloud-discoveryengine installed')"

echo.
echo Step 3: Verifying project structure...
if not exist "src\agents" mkdir src\agents
if not exist "src\services" mkdir src\services
if not exist "src\models" mkdir src\models
if not exist "config" mkdir config
if not exist "tests" mkdir tests

echo ✓ Project structure verified

echo.
echo Step 4: Creating __init__.py files...
type nul > src\__init__.py
type nul > src\agents\__init__.py
type nul > src\services\__init__.py
type nul > src\models\__init__.py
type nul > config\__init__.py
echo ✓ __init__.py files created

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update your .env file with GCP credentials
echo 2. Replace the agent files with corrected versions
echo 3. Run: python -m src.app
echo.
pause