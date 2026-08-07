import streamlit as st
import pandas as pd
import numpy as np
import warnings
from engine.operations import DataOperations
from engine.matcher import ColumnMatcher


class CommandEngine:

    def __init__(self):
        self.ops = DataOperations()
        self.matcher = ColumnMatcher()

    #########################################################

    def execute(self, data, df):
        steps = data.get("steps", [])
        result = df.copy()

        for step in steps:
            action = step.get("action")

            if action == "filter":
                result = self.filter(result, step)
            elif action == "sort":
                result = self.sort(result, step)
            elif action == "group_sum":
                result = self.group_sum(result, step)
            elif action == "group_count":
                result = self.group_count(result, step)
            elif action == "remove_duplicates":
                result = self.ops.remove_duplicates(result)
            elif action == "remove_empty":
                result = self.ops.remove_empty(result)
            elif action == "delete_column":
                result = self.delete_column(result, step)
            elif action == "rename_column":
                result = self.rename_column(result, step)
            elif action == "replace":
                result = self.replace(result, step)
            elif action == "statistics":
                result = self.ops.statistics(result)
            elif action == "fill_empty":
                result = self.fill_empty(result, step)
            elif action == "unique":
                result = self.unique(result, step)
            elif action == "value_counts":
                result = self.value_counts(result, step)
            elif action == "head":
                result = self.ops.head(result, step.get("count", 10))
            elif action == "tail":
                result = self.ops.tail(result, step.get("count", 10))
            elif action == "keep_columns":
                result = self.keep_columns(result, step)
            elif action == "remove_columns":
                result = self.remove_columns(result, step)
            elif action == "merge_columns":
                result = self.merge_columns(result, step)
            elif action == "pivot":
                result = self.pivot(result, step)
            elif action == "calculate":
                result = self.calculate(result, step)
            elif action == "add_column":
                result = self.add_column(result, step)
            elif action == "remove_rows":
                result = self.remove_rows(result, step)
            elif action == "formula":
                result = self.ops.formula(result, step)
            elif action == "convert_dtype":
                result = self.ops.convert_dtype(result, step)
            elif action == "uppercase":
                result = self.ops.uppercase(result, step.get("column"))
            elif action == "lowercase":
                result = self.ops.lowercase(result, step.get("column"))
            elif action == "trim":
                result = self.ops.trim(result, step.get("column"))
            elif action == "remove_spaces":
                result = self.ops.remove_spaces(result, step.get("column"))
            elif action == "fill_forward":
                result = self.ops.fill_forward(result)
            elif action == "fill_backward":
                result = self.ops.fill_backward(result)
            elif action == "remove_null_columns":
                result = self.ops.remove_null_columns(result)
            elif action == "split_column":
                result = self.ops.split_column(result, step)
            elif action == "concat_columns":
                result = self.ops.concat_columns(result, step)
            elif action == "sort_multiple":
                result = self.ops.sort_multiple(result, step)
            elif action == "remove_negative":
                result = self.ops.remove_negative(result, step.get("column"))
            elif action == "remove_zero":
                result = self.ops.remove_zero(result, step.get("column"))
            elif action == "percentage_column":
                result = self.ops.percentage_column(result, step)
            elif action == "round":
                result = self.ops.round_column(result, step)
            elif action == "filter_between":
                result = self.ops.filter_between(result, step)
            elif action == "top":
                result = self.ops.top(result, step.get("count", 10))
            elif action == "bottom":
                result = self.ops.bottom(result, step.get("count", 10))
            elif action == "sample":
                result = self.ops.sample(result, step.get("count", 10))
            elif action == "remove_text":
                result = self.ops.remove_text(result, step)
            elif action == "add_text":
                result = self.ops.add_text(result, step)
            elif action == "sort_index":
                result = self.ops.sort_index(result)
            elif action == "reset_index":
                result = self.ops.reset_index(result)
            elif action == "reverse":
                result = self.ops.reverse(result)
            elif action == "detect_outliers":
                result = self.ops.detect_outliers(result, step.get("column"))
            elif action == "remove_outliers":
                result = self.ops.remove_outliers(result, step.get("column"))
            elif action == "duplicate_rows":
                result = self.ops.duplicate_rows(result)
            elif action == "null_summary":
                result = self.ops.null_summary(result)
            elif action == "column_info":
                result = self.ops.column_info(result)
            elif action == "frequency_table":
                result = self.ops.frequency_table(result, step.get("column"))
            elif action == "find_replace_all":
                result = self.ops.find_replace_all(result, step)
            elif action == "sort_columns":
                result = self.ops.sort_columns(result)
            elif action == "transpose":
                result = self.ops.transpose(result)
            elif action == "remove_blank_strings":
                result = self.ops.remove_blank_strings(result)
            elif action == "memory_usage":
                result = self.ops.memory_usage(result)
            elif action == "describe":
                result = self.ops.describe(result)
            elif action == "corr":
                result = self.ops.corr(result)
            elif action == "auto_analyze":
                result = self.ops.auto_analyze(result)
            elif action == "auto_profile":
                result = self.ops.auto_profile(result)
            elif action == "ai_recommendations":
                result = self.ops.ai_recommendations(result)
            elif action == "duplicate_columns_summary":
                result = self.ops.duplicate_columns_summary(result)
            elif action == "column_cardinality":
                result = self.ops.column_cardinality(result)
            elif action == "suggest_charts":
                result = self.ops.suggest_charts(result)
            elif action == "numeric_summary":
                result = self.ops.numeric_summary(result)
            elif action == "text_summary":
                result = self.ops.text_summary(result)
            elif action == "detect_phone_columns":
                result = self.ops.detect_phone_columns(result)
            elif action == "detect_email_columns":
                result = self.ops.detect_email_columns(result)
            elif action == "detect_date_columns":
                result = self.ops.detect_date_columns(result)
            elif action == "dataframe_info":
                result = self.ops.dataframe_info(result)
            elif action == "smart_report":
                result = self.ops.smart_report(result)
            elif action == "top_null_columns":
                result = self.ops.top_null_columns(result, step.get("count", 10))
            elif action == "top_duplicate_values":
                result = self.top_duplicate_values(result, step)
            elif action == "longest_text":
                result = self.longest_text(result, step)
            elif action == "detect_currency_columns":
                result = self.ops.detect_currency_columns(result)
            elif action == "detect_id_columns":
                result = self.ops.detect_id_columns(result)
            elif action == "dataset_health":
                result = self.ops.dataset_health(result)
            elif action == "column_lengths":
                result = self.ops.column_lengths(result)
            elif action == "ai_dataset_score":
                result = self.ops.ai_dataset_score(result)
            elif action == "ai_find_problems":
                result = self.ops.ai_find_problems(result)
            elif action == "ai_best_chart":
                result = self.ops.ai_best_chart(result)
            elif action == "ai_insights":
                result = self.ops.ai_insights(result)
            elif action == "ai_missing_columns":
                result = self.ops.ai_missing_columns(result)
            elif action == "ai_column_score":
                result = self.ops.ai_column_score(result)
            elif action == "ai_auto_fix":
                result = self.ops.ai_auto_fix(result)
            elif action == "ai_detect_column_types":
                result = self.ops.ai_detect_column_types(result)
            elif action == "ai_empty_rows":
                result = self.ops.ai_empty_rows(result)
            elif action == "ai_duplicate_report":
                result = self.ops.ai_duplicate_report(result)
            elif action == "ai_business_summary":
                result = self.ops.ai_business_summary(result)
            elif action == "ai_column_relationships":
                result = self.ops.ai_column_relationships(result)
            elif action == "ai_top_categories":
                result = self.ai_top_categories(result, step)
            elif action == "ai_bottom_categories":
                result = self.ai_bottom_categories(result, step)
            elif action == "ai_generate_sql":
                result = self.ops.ai_generate_sql(result)
            elif action == "ai_column_dictionary":
                result = self.ops.ai_column_dictionary(result)
            elif action == "ai_detect_primary_key":
                result = self.ops.ai_detect_primary_key(result)
            elif action == "ai_detect_empty_columns":
                result = self.ops.ai_detect_empty_columns(result)
            elif action == "ai_dashboard_summary":
                result = self.ops.ai_dashboard_summary(result)
            elif action == "ai_kpi":
                result = self.ai_kpi(result, step)
            elif action == "ai_find_anomalies":
                result = self.ai_find_anomalies(result, step)
            elif action == "ai_duplicate_cells":
                result = self.ai_duplicate_cells(result, step)
            elif action == "ai_clean_column_names":
                result = self.ops.ai_clean_column_names(result)
            elif action == "ai_remove_full_duplicates":
                result = self.ops.ai_remove_full_duplicates(result)
            elif action == "ai_sort_all_columns":
                result = self.ops.ai_sort_all_columns(result)
            elif action == "ai_detect_boolean_columns":
                result = self.ops.ai_detect_boolean_columns(result)
            elif action == "ai_column_summary":
                result = self.ops.ai_column_summary(result)
            elif action == "ai_detect_currency":
                result = self.ai_detect_currency(result, step)
            elif action == "ai_text_statistics":
                result = self.ai_text_statistics(result, step)
            elif action == "ai_numeric_statistics":
                result = self.ai_numeric_statistics(result, step)
            elif action == "ai_export_json":
                result = self.ops.ai_export_json(result)

            # ========== YENİ ACTION: execute_python ==========
            elif action == "execute_python":
                result = self.execute_python(result, step)

            # ========== YENİ ACTION: merge ==========
            elif action == "merge":
                result = self.merge(result, step)

        return result

    #########################################################

    def find(self, column, df):
        real = self.matcher.match(column, list(df.columns))
        if real is None:
            raise Exception(f"Kolon bulunamadı : {column}")
        return real

    #########################################################

    def filter(self, df, step):
        return self.ops.filter_rows(
            df,
            self.find(step["column"], df),
            step["operator"],
            step["value"]
        )

    def sort(self, df, step):
        return self.ops.sort(
            df,
            self.find(step["column"], df),
            step.get("ascending", True)
        )

    def group_sum(self, df, step):
        return self.ops.group_sum(
            df,
            self.find(step["group_column"], df),
            self.find(step["value_column"], df)
        )

    def group_count(self, df, step):
        return self.ops.group_count(
            df,
            self.find(step["group_column"], df)
        )

    def delete_column(self, df, step):
        return self.ops.delete_column(
            df,
            self.find(step["column"], df)
        )

    def rename_column(self, df, step):
        return self.ops.rename_column(
            df,
            self.find(step["old_name"], df),
            step["new_name"]
        )

    def replace(self, df, step):
        return self.ops.replace(
            df,
            self.find(step["column"], df),
            step["old_value"],
            step["new_value"]
        )

    def fill_empty(self, df, step):
        return self.ops.fill_empty(
            df,
            self.find(step["column"], df),
            step["value"]
        )

    def unique(self, df, step):
        return self.ops.unique(
            df,
            self.find(step["column"], df)
        )

    def value_counts(self, df, step):
        return self.ops.value_counts(
            df,
            self.find(step["column"], df)
        )

    def keep_columns(self, df, step):
        cols = []
        for c in step["columns"]:
            cols.append(self.find(c, df))
        return self.ops.keep_columns(df, cols)

    def remove_columns(self, df, step):
        cols = []
        for c in step["columns"]:
            cols.append(self.find(c, df))
        return self.ops.remove_columns(df, cols)

    def merge_columns(self, df, step):
        return self.ops.merge_columns(
            df,
            self.find(step["column1"], df),
            self.find(step["column2"], df),
            step["new_column"]
        )

    def pivot(self, df, step):
        return self.ops.pivot(
            df,
            self.find(step["index"], df),
            self.find(step["values"], df),
            step.get("aggfunc", "sum")
        )

    def calculate(self, df, step):
        column = self.find(step["column"], df)
        value = self.ops.calculate(df, column, step["operation"])
        return pd.DataFrame({step["operation"]: [value]})

    def add_column(self, df, step):
        return self.ops.add_column(
            df,
            step["column"],
            step.get("default", "")
        )

    def remove_rows(self, df, step):
        return self.ops.remove_rows(
            df,
            self.find(step["column"], df),
            step["value"]
        )

    def top_duplicate_values(self, df, step):
        return self.ops.top_duplicate_values(
            df,
            self.find(step["column"], df),
            step.get("count", 20)
        )

    def longest_text(self, df, step):
        return self.ops.longest_text(
            df,
            self.find(step["column"], df),
            step.get("count", 20)
        )

    def ai_top_categories(self, df, step):
        return self.ops.ai_top_categories(
            df,
            self.find(step["column"], df),
            step.get("count", 10)
        )

    def ai_bottom_categories(self, df, step):
        return self.ops.ai_bottom_categories(
            df,
            self.find(step["column"], df),
            step.get("count", 10)
        )

    def ai_kpi(self, df, step):
        return self.ops.ai_kpi(
            df,
            self.find(step["column"], df)
        )

    def ai_find_anomalies(self, df, step):
        return self.ops.ai_find_anomalies(
            df,
            self.find(step["column"], df)
        )

    def ai_duplicate_cells(self, df, step):
        return self.ops.ai_duplicate_cells(
            df,
            self.find(step["column"], df)
        )

    def ai_detect_currency(self, df, step):
        return self.ops.ai_detect_currency(
            df,
            self.find(step["column"], df)
        )

    def ai_text_statistics(self, df, step):
        return self.ops.ai_text_statistics(
            df,
            self.find(step["column"], df)
        )

    def ai_numeric_statistics(self, df, step):
        return self.ops.ai_numeric_statistics(
            df,
            self.find(step["column"], df)
        )

    #########################################################
    # YENİ MERGE METODU
    #########################################################

    def merge(self, df, step):
        """İki DataFrame'i birleştirir (VLOOKUP işlevi görür)."""
        kaynak_df = st.session_state.get("kaynak_df")
        if kaynak_df is None:
            raise Exception("Kaynak dosya yüklenmemiş! Lütfen önce kaynak dosyayı yükleyin.")

        left_on = step.get("left_on")
        right_on = step.get("right_on")
        columns = step.get("columns", [])
        how = step.get("how", "left")

        if not left_on or not right_on:
            raise Exception("left_on ve right_on belirtilmeli!")

        # Kaynak DataFrame'den sadece gerekli sütunları al
        if columns:
            # right_on sütununu da ekle
            kaynak_subset = kaynak_df[[right_on] + columns]
        else:
            kaynak_subset = kaynak_df

        # Birleştir
        merged = df.merge(kaynak_subset, left_on=left_on, right_on=right_on, how=how)

        # right_on sütununu temizle (eğer left_on ile aynı değilse)
        if right_on in merged.columns and right_on != left_on:
            merged = merged.drop(columns=[right_on])

        return merged

    #########################################################
    # YENİ EXECUTE_PYTHON METODU
    #########################################################

    def execute_python(self, df, step):
        """Kullanıcı tarafından istenen özel Python kodunu çalıştırır."""
        warnings.filterwarnings('ignore')

        code = step.get("code", "")
        if not code:
            raise Exception("Python kodu boş!")

        # Çalışma ortamı
        local_vars = {
            "df": df,
            "pd": pd,
            "np": np,
            "st": st,
            "kaynak_df": st.session_state.get("kaynak_df", None)
        }

        try:
            # Kodu çalıştır
            exec(code, {}, local_vars)
            # Sonuçta 'result' değişkeni olmalı
            if "result" in local_vars:
                result_df = local_vars["result"]
                if isinstance(result_df, pd.DataFrame):
                    return result_df
                else:
                    raise Exception("Kod sonucu bir pandas DataFrame olmalı!")
            else:
                raise Exception("Kod sonunda 'result' değişkeni tanımlanmamış!")
        except Exception as e:
            raise Exception(f"Python kodu çalıştırılırken hata: {str(e)}")