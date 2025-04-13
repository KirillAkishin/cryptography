## data
Dummy data for tests

## simple-encoders
#### 00_archiver
```bash
# run
python archiver.py "../../data/source/" "../../data/source-archive.zip"
```

#### 01_encryptor
##### Archiving
```bash
python encryptor.py -a "../../data/source" "../../data/source-archive.zip"
```

##### Unarchiving
```bash
python encryptor.py -u "../../data/source-archive.zip" "../../data/source"
```

##### Encrypting
```bash
python encryptor.py -e "../../data/source" "../../data/source-archive.zip.sec"
```

##### Decrypting
```bash
python encryptor.py -d "../../data/source-archive.zip.sec" "../../data/source"
```

##### Comparing
```bash
python encryptor.py -c "../../data/source" "../../data/source @TIMESTAMP"
```

#### 02_steganography
#### 03_sss
- https://github.com/jesseduffield/horcrux
- https://en.wikipedia.org/wiki/Shamir's_secret_sharing
- https://habr.com/ru/companies/globalsign/articles/776520

#### 10_all-in-one
