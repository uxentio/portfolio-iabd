param(
    [string]$OutputPath = "D:\Tarea 5 RAG\Capturas\screenshot.png"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }
}
"@

$proc = Get-Process -Name "MauiRAG" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($proc -eq $null) {
    Write-Error "MauiRAG not running"
    exit 1
}

$hwnd = $proc.MainWindowHandle
Write-Host "Window handle: $hwnd"

# Restore and bring to front
[Win32]::ShowWindow($hwnd, 9) | Out-Null
Start-Sleep -Milliseconds 500
[Win32]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 500

# Get window rect
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null

$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
Write-Host "Window size: ${width}x${height} at ($($rect.Left),$($rect.Top))"

if ($width -le 0 -or $height -le 0) {
    Write-Error "Window has invalid size"
    exit 1
}

# Capture
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($width, $height)))
$graphics.Dispose()
$bmp.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

Write-Host "Screenshot saved to: $OutputPath"
