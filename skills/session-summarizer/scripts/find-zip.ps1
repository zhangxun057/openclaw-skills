Get-ChildItem 'C:\Users\44452\.openclaw' -Filter '*.zip' -Recurse -ErrorAction SilentlyContinue | Select-Object FullName, Length
