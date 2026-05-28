@echo off
echo ========================================
echo 视频压缩工具安装脚本
echo ========================================
echo.

REM 检查Python
echo 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请从 https://www.python.org/downloads/ 下载安装Python
    echo 安装时请勾选"Add Python to PATH"
    pause
    exit /b 1
)
echo ✅ Python已安装

REM 检查FFmpeg
echo.
echo 检查FFmpeg安装...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠ FFmpeg未安装或未添加到PATH
    echo.
    echo 请按以下步骤安装FFmpeg:
    echo 1. 访问 https://ffmpeg.org/download.html
    echo 2. 下载Windows版本
    echo 3. 解压到 C:\ffmpeg
    echo 4. 将 C:\ffmpeg\bin 添加到系统PATH
    echo.
    echo 是否现在打开浏览器下载FFmpeg? (Y/N)
    set /p download=
    if /i "%download%"=="Y" (
        start https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    )
    echo.
    echo 安装FFmpeg后，请重新运行此脚本
    pause
    exit /b 1
)
echo ✅ FFmpeg已安装

REM 检查依赖
echo.
echo 检查Python依赖...
pip list | findstr "numpy" >nul 2>&1
if errorlevel 1 (
    echo 安装numpy...
    pip install numpy
) else (
    echo ✅ numpy已安装
)

REM 创建快捷方式
echo.
echo 创建快捷方式...
set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\视频压缩工具.lnk

REM 创建批处理文件
echo @echo off > "%SCRIPT_DIR%run_compressor.bat"
echo echo 视频压缩工具 >> "%SCRIPT_DIR%run_compressor.bat"
echo echo ======================================== >> "%SCRIPT_DIR%run_compressor.bat"
echo python "%~dp0video_compressor.py" %%* >> "%SCRIPT_DIR%run_compressor.bat"
echo pause >> "%SCRIPT_DIR%run_compressor.bat"

REM 创建VBS脚本创建快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%TEMP%\create_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\create_shortcut.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%run_compressor.bat" >> "%TEMP%\create_shortcut.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Description = "智能视频压缩工具" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Save >> "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs" >nul 2>&1
del "%TEMP%\create_shortcut.vbs"

if exist "%SHORTCUT_PATH%" (
    echo ✅ 桌面快捷方式已创建
) else (
    echo ⚠ 无法创建桌面快捷方式
)

REM 测试脚本
echo.
echo 测试脚本功能...
python "%SCRIPT_DIR%test_video_compressor.py"
if errorlevel 1 (
    echo.
    echo ⚠ 测试失败，但工具仍可尝试使用
    echo 请查看上面的错误信息
) else (
    echo.
    echo ✅ 所有测试通过！
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 双击桌面上的"视频压缩工具"快捷方式
echo 2. 或运行命令: python video_compressor.py [参数]
echo.
echo 详细说明请查看 README.md 文件
echo.
pause