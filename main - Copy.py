import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes
import pyzbar
import zipfile
import model
import Utility as utils
import pickle
import xml.dom.minidom

tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tess_path
from pytesseract import pytesseract

document_list = []

doc_path = "D:/qfc/kyc_data_extract_mask/docs"
pro_base_path = "D:/pythonProject"

adhaar_word = ["unique", "identification", 'dentfication', "unique identification authority of india",
               "cation authority", "authority of india",
               "aadhaar", "uidai", "to establish identity", "authenticate", "enrollment no",
               "enrollment", "year of birth", "adhikar", " आधार आदमी का", "आधार", "आध्यार", "आदमी", "आंदंमी", "आंधार",
               "प्रधिकरण", "प्राधिकरण", "विशिष्ट", "मेरी पहचान", "मेरा आधा", "aadhaar-aam", "year of bi"]


def aadhar(image_cropped):  # if input here only doc name
    blur = cv2.GaussianBlur(image_cropped, (5, 5), 0)
    ret, inverted = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
    img_1 = Image.fromarray(inverted)
    barcodes = ""
    try:
        barcodes = pyzbar.decode(img_1)
    except:
        pass

    if len(barcodes) > 0:
        # get barcode mask here function
        # mask_from_qrcode(img, PDF_file, barcodes)

        lst = barcodes[0].data.decode("utf-8")
        try:
            doc = xml.dom.minidom.parseString(lst)
            kl = doc.firstChild
            # co
            add = kl.getAttribute("co") + " " + kl.getAttribute("house") + " " + kl.getAttribute(
                "street") + " " + kl.getAttribute("lm") + " " + \
                  kl.getAttribute("loc") + " " + kl.getAttribute("vtc") + \
                  " " + kl.getAttribute("po") + " " + kl.getAttribute("dist") + \
                  " " + kl.getAttribute("subdist") + " " + kl.getAttribute("state") + " pincode: " + kl.getAttribute(
                "pc")
            # print(kl.getAttribute("uid"))
            # print(kl.getAttribute("yob"))
            # print(add)
            # print(kl.getAttribute("name"))
            print("Male" if kl.getAttribute("gender") == 'M' else "Female")
            # create_update_adhar(PDF_file, adhaar_no=kl.getAttribute("uid"))
            # create_update_adhar(PDF_file, birth_year=kl.getAttribute("yob"))
            # create_update_adhar(PDF_file, address=add)
            # create_update_adhar(PDF_file, name=kl.getAttribute("name"))
            # create_update_adhar(PDF_file, Sex="Male" if kl.getAttribute("gender") == 'M' else "Female")
            m = model.KYCDocument()
            m.adhaar_num = kl.getAttribute("uid")
            m.is_adhaar_name = kl.getAttribute("name")
            m.is_adhaar_dob = kl.getAttribute("yob")
            m.is_adhaar_address = add
            m.is_adhaar_gender = "Male" if kl.getAttribute("gender") == 'M' else "Female"
            return m
        except:
            pass

    return barcodes


def get_file_tree1(path):
    for f in os.scandir(path):
        if not f.is_dir(follow_symlinks=False):
            m1 = model.Document()
            m1.zip_path = f.path
            m1.zip_file_name = f.name
            document_list.append(m1)


# read the zip file and save the files in it to inter_doc_loc folder
def read_save_zip(e):
    path_to_zip_file = e.zip_path
    pro_path = pro_base_path + "/inter_doc_loc"
    folder_path = path_to_zip_file.split("\\")[-1]
    directory_to_extract_to = pro_path + "\\" + folder_path
    e.inter_path = directory_to_extract_to
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
        # zip_ref.filelist[0].filename
        t = []
        for f in zip_ref.filelist:
            t.append(f.filename)
        e.lst_docs_in_zip = t

    return e


"""
This variable is use to distinguish between different formats of aadhaar cards 
obj1.is_front_back and not obj1.is_big_small   :> 1
obj1.is_front_back and obj1.is_big_small       :> 2
obj1.is_big_small or (not obj2 is None and obj2.is_big_small and not obj2.is_back)   :> 3
else :> 4
"""

