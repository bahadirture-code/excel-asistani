from difflib import SequenceMatcher


class ColumnMatcher:

    def __init__(self):

        self.alias = {

            "yaş":[
                "yaş","yas","age","person_age","kisi_yasi"
            ],

            "isim":[
                "isim","ad","adi","firstname","name"
            ],

            "soyisim":[
                "soyisim","soyad","lastname","surname"
            ],

            "adsoyad":[
                "ad soyad","adsoyad","isim soyisim","fullname","full name"
            ],

            "telefon":[
                "telefon","gsm","cep","mobile","phone"
            ],

            "şehir":[
                "şehir","il","city","province"
            ],

            "adres":[
                "adres","address"
            ],

            "satış":[
                "satış","satis","sale","sales","amount","tutar"
            ],

            "gelir":[
                "gelir","income","maaş","maas"
            ],

            "tc":[
                "tc","tc kimlik","kimlik","identity","id"
            ]

        }

    def score(self,a,b):

        return SequenceMatcher(
            None,
            str(a).lower(),
            str(b).lower()
        ).ratio()

    def match(self,user_column,columns):

        if user_column is None:
            return None

        user_column=str(user_column).lower()

        best_column=None

        best_score=0

        for column in columns:

            s=self.score(
                user_column,
                column
            )

            if s>best_score:

                best_score=s

                best_column=column

        if best_score>=0.70:

            return best_column

        for alias_name,alias_list in self.alias.items():

            if user_column in alias_list:

                for real_column in columns:

                    if str(real_column).lower() in alias_list:

                        return real_column

        return None

    def exists(self,user_column,columns):

        return self.match(
            user_column,
            columns
        ) is not None

    def normalize(self,columns):

        result=[]

        for c in columns:

            result.append(str(c).strip())

        return result

    def all_matches(self,user_columns,columns):

        result={}

        for item in user_columns:

            result[item]=self.match(
                item,
                columns
            )

        return result