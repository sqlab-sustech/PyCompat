# PyCompat
## Description 
PyCompat is a semi-automatic tool to detect potential incompatible Python API usage.
It detects two kinds of usage issues: API renaming/relocating (ARR) and parameter renaming (PRN).
For detailed description, please refer to our SANER 2020 paper: [How Do Python Framework APIs Evolve? An Exploratory Study
](https://ieeexplore.ieee.org/abstract/document/9054800.).

## Usage Manual
```bash
cd ./src
python pycompat.py ${py_file_under_test} ${framework} ${api_evolution_dataset} ${output_path}  
``` 
 