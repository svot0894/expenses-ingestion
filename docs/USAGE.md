# if on windows, i recommend scoop as a package manager

Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')

# install Supabase CLI

scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

https://supabase.com/docs/guides/deployment/managing-environments
