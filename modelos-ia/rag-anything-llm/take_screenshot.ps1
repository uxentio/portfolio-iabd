param([string]$OutFile = "D:\Tarea 5 RAG\Capturas\test_capture.png")

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    Write-Host "Assemblies loaded"

    $src = @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, ref tagRECT lpRect);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    public struct tagRECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
    Add-Type -TypeDefinition $src -ErrorAction SilentlyContinue
    Write-Host "WinAPI loaded"

    $p = Get-Process -Name "MauiRAG" | Select-Object -First 1
    $h = $p.MainWindowHandle
    Write-Host "Handle: $h"

    [WinAPI]::ShowWindow($h, 9) | Out-Null
    Start-Sleep -Seconds 1
    [WinAPI]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Seconds 1

    $r = New-Object WinAPI+tagRECT
    [WinAPI]::GetWindowRect($h, [ref]$r) | Out-Null
    $w = $r.Right - $r.Left
    $ht = $r.Bottom - $r.Top
    Write-Host "Size: ${w}x${ht} pos: $($r.Left),$($r.Top)"

    $bmp = New-Object System.Drawing.Bitmap $w, $ht
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)
    $gfx.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $ht))
    $gfx.Dispose()
    $bmp.Save($OutFile)
    $bmp.Dispose()
    Write-Host "Saved: $OutFile"
} catch {
    Write-Host "ERROR: $_"
}
