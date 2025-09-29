@echo off
echo --------------------------------------------------
echo Checking Python version...
python --version

echo Checking pip version...
pip --version

echo --------------------------------------------------
set /p proceed="Do you want to install required Python modules? (Y/n): "

if /I "%proceed%"=="Y" (
    echo Installing Python modules...
    pip install -r requirements.txt

    echo --------------------------------------------------
    echo The installation has been finished successfully!
) else (
    echo Installation cancelled by user.
)

echo --------------------------------------------------
echo Now Open the run.bat file to use the Application
echo

pause
