@echo off
title STEM Robotics Project Launcher

:menu
cls
echo ==========================================
echo   STEM ROBOTICS PROJECT LAUNCHER
echo ==========================================
echo.
echo  [1] Hexapod Leg Coordination (CPG)
echo  [2] Motion Planning Demonstrator
echo  [3] Robot Posture Validation
echo  [4] Safe Motion Transitions
echo  [5] Exit
echo.
echo ==========================================
set /p choice="Select a project to launch (1-5): "

if "%choice%"=="1" goto hexapod
if "%choice%"=="2" goto motion
if "%choice%"=="3" goto posture
if "%choice%"=="4" goto safe
if "%choice%"=="5" exit

echo Invalid choice! Please try again.
timeout /t 2 >nul
goto menu

:hexapod
streamlit run hexapod_cpg_simulator\app.py
pause
goto menu

:motion
streamlit run motion_planning_demo\app.py
pause
goto menu

:posture
streamlit run robot_posture_validation\app.py
pause
goto menu

:safe
streamlit run safe_motion_transitions\app.py
pause
goto menu