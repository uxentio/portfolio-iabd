param([string]$OutFile, [int]$ScrollAmount = 5)

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $src = @"
using System;
using System.Runtime.InteropServices;
public class WinScroll2 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, ref tagRECT lpRect);
    [DllImport("user32.dll")] public static extern void SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    public struct tagRECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
    Add-Type -TypeDefinition $src -ErrorAction SilentlyContinue

    $p = Get-Process -Name "MauiRAG" | Select-Object -First 1
    $h = $p.MainWindowHandle

    [WinScroll2]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Milliseconds 500

    $r = New-Object WinScroll2+tagRECT
    [WinScroll2]::GetWindowRect($h, [ref]$r) | Out-Null

    $cx = [int](($r.Left + $r.Right) / 2)
    $cy = [int](($r.Top + $r.Bottom) / 2)
    [WinScroll2]::SetCursorPos($cx, $cy)
    Start-Sleep -Milliseconds 200

    # Scroll down: MOUSEEVENTF_WHEEL=0x0800, data=-120 per click
    for ($i = 0; $i -lt $ScrollAmount; $i++) {
        [WinScroll2]::mouse_event(0x0800, 0, 0, -120, 0)
        Start-Sleep -Milliseconds 150
    }
    Start-Sleep -Milliseconds 800

    [WinScroll2]::GetWindowRect($h, [ref]$r) | Out-Null
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
