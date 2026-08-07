import json
from groq import Groq


class AIParser:

    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def parse(self, prompt, dataframe, temperature=0.0, max_tokens=2048):
        columns = [str(c) for c in dataframe.columns]
        sample = dataframe.head(3).fillna("").astype(str)
        preview = sample.to_dict(orient="records")

        user_prompt = f"""
EXCEL SÜTUNLARI
{json.dumps(columns, ensure_ascii=False)}

İLK 3 SATIR
{json.dumps(preview, ensure_ascii=False)}

KULLANICI İSTEĞİ
{prompt}
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