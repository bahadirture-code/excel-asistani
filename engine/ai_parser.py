import os
import json
from groq import Groq


class AIParser:

    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(base_dir, "system_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def parse(self, prompt, dataframe, temperature=0.1, max_tokens=2048):
        columns = [str(c) for c in dataframe.columns]
        sample = dataframe.head(3).fillna("").astype(str)
        preview = sample.to_dict(orient="records")
        column_types = {str(col): str(dtype) for col, dtype in dataframe.dtypes.items()}

        user_prompt = f"""
EXCEL SÜTUNLARI VE TİPLERİ
{json.dumps(column_types, ensure_ascii=False)}

İLK 3 SATIR
{json.dumps(preview, ensure_ascii=False)}

KULLANICI İSTEĞİ
{prompt}

ÖNEMLİ: Çıktı JSON içinde mutlaka kullanıcıya gösterilmek üzere anlaşılır Türkçe bir "plan" açıklaması ekle.
"""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        answer = response.choices[0].message.content
        data = json.loads(answer)
        if "steps" not in data:
            raise Exception("steps bulunamadı")
        return data