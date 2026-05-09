param([int]$X, [int]$Y, [string]$Text, [string]$OutFile)

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $src = @"
using System;
using System.Runtime.InteropServices;
public class WinPaste {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, ref tagRECT lpRect);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern void SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
    public struct tagRECT { public int Left; public int Top; public int Right; public int Bottom; }
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(100);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
}
"@
    Add-Type -TypeDefinition $src -ErrorAction SilentlyContinue

    $p = Get-Process -Name "MauiRAG" | Select-Object -First 1
    $h = $p.MainWindowHandle

    [WinPaste]::ShowWindow($h, 9) | Out-Null
    Start-Sleep -Milliseconds 300
    [WinPaste]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Milliseconds 500

    $r = New-Object WinPaste+tagRECT
    [WinPaste]::GetWindowRect($h, [ref]$r) | Out-Null

    $absX = $r.Left + $X
    $absY = $r.Top + $Y
    Write-Host "Clicking at abs: ($absX, $absY)"

    # Copy text to clipboard
    [System.Windows.Forms.Clipboard]::SetText($Text)
    Start-Sleep -Milliseconds 200

    # Click on the field
    [WinPaste]::Click($absX, $absY)
    Start-Sleep -Milliseconds 500

    # Select all and paste
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("^v")
    Start-Sleep -Seconds 2

    # Take screenshot
    [WinPaste]::GetWindowRect($h, [ref]$r) | Out-Null
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
