class Document:
    zip_path = None
    zip_file_name = None
    inter_path = None
    lst_docs_in_zip = []


class KYCDocument:
    doc_name = None
    bin_img = None
    extract_text = ""
    doc_type = None  # Aadhaar, Pan, Others
    is_adhaar_type = None # Big , small
    adhaar_num = None
    is_adhaar_name = None
    is_adhaar_dob = None
    is_adhaar_gender = None
    is_adhaar_address = None


    def __str__(self) -> str:
        return "doc_type: %s adhaar_num: %s adhaar_name: %s" % (self.doc_type, self.adhaar_num, self.is_adhaar_name)




