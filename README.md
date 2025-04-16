## data
Dummy data for tests

## simple-encoders
### 00_archiver
```bash
# run
python archiver.py "../../data/source/" "../../data/source-archive.zip"
```

### 01_encryptor
###### Archiving
```bash
python encryptor.py -a "../../data/source" "../../data/source-archive.zip"
```

###### Unarchiving
```bash
python encryptor.py -u "../../data/source-archive.zip" "../../data/source"
```

###### Encrypting
```bash
python encryptor.py -e "../../data/source" "../../data/source-archive.zip.sec"
```

###### Decrypting
```bash
python encryptor.py -d "../../data/source-archive.zip.sec" "../../data/source"
```

###### Comparing
```bash
python encryptor.py -c "../../data/source" "../../data/source @TIMESTAMP"
```

### 02_steganography
##### Useful links
- https://www.reddit.com/r/Python/comments/gdjnfn/my_take_at_steganography
- https://exo.substack.com/p/the-exo-guide-to-data-cloaking
- https://en.wikipedia.org/wiki/Steganography
- https://ru.wikipedia.org/wiki/Стеганография
- https://habr.com/ru/companies/vdsina/articles/518292
- https://habr.com/ru/articles/803839
- https://habr.com/ru/articles/848048
- https://habr.com/ru/articles/422593
- https://habr.com/ru/articles/651905
- https://habr.com/ru/articles/253045
- https://habr.com/ru/articles/862598
- https://habr.com/ru/articles/128327
- https://habr.com/ru/articles/339432

##### Commands
###### Encrypting file
```bash
python stegano.py -e ../../data/first_image.png --img=../../data/second_image.png --res=../../data/third_image.png
```

###### Decrypting file
```bash
python stegano.py -d ../../data/third_image.png --res=../../data/fourth_image.png
```

###### Encrypting message
```bash
python stegano.py -e test_message+123 --img=../../data/second_image.png --res=../../data/fifth_image.png
```

###### Decrypting message
```bash
python stegano.py -d ../../data/fifth_image.png
```

### 03_sss
##### Useful links
- https://github.com/jesseduffield/horcrux
- https://en.wikipedia.org/wiki/Shamir's_secret_sharing
- https://habr.com/ru/companies/globalsign/articles/776520

### 10_all-in-one
