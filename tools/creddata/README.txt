How the 34 CredData samples were produced (for reproducibility; not needed to run the project).
Needs Linux (CredData file names break on Windows), git and network access to GitHub.

1. git clone https://github.com/Samsung/CredData creddata
2. Write needed_repos.json: CredData repos with labelled Python lines, mapped to (pinned commit id, URL)
   from creddata/snapshot.json (repo name = crc32 of the snapshot key, as in CredData's download_data.py).
3. python fetch_repos.py        -> fetches each repository at CredData's pinned commit (about 5 GB)
4. python extract_creddata.py   -> writes the samples and cd_rows.json (fixed random seed 2026)
Selection and labelling rules: dataset/LABELLING.md, section 5.
