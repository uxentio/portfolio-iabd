param([string]$OutFile, [int]$Width = 1200, [int]$Height = 900)

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $src = @"
using System;
using System.Runtime.InteropServices;
public class WinResize {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, ref tagRECT lpRect);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern void SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    public struct tagRECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
    Add-Type -TypeDefinition $src -ErrorAction SilentlyContinue

    $p = Get-Process -Name "MauiRAG" | Select-Object -First 1
    $h = $p.MainWindowHandle

    # Restore, resize, bring to front
    [WinResize]::ShowWindow($h, 9) | Out-Null
    Start-Sleep -Milliseconds 300
    [WinResize]::MoveWindow($h, 50, 30, $Width, $Height, $true) | Out-Null
    Start-Sleep -Milliseconds 500
    [WinResize]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Milliseconds 500

    # Scroll to top first
    $cx = [int](50 + $Width / 2)
    $cy = [int](30 + $Height / 2)
    [WinResize]::SetCursorPos($cx, $cy)
    Start-Sleep -Milliseconds 200
    for ($i = 0; $i -lt 10; $i++) {
        [WinResize]::mouse_event(0x0800, 0, 0, 120, 0)
        Start-Sleep -Milliseconds 50
    }
    Start-Sleep -Milliseconds 500

    # Take screenshot
    $r = New-Object WinResize+tagRECT
    [WinResize]::GetWindowRect($h, [ref]$r) | Out-Null
    $w = $r.Right - $r.Left
    $ht = $r.Bottom - $r.Top

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
