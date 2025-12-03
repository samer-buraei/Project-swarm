# Dataset Download Instructions

## FLAME Dataset (Priority: Critical)

### Option 1: IEEE DataPort (Official)
1. Create free account at https://ieee-dataport.org
2. Go to: https://ieee-dataport.org/open-access/flame-dataset
3. Download all files (~2.3GB)
4. Extract to: `datasets/FLAME/`

### Option 2: Kaggle (Mirror)
```bash
pip install kaggle
kaggle datasets download -d phylake1337/fire-dataset
unzip fire-dataset.zip -d datasets/FLAME/
```

### Option 3: Direct Links (if available)
[List any direct download links found]

## Folder Structure After Download
```
datasets/
├── FLAME/
│   ├── RGB/
│   ├── Thermal/
│   └── Labels/
├── DFireDataset/  (already have)
└── Combined/      (will create)
```
