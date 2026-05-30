$csm = New-Object -ComObject "Microsoft.Windows.Search.CrawlScopeManager"
$csm.AddUserScopeRule("file:///F:\", $false, $false, $null)
$csm.AddUserScopeRule("file:///G:\", $false, $false, $null)
$csm.SaveAll()
Write-Output "Gata! F: si G: au fost excluse din Indexare!"
