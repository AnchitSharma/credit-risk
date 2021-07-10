import PyPDF2
import re
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from os.path import exists


adhaar_back = ["INFORMATION", "identity", "citizenship", "establish", "authenticate", "online", "throughout",
               "future", "address", "पता:", "addtess", "uidai", "govin", "gov.in", "w/o"]

verhoeff_table_d = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0))

verhoeff_table_p = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))

verhoeff_table_inv = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def check_PDF_valid(path):
    try:
        inputFile = open(path, 'rb')
        PyPDF2.PdfFileReader(inputFile)
        inputFile.close()
        return True
    except:
        return False


def checksum(number):
    """For a given number generates a Verhoeff digit and returns number + digit"""
    c = 0
    for i, item in enumerate(reversed(str(number))):
        c = verhoeff_table_d[c][verhoeff_table_p[i % 8][int(item)]]
    return c


def validateVerhoeff(number):
    """Validate Verhoeff checksummed number (checksum is last digit)"""
    if number.isdigit() and number[0] != '0':
        return checksum(number) == 0
    else:
        return False


def check_adhaar_re_verf(txt):
    ls = re.findall("\d{4}\s\d{4}\s\d{4}", txt)
    if ls and len(ls) > 0:
        for x in ls:
            x = re.sub(r"\s+", "", x, flags=re.I)
            if validateVerhoeff(x):
                return True
    else:
        return False


def rem_non_ascii(m):
    return re.sub(r'[^\x00-\x7F]+', ' ', m)


def check_adhaar_re(txt):
    txt = re.sub(r'[a-zA-Z]', '', txt).strip()
    txt = re.sub(r"\W", " ", txt, flags=re.I).strip()
    ls = re.findall("^\d{4}\s\d{4}\s\d{4}$", txt)
    if ls and len(ls) > 0:
        return True
    else:
        return False


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_image_slice(image_cropped, lst):
    """

    :param image_cropped:
    :param lst: x1 should not be less than 0, y1 should not be less than 0, x2 should not be grater than image size, y2
    :return:
    """
    h, w = image_cropped.shape[0:2]
    if lst[0] < 0:
        lst[0] = 0
    if lst[1] < 0:
        lst[1] = 0
    if lst[0] > w:
        return None
    if lst[2] > w:
        lst[2] = w
    if lst[3] > h:
        lst[3] = h

    return image_cropped[int(lst[1]):int(lst[3]), int(lst[0]):int(lst[2])]


