mkdir data/data_${2}
wget ${1} -O data/data_${2}/paper.pdf -U definitely-not-wget
time convert      \
    -density 150   \
    data/data_${2}/paper.pdf \
    -quality 100   \
    -sharpen 0x1.0 \
    -background white \
    -alpha remove  \
    data/data_${2}/out.jpg
touch data/data_${2}/fin