"""
        if d_type[0] == 2 or d_type[0] == 3:
            if d_type[1] == 1:
                document.is_front = True
            elif d_type[1] == 2:
                document.is_back = True
            elif d_type[1] == 3:
                document.is_front_back = True
            if len(d_type) > 2:
                if d_type[2] == 4:
                    document.is_big_small = True
                elif d_type[2] == 0:
                    document.is_big_small = False
            return document

"""


def classify_adhaar(wd_list, doc_path):
    also_check_app_word = ["financial", "koota", "loan application form"]
    vb = [wd for wd in wd_list if all(x in wd.lower() for x in ["cation", "auth", "ind"]) or
          all(x in wd.lower() for x in ["जन्म", "वर्ष"]) or
          (all(x in wd.lower() for x in ["प्रा", "करण"])) or
          all(x in wd.lower() for x in ["nique", "ident"]) or
          all(x in wd.lower() for x in ["he", "uid", "gov"]) or
          (all(x in wd.lower() for x in ["1800", "300"])) or
          all(x in wd.lower() for x in ["nique", "fication"]) or
          all(x in wd.lower() for x in ["nique", "ath", "india"]) or
          all(x in wd.lower() for x in ["nique", "dent", "thor", "india"]) or
          (all(x in wd.lower() for x in ["00", "1947"])) or
          (utils.check_adhaar_re_verf(utils.rem_non_ascii(wd))) or
          (utils.check_adhaar_re(utils.rem_non_ascii(wd))) or
          (all(x in wd.lower() for x in ["1800", "47"])) or
          all(x in wd.lower() for x in ["aut", "india"]) or
          all(x in wd.lower() for x in ["year", "birth", "of"]) or
          all(x in wd for x in ["आम", "अधिकार"]) or
          utils.check_str_exist2('enrolment', wd.lower()) or
          (any(x in wd.lower() or re.search(r"(help)\s?[@][a-z.]{6}(gov)", wd) or re.search(r"(YOB|yob){3}[\s][\d]{4}",
                                                                                            utils.rem_non_ascii(
                                                                                                wd)) or re.search(
              r"(Bengaluru)[-|\s][\d]{3}[:|\s][\d]{2}", wd) for x in adhaar_word))]

    vb_1 = [wd for wd in wd_list if any(x in wd.lower() for x in ['debit', 'arrear'])]
    if len(vb_1) > 0:
        vb = []
    vb_1 = [wd for wd in wd_list if all(x in wd.lower() for x in ['two wheeler', 'loan', 'applicati'])]
    if len(vb_1) > 0:
        vb = []

    # group personal accident policy: member enrolment form
    # PERSONAL ACCIDENT POLICY: MEMBER ENROLMENT. FORM
    # GROUP PERSONAL ACCIDENT POLICY: MEMBER ENROLMENT FORM
    vb_1 = [wd for wd in wd_list if all(x in wd.lower() for x in ['policy', 'personal', 'group', 'acc'])]
    if len(vb_1) > 0:
        vb = []

    vb_1 = [wd for wd in wd_list if all(x in wd.lower() for x in ['member', 'enrolment', 'form'])]
    if len(vb_1) > 0:
        vb = []

    # tax invoice (vehicle)
    vb_1 = [wd for wd in wd_list if all(x in wd.lower() for x in ['tax', 'invoice', 'vehicle'])]
    if len(vb_1) > 0:
        vb = []

    # check the document name
    # 91316466_1_UID_00001831939_Schedule_Form_UID_0000183193921022011491616.pdf
    # SCHEDULE FORMING PART OF AUTO LOAN AGREEMENT

    if '_Schedule_Form_' in doc_path:
        vb = []

    vb_2 = [wd for wd in wd_list if any(x in wd.lower() for x in also_check_app_word)]
    # Two Wheeler - Loan Applicati
    if len(vb_2) > 0:
        vb = []

    if len(vb) > 0:
        t = [wd for wd in vb if any(utils.check_str_exist2(x, wd.lower()) for x in ["computerised", "pass book"])]
        if len(t) > 0:
            vb = []


        if vb and len(vb) > 0:
            return True

    return False