def get_your_adhaar_pos4(file_path):
    with open("{}.hocr".format(file_path), 'r',encoding="utf8") as file:
        filedata = file.read()
        soup = BeautifulSoup(filedata, 'html.parser')
        words = soup.findAll('span')
        is_adhaar_detect = False
        blocks = []
        for s in words:
            sp = s.text.strip().replace("\n", " ")
            sp = re.sub(r"[,@|\'?\.$%_]", "", sp, flags=re.I).strip()
            if len(sp) == 0:
                continue
            if len(sp) != 0:
                if is_adhaar_detect:
                    if any(x in sp.lower() for x in ["enral", "enrol"]):
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]
                        zz[0] = zz[0] - 400
                        zz[1] = zz[1] + 200
                        zz[2] = zz[2] + 500
                        zz[3] = zz[3] + 1000
                        return zz

                if not is_adhaar_detect:
                    if "enrol" in sp.lower() or all(x in sp for x in ["Enr", "No"]):
                        is_adhaar_detect = True

    with open("{}.hocr".format(file_path), 'r', encoding="utf8") as file:
        filedata = file.read()
        soup = BeautifulSoup(filedata, 'html.parser')
        words = soup.findAll('span')
        is_adhaar_detect = False
        m = 0
        for s in words:
            sp = s.text.strip().replace("\n", " ")
            sp = re.sub(r"[,@|\'?\.$%_]", "", sp, flags=re.I).strip()
            if len(sp) == 0:
                continue
            if len(sp) != 0:
                if is_adhaar_detect:

                    if m == 1 and re.search(r"\b[0-9]{6}\b", sp):
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]
                        zz[0] = zz[0] - 450
                        zz[1] = zz[1] - 450
                        zz[2] = zz[2] + 50
                        zz[3] = zz[3]
                        return zz

                    if m == 2 and any(x in sp.lower() for x in ['your', 'adhaar', 'no']):
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]
                        return zz

                    if m == 3 and "enrol" in sp.lower():
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]
                        zz[0] = zz[0] - 270
                        zz[1] = zz[1] + 200 - 100
                        zz[2] = zz[2] + 200
                        zz[3] = zz[3] + 800
                        return zz
                    if m == 4 and re.search(r'[A-Z]{2}[\d]{9}[A-Z0-9]{2}', re.sub(r"\s", "", sp)):
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]

                        return zz

                    if m == 5 and re.search(r'[\d]{4}\/[\/|0-9]{5}[\/|0-9][\d]{5}', re.sub(r"\s", "", sp)):
                        zz = s['title'].split(';')[0]
                        zz = zz.split(' ')[1:]
                        zz = [int(x) for x in zz]
                        zz[0] = zz[0] - 700
                        zz[1] = zz[1] + 300
                        zz[2] = zz[2] - 200
                        zz[3] = zz[3] + 1000
                        return zz

                if not is_adhaar_detect:
                    if re.search(r'[A-Z]{2}[\d]{9}[A-Z0-9]{2}', re.sub(r"\s", "", sp)):
                        is_adhaar_detect = True
                        m = 4

                    if "enrol" in sp.lower():
                        is_adhaar_detect = True
                        m = 3

                    if re.search(r'[\d]{4}\/[\/|0-9]{5}[\/|0-9][\d]{5}', re.sub(r"\s", "", sp)):
                        is_adhaar_detect = True
                        m = 5

                    if all(x in sp.lower() for x in ['your', 'adhaar', 'no']):
                        is_adhaar_detect = True
                        m = 2

                    # '3 Chfiattisgarh - - 493441'
                    if re.search(
                            r"(Andhra Pradesh|Amaravati|Arunachal Pradesh|Assam|Bihar|Chhattisgarh|Goa|Gujarat|Haryana|Himachal Pradesh|Dharamshala|Jharkhand|Karnataka|Kerala|Madhya Pradesh|Maharashtra|Nagpur|Manipur|Meghalaya|Mizoram|Nagaland|Odisha|Punjab|Rajasthan|Sikkim|Tamil Nadu|Telangana|Tripura|Uttar Pradesh|Uttarakhand|Dehradun|West Bengal)",
                            sp) and re.search(
                        r"\b[0-9]{6}\b", sp):
                        is_adhaar_detect = True
                        m = 1



def get_text_hocr(PDF_file):
    wd_list = []
    if exists(f"{PDF_file}.hocr"):
        with open(f"{PDF_file}.hocr", 'r',encoding="utf8") as file:
            filedata = file.read()
            soup = BeautifulSoup(filedata, 'html.parser')
            words = soup.findAll('span')
            for s in words:
                sp = s.text.strip().replace("\n", " ")
                if not any(sp in y for y in wd_list):
                    wd_list.append(sp)
                else:
                    continue

    # #################print("getVoterHOCR: ", wd_list)
    return wd_list

