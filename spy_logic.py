import re

class ScamSpy:
    def analyze_message(self, text):
        intel = {
            "upi_id": [],
            "phone": [],
            "bank_account": [],
            "phishing_links": [],
            "threat_score": 0
        }
        
        # 1. UPI Extraction
        intel["upi_id"] = re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text)
        
        # 2. Phishing Links (Enhanced Regex)
        intel["phishing_links"] = re.findall(r'(?:https?://)?(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', text)
        
        # 3. Phone Numbers
        intel["phone"] = re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text)
        
        # 4. Bank Account Numbers
        potential_accounts = re.findall(r'\b\d{9,18}\b', text)
        intel["bank_account"] = [x for x in potential_accounts if x not in intel["phone"]]

        return intel
