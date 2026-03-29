@echo off
:restart
echo [%date% %time%] Starting System...
streamlit run app.py
echo [%date% %time%] System crashed or closed. Restarting in 5 seconds...
timeout /t 5
goto restart
