import re
import json


class CommandParser:

    def __init__(self):

        self.operations = {

            "filter": [
                "getir",
                "listele",
                "filtrele",
                "göster",
                "bul"
            ],

            "sort": [
                "sırala",
                "küçükten",
                "büyükten"
            ],

            "group": [
                "grupla",
                "topla"
            ],

            "delete_column": [
                "sil",
                "kaldır"
            ],

            "rename_column": [
                "değiştir",
                "yeniden adlandır"
            ],

            "duplicates": [
                "tekrar eden",
                "mükerrer"
            ],

            "dropna": [
                "boş",
                "eksik"
            ],

            "replace": [
                "değiştir",
                "yerine yaz"
            ],

            "chart": [
                "grafik",
                "çiz"
            ],

            "statistics": [
                "istatistik",
                "özet",
                "analiz"
            ]

        }

    def parse(self, text):

        text = text.lower()

        result = {
            "operation": None,
            "column": None,
            "operator": None,
            "value": None
        }

        for op, words in self.operations.items():

            for w in words:

                if w in text:

                    result["operation"] = op

                    break

        self.find_operator(text, result)

        self.find_value(text, result)

        self.find_column(text, result)

        return result

    def find_operator(self, text, result):

        if "büyük" in text:

            result["operator"] = ">"

        elif "küçük" in text:

            result["operator"] = "<"

        elif "eşit" in text:

            result["operator"] = "=="

        elif "içeren" in text:

            result["operator"] = "contains"

    def find_value(self, text, result):

        m = re.search(r"\d+", text)

        if m:

            result["value"] = int(m.group())

    def find_column(self, text, result):

        columns = [

            "yaş",

            "isim",

            "soyisim",

            "şehir",

            "satış",

            "telefon",

            "maaş",

            "gelir",

            "tc",

            "adres"

        ]

        for c in columns:

            if c in text:

                result["column"] = c

                return