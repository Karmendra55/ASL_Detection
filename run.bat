@echo off
title  Launching ASL App 

:: Clear the screen
cls

::  ASCII banner
echo =====================================
echo        American Sign Language App 
echo =====================================
echo.

:: Run Streamlit
echo Launching Streamlit...
streamlit run main.py

:: Keep the window open after closing the app
echo.
echo Streamlit has exited. Press any key to close this window.
pause >nul
