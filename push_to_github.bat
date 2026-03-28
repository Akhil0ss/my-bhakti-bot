@echo off
echo ========================================
echo   AURA ENGINE - GITHUB PUSH TOOL
echo ========================================
echo.
git add .
git commit -m "Repurpose Engine - TikTok + Insta + No Watermark"
echo.
echo Pushing to: https://github.com/Akhil0ss/my-bhakti-bot.git
echo (Ek Login Popup aa sakta hai, please use approve karein)
echo.
git push -u origin main
echo.
echo ========================================
if %errorlevel% neq 0 (
    echo [ERROR] Push fail ho gaya. Internet check karein ya VPN lagayein.
) else (
    echo [SUCCESS] Code GitHub par pahuch gaya!
)
echo ========================================
pause
