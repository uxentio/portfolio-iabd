Get-Process | Where-Object { $_.ProcessName -like '*Maui*' } | Select-Object ProcessName, MainWindowTitle, MainWindowHandle | Format-Table -AutoSize
