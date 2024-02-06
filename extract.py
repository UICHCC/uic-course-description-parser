import re
import string
import fitz
import csv

FILENAME_PREFIX = "20240118"
PDF_FILENAME = "cd-20240118.pdf"

printable = set(string.printable)

printable.remove('\t')
printable.remove('\n')
printable.remove('\x0b')
printable.remove('\x0c')
printable.remove('\r')

print(f"Loading PDF {PDF_FILENAME}")

with fitz.open(PDF_FILENAME) as doc:  # open document
    text = chr(12).join([page.get_text() for page in doc])
    text = text.split('\n')
    text = ["".join(filter(lambda x: x in printable, l)) for l in text][6:]

RAW_FILENAME = f"{FILENAME_PREFIX}-raw_lines.txt"

print(f"There are {len(text)} lines of text in the PDF, saving to {RAW_FILENAME}")

with open(RAW_FILENAME, 'w') as fp:
    for item in text:
        # write each item on a new line
        fp.write("%s\n" % item)
    print("Done")

pattern = r"([A-Z]{2,4}\d{4})"  # Simple Course Code Pattern
cc_dict = dict()
for i in text:
    # print(i)
    if re.match(pattern, i):
        result = re.search(pattern, i)
        try:
            cc_dict[result.group(1)] += 1
        except KeyError:
            cc_dict[result.group(1)] = 1

print(f"Found {len(cc_dict.keys())} matched course code")

pattern = "^([A-Z]{2,4}\d{4}) ([0-9A-Z\s\-\(\)&\+\?,:]*)$" # Course Code with Course Name Pattern

cn_list = list()  # Course Name List
cd_list = list()  # Course Description List

new_flag = 0
temp_c_list = list()
for k, i in enumerate(text):
    if re.match(pattern, i):  # A new course pattern like string
        if new_flag == 1:  # *Course Description* flag not meet
            temp_c_list.append(i)  # Just another line
        else:  # *Course Description* flag meet
            if cn_list:
                cd_list.append(temp_c_list)  # Save previous raw data
                temp_c_list = list()
            new_flag = 1
            cn_list.append(i)  # Save new course name
    elif "Course Description:" in i or "Course  Description" in i or "Description:" in i or "Course Description" in i:
        new_flag = 0
        temp_c_list.append(i)
    else:
        temp_c_list.append(i)
cd_list.append(temp_c_list)

print(f"Found {len(cn_list)} Course Name, {len(cd_list)} Course Description (Two number equal means good)")

def hanging_course_name(course_raw):
    buffer = list()
    for i in course_raw:
        if "(" in i:
            break
        if i:
            buffer.append(i)
    return buffer

def get_course_code(course_name):
    pattern = r"([A-Z]{2,4}\d{4})"
    result = re.search(pattern, course_name)
    return result.group(1)

def get_course_name(course_name, course_raw):
    raw_course_name = course_name.replace(get_course_code(course_name), '')
    hanging = hanging_course_name(course_raw)
    lower_course_name = ' '.join([raw_course_name.strip()] + hanging).strip()
    return "".join(lower_course_name)
    

def get_course_unit(course_raw):
    for i in course_raw:
        if re.match(r"\(\d{1}\s*(unit|UNIT).*\)", i.strip()):  # A new course pattern like string
        # if "(" in i and ("unit" in i or "UNIT" in i):
            return i.strip()[1:2]
        
def get_course_desc(course_raw):
    buffer = list()
    start = 0
    for i in course_raw:
        if "Course Description:" in i or "Course  Description" in i or "Description:" in i or "Course Description" in i:
            start = 1
        if start:
            buffer.append(i)
    return buffer
        
def get_course_pre(course_raw):
    buffer = list()
    start = 0
    for i in course_raw:
        if "Pre-requisite(s):" in i:
            start = 1
        if "Course Description:" in i or "Course  Description" in i or "Description:" in i or "Course Description" in i:
            start = 0
            break
        if start:
            if "Pre-requisite(s):" in i:
                buffer.append(i.replace("Pre-requisite(s):", ""))
            else:
                buffer.append(i)
    return "".join(buffer)

course_dict = dict()
for n, r in zip(cn_list, cd_list):
    cc = get_course_code(n)
    payload = {
        'course_code': cc,
        'course_name': get_course_name(n, r),
        'unit': get_course_unit(r),
        'prerequisite': get_course_pre(r),
        'description': get_course_desc(r)
    }
    course_dict[cc] = payload

print("Saving Course Records")

with open(f'{FILENAME_PREFIX}-records.tsv', 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    writer.writerow(["course_code","course_name","prerequisite","unit"])
    for k, v in course_dict.items():
        temp_prereq = v['prerequisite'].strip()
        if "None" in temp_prereq or "None Course" in temp_prereq:
            temp_prereq = "N/A"
        writer.writerow([v['course_code'], v['course_name'], temp_prereq, v['unit']])

code_desc_dict = dict()
for k, v in course_dict.items():
    code_desc_dict[k] = v['description']

for k, v in code_desc_dict.items():
    tv = [line for line in v if not re.match(r"\d+ / \d+", line.strip())]  # Clean up page number pattern 
    temp = ''.join(''.join(tv).split(":")[1:]).strip()
    code_desc_dict[k] = temp

print("Saving Course Descriptions")

with open(f'{FILENAME_PREFIX}-description.tsv', 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    writer.writerow(["course_code","course_description"])
    for k, v in code_desc_dict.items():
        writer.writerow([k, v])

print("Done, Exiting")
