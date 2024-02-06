# uic-course-description-parser
Simple Python script converting UIC official course description PDF to semi-structure file (TSV)

## Setup Environment
It is recommended to create a new virtual enviroment for this project, you can use `venv` or `conda`.

After setup the environment, you need to install required packages specified in `requirements.txt`, this can be done with command `pip install -r requirements.txt`

After pip finished the installation, you have a enviroment ready to process the PDF.

## Prepare the PDF file
Since we do not own the copyright of the file, we will not prepare a copy in this repositry. But you should able to obtain the file via [AR's Website](https://ar.uic.edu.cn/current_students/student_handbook/course_Deescription.htm).

## Use the Script
This script is not well polished, so parameters are all hard-coded. So before you actually press the button to start the parsing magic, you need to change these two variable:

- `PDF_FILENAME` at [Line 7 of the extract.py file](https://github.com/UICHCC/uic-course-description-parser/blob/d6471f33c75f98de79a23d10ce9020e51f38ad12/extract.py#L7C1-L7C13): This should point to the path where the PDF located.
- `FILENAME_PREFIX` at [Line 6 of the extract.py file](https://github.com/UICHCC/uic-course-description-parser/blob/d6471f33c75f98de79a23d10ce9020e51f38ad12/extract.py#L6C1-L6C16): This is the prefix for all output files.
  - The script should output three files, including
  - `<FILENAME_PREFIX>-raw_lines.txt`: The raw lines extracted from PDF file, use for code debug.
  - `<FILENAME_PREFIX>-records.tsv`: TSV file contains columns `course_code`, `course_name`, `course_units`, `course_prerequisites`
  - `<FILENAME_PREFIX>-description.tsv`: TSV file contains columns `course_code`, `course_description`
 
After you modified there two variable, you should able to start parsing with command `python extract.py`
 
## Licences 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
