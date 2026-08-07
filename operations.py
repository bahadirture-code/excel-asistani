import pandas as pd

class DataOperations:

    # ==================== FİLTRE / SIRALAMA / GRUPLAMA ====================

    def filter_rows(self, df, column, operator, value):
        if operator == ">":
            return df[df[column] > value]
        elif operator == "<":
            return df[df[column] < value]
        elif operator == ">=":
            return df[df[column] >= value]
        elif operator == "<=":
            return df[df[column] <= value]
        elif operator == "==":
            return df[df[column] == value]
        elif operator == "!=":
            return df[df[column] != value]
        elif operator == "contains":
            return df[df[column].astype(str).str.contains(str(value), case=False, na=False)]
        else:
            raise ValueError(f"Desteklenmeyen operatör: {operator}")

    def sort(self, df, column, ascending=True):
        return df.sort_values(by=column, ascending=ascending)

    def group_sum(self, df, group_column, value_column):
        return df.groupby(group_column)[value_column].sum().reset_index()

    def group_count(self, df, group_column):
        return df.groupby(group_column).size().reset_index(name='count')

    # ==================== TEMİZLEME / DÜZENLEME ====================

    def remove_duplicates(self, df):
        return df.drop_duplicates()

    def remove_empty(self, df):
        return df.dropna(how='all')

    def delete_column(self, df, column):
        return df.drop(columns=[column])

    def rename_column(self, df, old_name, new_name):
        return df.rename(columns={old_name: new_name})

    def replace(self, df, column, old_value, new_value):
        df = df.copy()
        df[column] = df[column].replace(old_value, new_value)
        return df

    def fill_empty(self, df, column, value):
        df = df.copy()
        df[column] = df[column].fillna(value)
        return df

    def unique(self, df, column):
        return pd.DataFrame({column: df[column].unique()})

    def value_counts(self, df, column):
        return df[column].value_counts().reset_index()

    def head(self, df, count=10):
        return df.head(count)

    def tail(self, df, count=10):
        return df.tail(count)

    def keep_columns(self, df, columns):
        return df[columns]

    def remove_columns(self, df, columns):
        return df.drop(columns=columns)

    def merge_columns(self, df, col1, col2, new_col):
        df = df.copy()
        df[new_col] = df[col1].astype(str) + " " + df[col2].astype(str)
        return df

    # ==================== HESAPLAMA / FORMÜL ====================

    def calculate(self, df, column, operation):
        if operation == "sum":
            return df[column].sum()
        elif operation == "mean":
            return df[column].mean()
        elif operation == "max":
            return df[column].max()
        elif operation == "min":
            return df[column].min()
        elif operation == "count":
            return df[column].count()
        else:
            raise ValueError(f"Desteklenmeyen işlem: {operation}")

    def formula(self, df, step):
        new_col = step.get("new_column")
        formula = step.get("formula")
        df = df.copy()
        df[new_col] = df.eval(formula)
        return df

    def add_column(self, df, column, default_value=""):
        df = df.copy()
        df[column] = default_value
        return df

    def remove_rows(self, df, column, value):
        return df[df[column] != value]

    def pivot(self, df, index, values, aggfunc="sum"):
        return df.pivot_table(index=index, values=values, aggfunc=aggfunc).reset_index()

    # ==================== METİN İŞLEMLERİ ====================

    def uppercase(self, df, column):
        df = df.copy()
        df[column] = df[column].astype(str).str.upper()
        return df

    def lowercase(self, df, column):
        df = df.copy()
        df[column] = df[column].astype(str).str.lower()
        return df

    def trim(self, df, column):
        df = df.copy()
        df[column] = df[column].astype(str).str.strip()
        return df

    def remove_spaces(self, df, column):
        df = df.copy()
        df[column] = df[column].astype(str).str.replace(" ", "", regex=False)
        return df

    def split_column(self, df, step):
        column = step.get("column")
        separator = step.get("separator", " ")
        new_columns = step.get("new_columns", [])
        df = df.copy()
        parts = df[column].astype(str).str.split(separator, expand=True)
        for i, col in enumerate(new_columns):
            if i < parts.shape[1]:
                df[col] = parts[i]
        return df

    def concat_columns(self, df, step):
        columns = step.get("columns")
        new_col = step.get("new_column")
        separator = step.get("separator", " ")
        df = df.copy()
        df[new_col] = df[columns].astype(str).agg(separator.join, axis=1)
        return df

    def remove_text(self, df, step):
        column = step.get("column")
        text = step.get("text")
        df = df.copy()
        df[column] = df[column].astype(str).str.replace(text, "", regex=False)
        return df

    def add_text(self, df, step):
        column = step.get("column")
        text = step.get("text")
        position = step.get("position", "end")
        df = df.copy()
        if position == "start":
            df[column] = text + df[column].astype(str)
        else:
            df[column] = df[column].astype(str) + text
        return df

    # ==================== TİP DÖNÜŞÜMLERİ ====================

    def convert_dtype(self, df, step):
        column = step.get("column")
        dtype = step.get("dtype")
        df = df.copy()
        if dtype == "string":
            df[column] = df[column].astype(str)
        elif dtype == "int":
            df[column] = df[column].astype(int)
        elif dtype == "float":
            df[column] = df[column].astype(float)
        elif dtype == "datetime":
            df[column] = pd.to_datetime(df[column])
        return df

    # ==================== EKSİK VERİ İŞLEMLERİ ====================

    def fill_forward(self, df):
        return df.ffill()

    def fill_backward(self, df):
        return df.bfill()

    def remove_null_columns(self, df):
        return df.dropna(axis=1, how="all")

    # ==================== SIRALAMA / ENDEKS ====================

    def sort_multiple(self, df, step):
        columns = step.get("columns")
        ascending = step.get("ascending", True)
        return df.sort_values(by=columns, ascending=ascending)

    def sort_index(self, df):
        return df.sort_index()

    def reset_index(self, df):
        return df.reset_index(drop=True)

    def reverse(self, df):
        return df.iloc[::-1].reset_index(drop=True)

    # ==================== SAYISAL FİLTRELEME ====================

    def remove_negative(self, df, column):
        return df[df[column] >= 0]

    def remove_zero(self, df, column):
        return df[df[column] != 0]

    def filter_between(self, df, step):
        column = step.get("column")
        min_val = step.get("min")
        max_val = step.get("max")
        return df[(df[column] >= min_val) & (df[column] <= max_val)]

    # ==================== YÜZDE / YUVARLAMA ====================

    def percentage_column(self, df, step):
        column = step.get("column")
        new_col = step.get("new_column")
        df = df.copy()
        total = df[column].sum()
        df[new_col] = (df[column] / total) * 100
        return df

    def round_column(self, df, step):
        column = step.get("column")
        digits = step.get("digits", 2)
        df = df.copy()
        df[column] = df[column].round(digits)
        return df

    # ==================== ÖRNEKLEME ====================

    def top(self, df, count=10):
        return df.head(count)

    def bottom(self, df, count=10):
        return df.tail(count)

    def sample(self, df, count=10):
        return df.sample(n=min(count, len(df)))

    # ==================== AYKIRI DEĞERLER ====================

    def detect_outliers(self, df, column):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        return df[(df[column] < low) | (df[column] > high)]

    def remove_outliers(self, df, column):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        return df[(df[column] >= low) & (df[column] <= high)]

    # ==================== TEKRAR EDENLER ====================

    def duplicate_rows(self, df):
        return df[df.duplicated(keep=False)]

    # ==================== ÖZET / RAPORLAR ====================

    def statistics(self, df):
        return df.describe().T.reset_index()

    def null_summary(self, df):
        return pd.DataFrame({
            "Column": df.columns,
            "Null Count": df.isna().sum().values,
            "Null %": (df.isna().sum() / len(df) * 100).round(2)
        })

    def column_info(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Type": str(df[c].dtype),
                "Unique": df[c].nunique(),
                "Null": df[c].isna().sum()
            })
        return pd.DataFrame(rows)

    def frequency_table(self, df, column):
        return df[column].value_counts(dropna=False).reset_index()

    def find_replace_all(self, df, step):
        old = step.get("old_value")
        new = step.get("new_value")
        return df.replace(old, new)

    def sort_columns(self, df):
        return df.reindex(sorted(df.columns), axis=1)

    def transpose(self, df):
        return df.T.reset_index()

    def remove_blank_strings(self, df):
        return df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")

    def memory_usage(self, df):
        return pd.DataFrame({
            "Column": df.columns,
            "Memory(Bytes)": [df[c].memory_usage(deep=True) for c in df.columns]
        })

    def dtypes(self, df):
        return pd.DataFrame({"Column": df.columns, "Type": [str(df[c].dtype) for c in df.columns]})

    def corr(self, df):
        return df.corr(numeric_only=True)

    def remove_constant_columns(self, df):
        return df.loc[:, df.nunique() > 1]

    def duplicate_columns_summary(self, df):
        duplicated = []
        cols = list(df.columns)
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                if df[cols[i]].equals(df[cols[j]]):
                    duplicated.append({"Column1": cols[i], "Column2": cols[j]})
        return pd.DataFrame(duplicated)

    def column_cardinality(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Unique": df[c].nunique(),
                "Total": len(df),
                "Cardinality %": round(df[c].nunique() / len(df) * 100, 2)
            })
        return pd.DataFrame(rows)

    def suggest_charts(self, df):
        numeric = df.select_dtypes(include="number").columns.tolist()
        text = [c for c in df.columns if c not in numeric]
        charts = []
        if text and numeric:
            charts.append({"Chart": "Bar", "X": text[0], "Y": numeric[0]})
            charts.append({"Chart": "Line", "X": text[0], "Y": numeric[0]})
        if len(numeric) >= 2:
            charts.append({"Chart": "Scatter", "X": numeric[0], "Y": numeric[1]})
        if text and numeric:
            charts.append({"Chart": "Pie", "X": text[0], "Y": numeric[0]})
        return pd.DataFrame(charts) if charts else pd.DataFrame(columns=["Chart", "X", "Y"])

    def numeric_summary(self, df):
        return df.describe().T.reset_index()

    def text_summary(self, df):
        rows = []
        for c in df.select_dtypes(include="object").columns:
            rows.append({
                "Column": c,
                "Unique": df[c].nunique(),
                "Longest": df[c].astype(str).str.len().max(),
                "Shortest": df[c].astype(str).str.len().min()
            })
        return pd.DataFrame(rows)

    def detect_phone_columns(self, df):
        keywords = ["telefon", "phone", "gsm", "cep", "mobile"]
        rows = []
        for c in df.columns:
            found = any(k in str(c).lower() for k in keywords)
            rows.append({"Column": c, "Phone Column": found})
        return pd.DataFrame(rows)

    def detect_email_columns(self, df):
        keywords = ["mail", "email", "e-mail"]
        rows = []
        for c in df.columns:
            found = any(k in str(c).lower() for k in keywords)
            rows.append({"Column": c, "Email Column": found})
        return pd.DataFrame(rows)

    def detect_date_columns(self, df):
        rows = []
        for c in df.columns:
            rows.append({"Column": c, "Date": pd.api.types.is_datetime64_any_dtype(df[c])})
        return pd.DataFrame(rows)

    def dataframe_info(self, df):
        return pd.DataFrame({
            "Rows": [len(df)],
            "Columns": [len(df.columns)],
            "Memory(MB)": [round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)]
        })

    def smart_report(self, df):
        numeric = df.select_dtypes(include="number")
        report = {
            "Toplam Satır": len(df),
            "Toplam Kolon": len(df.columns),
            "Boş Hücre": int(df.isna().sum().sum()),
            "Tekrar Eden Satır": int(df.duplicated().sum())
        }
        if len(numeric.columns) > 0:
            report["Sayısal Kolon"] = len(numeric.columns)
            report["Toplam Sayısal Değer"] = numeric.sum().sum()
        return pd.DataFrame([report])

    def top_null_columns(self, df, count=10):
        s = df.isna().sum()
        return s.sort_values(ascending=False).head(count).reset_index().rename(columns={"index": "Column", 0: "Null"})

    def top_duplicate_values(self, df, column, count=20):
        return df[column].value_counts().head(count).reset_index()

    def longest_text(self, df, column, count=20):
        x = df.copy()
        x["__LEN__"] = x[column].astype(str).str.len()
        return x.sort_values("__LEN__", ascending=False).head(count).drop(columns="__LEN__")

    def detect_currency_columns(self, df):
        keywords = ["fiyat", "price", "ücret", "ucret", "tutar", "amount", "toplam", "total", "satış", "satis", "gelir", "income"]
        rows = []
        for c in df.columns:
            found = any(k in str(c).lower() for k in keywords)
            rows.append({"Column": c, "Currency": found})
        return pd.DataFrame(rows)

    def detect_id_columns(self, df):
        keywords = ["id", "kod", "code", "tc", "kimlik", "uuid"]
        rows = []
        for c in df.columns:
            found = any(k in str(c).lower() for k in keywords)
            rows.append({"Column": c, "ID": found})
        return pd.DataFrame(rows)

    def dataset_health(self, df):
        total = len(df)
        score = 100
        score -= min(40, int(df.isna().sum().sum()))
        score -= min(30, int(df.duplicated().sum()))
        return pd.DataFrame({
            "Health Score": [max(score, 0)],
            "Rows": [total],
            "Columns": [len(df.columns)]
        })

    def column_lengths(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Max Length": df[c].astype(str).str.len().max(),
                "Average Length": round(df[c].astype(str).str.len().mean(), 2)
            })
        return pd.DataFrame(rows)

    # ==================== AI FONKSİYONLARI ====================

    def ai_dataset_score(self, df):
        score = 100
        duplicate = int(df.duplicated().sum())
        nulls = int(df.isna().sum().sum())
        if duplicate > 0:
            score -= min(duplicate, 20)
        if nulls > 0:
            score -= min(nulls, 30)
        numeric = len(df.select_dtypes(include="number").columns)
        text = len(df.columns) - numeric
        return pd.DataFrame({
            "AI Score": [max(score, 0)],
            "Rows": [len(df)],
            "Columns": [len(df.columns)],
            "Numeric": [numeric],
            "Text": [text],
            "Duplicates": [duplicate],
            "Null": [nulls]
        })

    def ai_find_problems(self, df):
        problems = []
        for c in df.columns:
            if df[c].isna().sum() > 0:
                problems.append({"Column": c, "Problem": "Null Values"})
            if df[c].duplicated().sum() > 0:
                problems.append({"Column": c, "Problem": "Duplicate Values"})
            if df[c].nunique() == 1:
                problems.append({"Column": c, "Problem": "Constant Column"})
        return pd.DataFrame(problems)

    def ai_best_chart(self, df):
        numeric = df.select_dtypes(include="number").columns.tolist()
        text = [c for c in df.columns if c not in numeric]
        chart = "Table"
        x = ""
        y = ""
        if text and numeric:
            chart = "Bar"
            x = text[0]
            y = numeric[0]
        elif len(numeric) >= 2:
            chart = "Scatter"
            x = numeric[0]
            y = numeric[1]
        return pd.DataFrame({"Chart": [chart], "X": [x], "Y": [y]})

    def ai_insights(self, df):
        rows = []
        numeric = df.select_dtypes(include="number").columns
        for c in numeric:
            rows.append({
                "Column": c,
                "Average": round(df[c].mean(), 2),
                "Median": round(df[c].median(), 2),
                "Min": round(df[c].min(), 2),
                "Max": round(df[c].max(), 2),
                "Std": round(df[c].std(), 2)
            })
        return pd.DataFrame(rows)

    def ai_missing_columns(self, df):
        rows = []
        total = len(df)
        for c in df.columns:
            missing = df[c].isna().sum()
            rows.append({
                "Column": c,
                "Missing": int(missing),
                "Percent": round(missing / total * 100, 2)
            })
        return pd.DataFrame(rows)

    def ai_column_score(self, df):
        rows = []
        total = len(df)
        for c in df.columns:
            score = 100
            score -= min(50, int(df[c].isna().sum() / total * 100))
            score -= min(20, int(df[c].duplicated().sum() / total * 100))
            rows.append({"Column": c, "Score": max(score, 0)})
        return pd.DataFrame(rows)

    def ai_auto_fix(self, df):
        df = df.copy()
        df = df.drop_duplicates()
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        df = df.dropna(how="all")
        for c in df.columns:
            if str(df[c].dtype) == "object":
                df[c] = df[c].astype(str).str.strip()
        return df

    def ai_detect_column_types(self, df):
        rows = []
        for c in df.columns:
            dtype = "Text"
            if pd.api.types.is_numeric_dtype(df[c]):
                dtype = "Numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[c]):
                dtype = "Date"
            rows.append({"Column": c, "Detected": dtype})
        return pd.DataFrame(rows)

    def ai_empty_rows(self, df):
        return df[df.isna().all(axis=1)]

    def ai_duplicate_report(self, df):
        return pd.DataFrame({
            "Duplicate Rows": [int(df.duplicated().sum())],
            "Duplicate %": [round(df.duplicated().sum() / len(df) * 100, 2)]
        })

    def ai_business_summary(self, df):
        rows = []
        numeric = df.select_dtypes(include="number").columns
        for c in numeric:
            rows.append({
                "Metric": c,
                "Total": round(df[c].sum(), 2),
                "Average": round(df[c].mean(), 2),
                "Maximum": round(df[c].max(), 2),
                "Minimum": round(df[c].min(), 2)
            })
        return pd.DataFrame(rows)

    def ai_column_relationships(self, df):
        corr = df.corr(numeric_only=True)
        rows = []
        cols = list(corr.columns)
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                rows.append({
                    "Column1": cols[i],
                    "Column2": cols[j],
                    "Correlation": round(corr.iloc[i, j], 4)
                })
        return pd.DataFrame(rows)

    def ai_top_categories(self, df, column, count=10):
        return df[column].value_counts().head(count).reset_index().rename(columns={"index": "Category", column: "Count"})

    def ai_bottom_categories(self, df, column, count=10):
        return df[column].value_counts().tail(count).reset_index().rename(columns={"index": "Category", column: "Count"})

    def ai_generate_sql(self, df, table_name="data"):
        type_map = {
            "int64": "INTEGER",
            "float64": "REAL",
            "object": "TEXT",
            "bool": "BOOLEAN",
            "datetime64[ns]": "DATETIME"
        }
        rows = []
        for c in df.columns:
            dtype = str(df[c].dtype)
            sql_type = type_map.get(dtype, "TEXT")
            rows.append(f"{c} {sql_type}")
        sql = "CREATE TABLE " + table_name + " (\n" + ",\n".join(rows) + "\n);"
        return pd.DataFrame({"SQL": [sql]})

    def ai_column_dictionary(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Type": str(df[c].dtype),
                "Null": int(df[c].isna().sum()),
                "Unique": int(df[c].nunique()),
                "Example": str(df[c].dropna().head(1).tolist())
            })
        return pd.DataFrame(rows)

    def ai_detect_primary_key(self, df):
        rows = []
        for c in df.columns:
            rows.append({"Column": c, "Primary Key Candidate": df[c].is_unique})
        return pd.DataFrame(rows)

    def ai_detect_empty_columns(self, df):
        rows = []
        for c in df.columns:
            rows.append({"Column": c, "Empty": df[c].isna().all()})
        return pd.DataFrame(rows)

    def ai_dashboard_summary(self, df):
        numeric = df.select_dtypes(include="number")
        result = {
            "Rows": len(df),
            "Columns": len(df.columns),
            "Missing": int(df.isna().sum().sum()),
            "Duplicates": int(df.duplicated().sum())
        }
        for c in numeric.columns[:5]:
            result[f"{c} Toplam"] = round(numeric[c].sum(), 2)
        return pd.DataFrame([result])

    def ai_kpi(self, df, column):
        s = df[column]
        return pd.DataFrame({
            "Sum": [round(s.sum(), 2)],
            "Average": [round(s.mean(), 2)],
            "Median": [round(s.median(), 2)],
            "Maximum": [round(s.max(), 2)],
            "Minimum": [round(s.min(), 2)]
        })

    def ai_find_anomalies(self, df, column):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        return df[(df[column] < low) | (df[column] > high)]

    def ai_duplicate_cells(self, df, column):
        return df[df[column].duplicated(keep=False)]

    def ai_clean_column_names(self, df):
        df = df.copy()
        cols = []
        for c in df.columns:
            c = str(c).strip().replace(" ", "_").replace("-", "_").replace("/", "_")
            cols.append(c.upper())
        df.columns = cols
        return df

    def ai_remove_full_duplicates(self, df):
        return df.drop_duplicates(keep="first")

    def ai_sort_all_columns(self, df):
        return df.reindex(sorted(df.columns), axis=1)

    def ai_detect_boolean_columns(self, df):
        rows = []
        for c in df.columns:
            u = df[c].dropna().unique()
            rows.append({"Column": c, "Boolean": len(u) <= 2})
        return pd.DataFrame(rows)

    def ai_column_summary(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Type": str(df[c].dtype),
                "Rows": len(df),
                "Null": int(df[c].isna().sum()),
                "Unique": int(df[c].nunique())
            })
        return pd.DataFrame(rows)

    def ai_detect_currency(self, df, column):
        s = df[column].astype(str)
        currencies = ["₺", "$", "€", "£"]
        rows = []
        for cur in currencies:
            rows.append({
                "Currency": cur,
                "Count": int(s.str.contains(cur, regex=False, na=False).sum())
            })
        return pd.DataFrame(rows)

    def ai_text_statistics(self, df, column):
        s = df[column].astype(str)
        return pd.DataFrame({
            "Average Length": [round(s.str.len().mean(), 2)],
            "Maximum Length": [int(s.str.len().max())],
            "Minimum Length": [int(s.str.len().min())],
            "Unique": [int(s.nunique())]
        })

    def ai_numeric_statistics(self, df, column):
        s = df[column]
        return pd.DataFrame({
            "Sum": [s.sum()],
            "Average": [round(s.mean(), 2)],
            "Median": [round(s.median(), 2)],
            "Std": [round(s.std(), 2)],
            "Variance": [round(s.var(), 2)]
        })

    def ai_export_json(self, df):
        return pd.DataFrame({"JSON": [df.to_json(orient="records", force_ascii=False)]})

    # ==================== OTOMATİK TESPİT / TEMİZLEME ====================

    def auto_clean(self, df):
        df = df.copy()
        df = df.drop_duplicates()
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        df = df.dropna(how="all")
        for c in df.columns:
            if str(df[c].dtype) == "object":
                df[c] = df[c].astype(str).str.strip()
        return df

    def remove_empty_columns(self, df):
        return df.dropna(axis=1, how="all")

    def column_statistics(self, df, column):
        s = df[column]
        return pd.DataFrame({
            "count": [s.count()],
            "null": [s.isna().sum()],
            "unique": [s.nunique()],
            "min": [s.min()],
            "max": [s.max()]
        })

    def random_rows(self, df, count):
        return df.sample(n=min(count, len(df)), random_state=42)

    def smart_filter(self, df, column, value):
        s = df[column]
        if str(s.dtype).startswith(("int", "float")):
            try:
                value = float(value)
                return df[s == value]
            except:
                pass
        return df[s.astype(str).str.contains(str(value), case=False, na=False)]

    def smart_sort(self, df, column):
        try:
            return df.sort_values(by=column, key=lambda x: pd.to_numeric(x, errors="ignore"))
        except:
            return df.sort_values(by=column)

    def duplicate_summary(self, df):
        d = df.duplicated()
        return pd.DataFrame({
            "Toplam Satır": [len(df)],
            "Tekrar Eden": [int(d.sum())],
            "Tekil": [int(len(df) - d.sum())]
        })

    def empty_summary(self, df):
        rows = []
        for c in df.columns:
            rows.append({"Column": c, "Empty": int(df[c].isna().sum())})
        return pd.DataFrame(rows)

    def data_quality(self, df):
        rows = []
        total = len(df)
        for c in df.columns:
            rows.append({
                "Column": c,
                "Null": int(df[c].isna().sum()),
                "Unique": int(df[c].nunique()),
                "Duplicate": int(df[c].duplicated().sum()),
                "Fill Rate": round((1 - df[c].isna().sum() / total) * 100, 2)
            })
        return pd.DataFrame(rows)

    def auto_optimize(self, df):
        df = self.auto_detect_numeric(df)
        df = self.auto_detect_date_columns(df)
        return df

    def auto_detect_numeric(self, df):
        df = df.copy()
        for c in df.columns:
            try:
                df[c] = pd.to_numeric(df[c], errors="ignore")
            except:
                pass
        return df

    def auto_detect_date_columns(self, df):
        df = df.copy()
        for c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c], errors="raise")
            except:
                pass
        return df

    def top_values(self, df, column, count=10):
        return df[column].value_counts().head(count).reset_index()

    def bottom_values(self, df, column, count=10):
        return df[column].value_counts().tail(count).reset_index()

    def detect_numeric_columns(self, df):
        rows = []
        for c in df.columns:
            rows.append({"Column": c, "Numeric": pd.api.types.is_numeric_dtype(df[c])})
        return pd.DataFrame(rows)

    def auto_analyze(self, df):
        total_rows = len(df)
        total_columns = len(df.columns)
        duplicate_rows = int(df.duplicated().sum())
        empty_cells = int(df.isna().sum().sum())
        numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        text = [c for c in df.columns if c not in numeric and not pd.api.types.is_datetime64_any_dtype(df[c])]
        date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
        return pd.DataFrame({
            "Toplam Satır": [total_rows],
            "Toplam Kolon": [total_columns],
            "Boş Hücre": [empty_cells],
            "Tekrar Eden Satır": [duplicate_rows],
            "Sayısal Kolon": [len(numeric)],
            "Metin Kolonu": [len(text)],
            "Tarih Kolonu": [len(date_cols)]
        })

    def auto_profile(self, df):
        rows = []
        for c in df.columns:
            rows.append({
                "Column": c,
                "Type": str(df[c].dtype),
                "Null": int(df[c].isna().sum()),
                "Unique": int(df[c].nunique()),
                "Duplicate": int(df[c].duplicated().sum()),
                "Example": str(df[c].dropna().head(1).tolist())
            })
        return pd.DataFrame(rows)

    def ai_recommendations(self, df):
        recs = []
        if df.duplicated().sum() > 0:
            recs.append("Tekrar eden satırlar bulundu.")
        if df.isna().sum().sum() > 0:
            recs.append("Boş hücreler bulundu.")
        for c in df.columns:
            if df[c].nunique() == 1:
                recs.append(f"{c} kolonu tek değerden oluşuyor.")
        if len(df.select_dtypes(include="number").columns) == 0:
            recs.append("Sayısal kolon bulunamadı.")
        if not recs:
            recs.append("Veri kalitesi iyi görünüyor.")
        return pd.DataFrame({"Öneriler": recs})