def class_loan_app(wd_list):
    also_check_app_word = ["loan application form"]
    vb_2 = [wd for wd in wd_list if any(x in wd.lower() for x in also_check_app_word)]
    if len(vb_2) > 0:
        return True

    vb_1 = [wd for wd in wd_list if all(x in wd.lower() for x in ['two wheeler', 'loan', 'applicati'])]
    if len(vb_1) > 0:
        return True

    return False


def text_classify(wd_list, doc_path):
    op = classify_adhaar(wd_list, doc_path)

    if op:
        big_small = [wd for wd in wd_list if all(x in wd.lower() for x in ["govern", "serv", "future"]) or
                     all(x in wd.lower() for x in ["help", "avail", "govern"]) or
                     all(x in wd for x in ["through", "country"]) or all(
            x in wd for x in ["authen", "online", "ident"]) or
                     all(x in wd for x in ["To", "estab", "ident"]) or all(x in wd for x in ["Enr", "No"]) or
                     re.search(r'[A-Z]{2}[\d]{9}[A-Z0-9]{2}', wd) or utils.check_str_exist2('enrolment',
                                                                                            wd.lower()) or any(
            x in wd.lower() for x in
            ["enrollment no", "enrolment no", "enrollment", "your", "aadhar", "aadhav",
             "आपका आधार क्रमांक", "क्रमांक", "adhaar no",
             'enroliment no.', "your aad", "enrolmen", "क्रम/ Enrol",
             "electronically generated", "electronically",
             "इलेक्ट्रॉनिक प्रक्रिया"])]

        if len(big_small) > 0:
            t = (4,)
        else:
            t = (0,)

        fx = [wd for wd in wd_list if
              re.search(r'[A-Z]{2}[\d]{9}[A-Z0-9]{2}', re.sub(r"\s", "", wd)) or re.search(
                  r'(Ref:?)[\d]{3}\/[\d]{2}[A-Z]?\/[\d]{6}\/[\d]{6}\/[A-z]', re.sub(r"\s", "", wd))]
        nfx = [wd for wd in wd_list if any(x in wd for x in ["electronically", "generated", "letter"])]

        m = model.KYCDocument()
        m.doc_name = doc_path
        m.adhaar_num = utils.get_adhaar_list(wd_list)
        m.doc_type = "Aadhaar"
        m.extract_text = wd_list

        adh_type = None
        if utils.check_adhaar_front(wd_list) and utils.check_adhaar_back(wd_list):
            if t[0] == 0:
                adh_type = (2, 3) + t
            if len(fx) > 0 or not len(nfx) > 0:
                adh_type = (2, 1) + t
            else:
                adh_type = (2, 3) + t
        elif utils.check_adhaar_back(wd_list):
            adh_type = (2, 2) + t
        else:
            adh_type = (2, 1) + t
        m.is_adhaar_type = adh_type
        return m

    else:
        m = model.KYCDocument()
        m.doc_name = doc_path
        m.doc_type = 'OTHERS'
        m.extract_text = wd_list
        return m


