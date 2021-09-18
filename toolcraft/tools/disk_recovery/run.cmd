rem https://github.com/nneonneo/ntfsrecover

python ntfs_recovery.py \\.\Harddisk1Partition1 --save-mft mft

python ntfs_recovery.py \\.\Harddisk1Partition1 --mft mft --pattern "*/GaMeS/*" --outdir recovered