def name_dob_gender(data):
    gender = ""
    gender_line = ""
    dob_line = ""
    dob = ""
    name = ""
    for i, line in enumerate(data):
        if "पुरुष" in line or (
                "male") in line.lower() or "female" in line.lower() or "महिला" in line.lower() or check_str_exist2(
            "female",
            line.lower()) or check_str_exist2(
            "male", line.lower()):
            gender_line = i
            gender = re.sub(r"[^A-Za-z]", " ", line)
            gender = gender.strip()
            gender = re.sub(' +', ' ', gender)
            if check_str_exist2("female", gender.lower()) and len(gender) > 4:
                gender = 'Female'
            elif "महिला" in line:
                gender = 'Female'
            elif "पुरुष" in line:
                gender = 'Male'
            else:
                gender = 'Male'

    for i, line in enumerate(data):
        if "dob" in line.lower() or re.findall(r'\d{2}\/\d{2}\/\d{4}', line):
            # #############print("entered second for")
            dob_line = i
            dob = re.sub(r"[^0-9\/]", " ", line)
            break
    if dob == "":
        for i, line in enumerate(data):
            if ("yob" in line.lower() and re.search(r"[\d]{4}", line)) or \
                    ("जन्म" in line or "तिथि" in line or "year" in line.lower() or "birth" in line.lower()):
                # #############print("entered third for")
                dob_line = i
                dob = re.sub(r"[^0-9\/]", " ", line)
                dob = dob
                break
    try:
        if dob == "" and gender_line != "":
            for i, line in enumerate(data):
                if i == gender_line - 1:
                    dob_line = i
                    dob = line
                    dob = re.sub(r"[^0-9\/]", " ", line)
    except:
        dob = ""
    if dob_line != "":
        data = data[:dob_line]
        for item in range(len(data) - 1, -1, -1):
            line = data[item]
            linex = line
            linex = list(linex.split(" "))
            # linex = re.sub("^[a-z].*","",line)
            output = [' '.join(w for w in a.split() if not (re.search(r"^[a-z]", w))) for a in linex]

            while "" in output:
                output.remove("")
            linex = ' '.join(output)
            linex = re.sub(r"[^A-Za-z:]", " ", linex)
            if "father" in linex.lower() or "husband" in linex.lower() or "baler" in linex.lower() or linex == "" or len(
                    linex.strip()) <= 5:
                continue
            else:
                if (":") in linex:
                    continue
                else:
                    check_name = linex
                    name = re.sub(r"[^A-Za-z]", " ", check_name)
                    name = name.strip()
                    break

    if dob != "":
        dob = re.sub(' +', ' ', dob)
        dob_copy = dob
        for i, word in enumerate(dob):
            dob_split = dob.split(" ")
            for i, date in enumerate(dob_split):
                if re.findall(r"(\d\d(\/)\d\d(\/)\d\d\d\d)", date) or re.findall(r"(\d\d(\/)\d\d(\/)\d\d)", date):
                    dob = date
                    break
                else:
                    pass
    '''if dob == "" :        
       for i,word in enumerate(dob_copy):
            dob_split = dob_copy.split(" ")
            for i,date in enumerate(dob_split) :
                   if re.findall("^[0-9].*",date) :
                        dob = date
                        break'''

    return name, gender, dob


def get_adhaar_list(wd_lst):
    for l in wd_lst:
        if all(x in l for x in ["1800", "1947"]) or all(x in l for x in ["1800", "300"]):
            continue
        l = rem_non_ascii(l)
        l = re.findall(r"\d{4}\s?\d{4}\s?\d{4}", l)
        if not l is None and len(l) > 0:
            for i in l:
                i = re.sub(r"\W", "", i, flags=re.I)
                if len(i) == 12 and validateVerhoeff(i):
                    return i


def check_str_exist2(main, fstr):
    fstr = fstr.replace('é', 'e')
    fstr = re.sub('[^a-zA-Z0-9 \n\.]', '', fstr).lower()

    lstr = fstr.split(' ')
    if main in fstr:
        return True

    for i in range(len(fstr)):
        if similar(main, fstr[i:i + len(main)]) >= 0.78:
            return True

    else:
        return False


def check_adhaar_front(wd_list):
    # get result using equals or similar set
    wdp = ["year of birth", "birth", "male", "enrolment", "महिला", "जन्म"]
    for i, x in enumerate(wd_list):
        if any(p in x.lower() for p in ["enrollment no", "enrolment no", "enrollment"]) or \
                all(p in x for p in ["Enrol", "No"]) or all(p in x for p in ["Enr", "ment"]):
            return True
        if re.search(r"[YOB|yob]{3}[\s][\d]{4}", x):
            return True
        if re.search(r'\d{2}\/\d{2}\/\d{4}', x):
            return True
        if any(y in x.lower() for y in wdp):
            return True
        if any(similar(y, x.lower()) > 0.8 for y in wdp):
            return True
        # "your" in x.lower() and i + 1<len(x) and "aadhaar" in x[i + 1]:
        if all(p in x.lower() for p in ["your", "aadhaar"]):
            return True
    return False


# '; (al eetegen ey: 1947 _ help@uidai.gov.in www.uidai.gov.in P.O. Box No.1947,'
def check_adhaar_back(wd_list):  #
    vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["non", "gov", "serv"]) or
          all(x in wd.lower() for x in ["serv", "future"]) or
          any(x in wd.lower() for x in adhaar_back)]

    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["help", "uidai", "gov"])]

    if len(vb) == 0:
        vb = [wd for wd in wd_list if re.search(r"(help)\s?[@][a-z.]{6}(gov)", wd)]

    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["p.o.", "box", "1947"])]
    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["1800", "300", "1947"])]

    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["1800", "300"]) or
              all(x in wd.lower() for x in ["1800", "47"])]

    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["bengaluru", "560", "001"])]
    if len(vb) == 0:
        vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["aadhaar", "aam", "aadmi", "adhikar"])]

    if len(vb) > 0:
        return True
    else:
        return False