# read the documents and get the classification result
def read_pdf_imgs(doc_list):
    ext_lst = []

    for docs in doc_list:
        d = docs.lst_docs_in_zip
        for doc_path in d:
            ip = docs.inter_path + "//" + doc_path
            if ip[ip.rindex('.') + 1:] == "pdf":
                if utils.check_PDF_valid(ip):
                    # print(docs.inter_path + "//" + doc_path)
                    with open(ip, 'rb') as pdf:
                        images_from_path = convert_from_bytes(pdf.read(), dpi=500)
                        extract_pdf_text = []
                        for i, page in enumerate(images_from_path):
                            image_cropped = np.array(page)
                            gray_img = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2GRAY)
                            id_text = pytesseract.image_to_string(gray_img, lang="eng+hin",
                                                                  config='--psm 6')
                            extract_pdf_text.extend(id_text.split('\n'))

                        ext_lst.append(text_classify(extract_pdf_text, ip))
                        # print(text_classify(extract_pdf_text, ip))

            elif any(x in ip[ip.rindex('.') + 1:] for x in ["png", "jpeg", "jpg", "tiff"]):
                # print(ip)
                image = cv2.imread(ip)
                gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                id_text = pytesseract.image_to_string(gray_img, lang="eng+hin", config='--psm 6')
                id_text = id_text.split('\n')
                # print(id_text)
                ext_lst.append(text_classify(id_text, ip))
                # print(text_classify(id_text))
                pass

    return ext_lst


def image_to_string(ig, conf, lang="eng"):
    return pytesseract.image_to_string(ig, lang=lang, config=conf)


def perform_hocr(PDF_file, lang="eng", tess_con="hocr"):
    pytesseract.run_tesseract(PDF_file, PDF_file, lang=lang, extension='hocr', config=tess_con)


"""
closed this image_cropped image before going out of the function
"""


def get_adhaar_address2(PDF_file):
    perform_hocr(PDF_file)
    blocks = []
    image_cropped = cv2.imread(PDF_file)
    lst = ["address", "w/o", "o70", "d/o", "d/0", "s/o", "wo", "advrese"]
    with open("{}.hocr".format(PDF_file), 'r', encoding="utf8") as file:
        filedata = file.read()
        soup = BeautifulSoup(filedata, 'html.parser')
        words = soup.findAll('span')
        is_adhaar_detect = False
        m = ""
        ls = []
        for s in words:
            sp = s.text.strip().replace("\n", " ")
            sp = re.sub(r"[,@|\:\'?\.$%_]", "", sp, flags=re.I).strip()
            if len(sp) == 0:
                continue

            if is_adhaar_detect:
                if sp.lower() == m:
                    blocks.append(s)
                    break

            if not is_adhaar_detect:
                for z in ["address", "addre", "advrese"]:
                    if utils.check_str_exist2(z, sp.lower()):  # z in sp.lower():
                        is_adhaar_detect = True
                        ls = [x for x in lst if x in sp.lower()]
                        m = z
                        break

    if len(blocks) > 0:
        zz = blocks[0]['title'].split(';')[0]
        zz = zz.split(' ')[1:]
        zz = [int(x) for x in zz]
        lp = []
        lp.append(zz[0])
        lp.append(zz[1] - 30)
        lp.append(zz[0] + 830)
        lp.append(zz[1] + 300)

        if len(ls) > 1:
            return image_to_string(utils.get_image_slice(image_cropped, lp), conf="--psm 6")

        else:

            address_loc = zz[0]
            rel_add = [0]
            with open("{}.hocr".format(PDF_file), 'r',
                      encoding="utf8") as file:
                filedata = file.read()
                soup = BeautifulSoup(filedata, 'html.parser')
                words = soup.findAll('span')
                blocks = []
                for i, s in enumerate(words):
                    sp = s.text
                    sp = s.text.split("\n")
                    sp = [sub.replace('/', '') for sub in sp]
                    sp = [sub.replace('|', '') for sub in sp]
                    sp = [sub.replace(':', '') for sub in sp]
                    sp_string = " ".join(sp)
                    for j, ssp in enumerate(sp):
                        if ("so" == ssp.lower()) or ("do" == ssp.lower()) or ("wo" == ssp.lower()) or (
                                "mo" == ssp.lower()):
                            for k, line in enumerate(s):
                                if k == j:
                                    z1 = words[i + k]['title'].split(';')[0]
                                    z1 = z1.split(' ')[1:]
                                    z1 = [int(x) for x in z1]
                                    rel_add.append(z1[0])
            rel_add = max(rel_add)
            diff = abs(int(rel_add) - int(address_loc))
            if diff < 280:
                diff = diff
            elif diff > 1:
                diff = 0
            else:
                diff = 50

            zz[0] = zz[0] - diff - 10
            lp = []
            lp.append(zz[0])
            lp.append(zz[1] - 30)
            lp.append(zz[0] + 720)
            lp.append(zz[1] + 500)

            return image_to_string(utils.get_image_slice(image_cropped, lp), lang="eng+hin", conf="--psm 6")

    if len(blocks) == 0:
        lst = ["पता"]
        with open("{}.hocr".format(PDF_file), 'r',
                  encoding="utf8") as file:
            filedata = file.read()
            soup = BeautifulSoup(filedata, 'html.parser')
            words = soup.findAll('span')
            is_adhaar_detect = False
            m = ""
            ls = []
            for s in words:
                sp = s.text.strip().replace("\n", " ")
                sp = re.sub(r"[,@|\:\'?\.$%_]", "", sp, flags=re.I).strip()
                if len(sp) == 0:
                    continue

                if is_adhaar_detect:
                    if sp.lower() == m:
                        blocks.append(s)
                        break

                if not is_adhaar_detect:
                    for z in ["पता"]:
                        if z in sp:  # z in sp.lower():
                            is_adhaar_detect = True
                            ls = [x for x in lst if x in sp.lower()]
                            m = z
                            break

        if len(blocks) > 0:
            zz = blocks[0]['title'].split(';')[0]
            zz = zz.split(' ')[1:]
            zz = [int(x) for x in zz]
            lp = []
            lp.append(zz[0] + 800)
            lp.append(zz[1] - 70)
            lp.append(zz[0] + 1500)
            lp.append(zz[1] + 300)
            h, w = image_cropped.shape[0:2]
            if int(lp[0]) > w:
                return None
            else:
                try:
                    return image_to_string(utils.get_image_slice(image_cropped, lp), conf="--psm 6")
                except:
                    return None
    return None


