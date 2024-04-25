# Match Between Runs (MBR) Filter
<img src="./resource/icon.png" width='50%'>

- This filter is used to filter out the peptides that are not detected by MS/MS in meta conditions.
- It allows the user to provide a table of Peptide identifications (separated by tab), as well as a meta table (Smaples as first col). By user setting, only Peptide Intensity containing at least a specified number of MS/MS results in a particular group is retained.

## Requires: 

- pandas

- pyqt5
- pyqtdarktheme (optional)