def get_adhaar_address(PDF_file):
    add = get_adhaar_address2(PDF_file)
    try:
        if not add is None:
            txt = utils.rem_non_ascii(add)
            txt = txt.replace("'", "")
            x = re.search(r"\D(\d{6})\D", str(txt)) or re.search(r"\D(\d{5})\D", str(txt))
            if x is not None:
                txt = txt[:x.end()]

        add = utils.rem_non_ascii(add)
        add = " ".join(x for x in add.split("\n"))
        add = re.sub(r"[,@|\'?{}\.$%_]", "", add, flags=re.I)
    except:
        add = " "
    # create_update_adhar(doc_name, address=add)
    return add


def test_address4(img_name, image_cropped):
    perform_hocr(img_name)
    pnts = utils.get_your_adhaar_pos4(img_name)
    if pnts is None:
        return
    pnts[0] = pnts[0] - 900
    pnts[1] = pnts[1] - 50
    pnts[2] = pnts[2] - 200
    pnts[3] = pnts[3] - 400

    # guess_name = getPersonName(wd)
    lst = ["address", "w/o", "o70", "d/o", "d/0", "s/o", "wo", "so", "9/0", "vo", "0:", "s10"]
    txt = image_to_string(utils.get_image_slice(image_cropped, pnts), conf="--psm 6", lang="eng+hin")
    txt = txt.replace("$", "S")
    if not txt is None:
        txt = utils.rem_non_ascii(txt)
        txt = txt.replace("'", "")
        x = re.search(r"\D(\d{6})\D", str(txt)) or re.search(r"\D(\d{5})\D", str(txt))
        if x is not None:
            txt = txt[:x.end()]

    txt = txt.split('\n')
    txt = [x.strip() for x in txt]
    txt = [x for x in txt if len(x) > 3]
    for i, t in enumerate(txt):
        if any(x in t.lower() for x in lst):
            if len(txt[i - 1]) == 0:
                p = txt[i - 2]
            else:
                p = txt[i - 1]
            address = " ".join(x for x in txt[i:])
            return

    if not txt is None and len(txt) > 0:
        address = " ".join(x for x in txt[2:])

    return address


def test_address3(img_name, image_cropped):
    perform_hocr(img_name)
    pnts = utils.get_your_adhaar_pos4(img_name)
    if pnts is None:
        return
    lst = ["address", "w/o", "o70", "d/o", "d/0", "s/o", "wo", "so", "9/0", "vo", "0:", "s10"]
    txt = image_to_string(utils.get_image_slice(image_cropped, pnts), conf="--psm 6", lang="eng+hin")
    txt = txt.replace("$", "S")
    if not txt is None:
        txt = utils.rem_non_ascii(txt)
        txt = txt.replace("'", "")
        x = re.search(r"\D(\d{6})\D", str(txt)) or re.search(r"\D(\d{5})\D", str(txt))
        if x is not None:
            txt = txt[:x.end()]

    txt = txt.split('\n')
    txt = [x.strip().replace(",", "") for x in txt]  # 'To ,'
    txt = [re.sub(r"\s+", " ", x, flags=re.I) for x in txt if len(x) > 0]

    address = None
    for i, t in enumerate(txt):
        if any(x in t.lower() for x in lst):
            address = " ".join(x for x in txt[i:])
            return address

    if not txt is None and len(txt) > 0:
        address = " ".join(x for x in txt[2:])

    return address


def get_adhr_address(adm):
    image_cropped = cv2.imread(adm.doc_name)
    back = None
    doc_type = 3  # for else part
    if (adm.is_adhaar_type[2] == 4) or (adm.is_adhaar_type[1] == 2):
        doc_type = 3
    elif (adm.is_adhaar_type[1] == 3) and (adm.is_adhaar_type[2] == 4):
        doc_type = 2

    if doc_type == 3:
        return test_address3(adm.doc_name, image_cropped)
    elif doc_type == 2:
        return test_address4(adm.doc_name, image_cropped)
    else:
        if back:
            bac_lst = utils.get_text_hocr(adm.doc_name)
            if len(bac_lst) == 0:
                perform_hocr(image_cropped, adm.doc_name)
            return get_adhaar_address(PDF_file=adm.doc_name)
        else:
            return get_adhaar_address(PDF_file=adm.doc_name)


def check_value_is_present(mdl):
    if (mdl == '') or (mdl is None):
        return False
    if mdl.is_adhaar_address is None:
        return False
    elif mdl.is_adhaar_name is None:
        return False
    elif mdl.is_adhaar_dob is None:
        return False
    elif mdl.is_adhaar_gender is None:
        return False
    elif mdl.adhaar_num is None:
        return False
    else:
        return True


if __name__ == '__main__':
    get_file_tree1(doc_path)
    document_list = [read_save_zip(x) for x in document_list]
    kycdoc_list = read_pdf_imgs(document_list)
    # dbfile = open('examplePickle.pkl', 'ab')
    # pickle.dump(kycdoc_list, dbfile)
    # dbfile.close()

    final_lst = []
    for mdl in kycdoc_list:
        if mdl.doc_type == 'Aadhaar':
            t = mdl.is_adhaar_type
            image = cv2.imread(mdl.doc_name)
            # extract data using qr
            m = aadhar(image)

            if not check_value_is_present(m):
                details = utils.name_dob_gender(mdl.extract_text)
                m = mdl
                m.is_adhaar_name = details[0]
                m.is_adhaar_gender = details[1]
                m.is_adhaar_dob = details[2]
                m.is_adhaar_address = get_adhr_address(m)

                if m.adhaar_num is None:
                    m.adhaar_num = utils.get_adhaar_list(utils.get_text_hocr(m.doc_name))

            final_lst.append(m)
        else:
            final_lst.append(mdl)

    dbfile = open('examplePickle.pkl', 'ab')
    pickle.dump(final_lst, dbfile)
    dbfile.close()
