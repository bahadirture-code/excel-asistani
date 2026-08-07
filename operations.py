####################################################

def pivot(
    self,
    df,
    index,
    values,
    aggfunc="sum"
):

    return df.pivot_table(

        index=index,

        values=values,

        aggfunc=aggfunc

    ).reset_index()

####################################################

def merge_dataframes(
    self,
    left_df,
    right_df,
    left_key,
    right_key,
    how="inner"
):

    return left_df.merge(

        right_df,

        left_on=left_key,

        right_on=right_key,

        how=how

    )

####################################################

def remove_rows(
    self,
    df,
    column,
    value
):

    return df[

        df[column] != value

    ]

####################################################

def add_column(
    self,
    df,
    column,
    default_value=""
):

    df=df.copy()

    df[column]=default_value

    return df

####################################################

def calculate(
    self,
    df,
    column,
    operation
):

    if operation=="sum":

        return df[column].sum()

    if operation=="mean":

        return df[column].mean()

    if operation=="max":

        return df[column].max()

    if operation=="min":

        return df[column].min()

    if operation=="count":

        return df[column].count()

    raise Exception("Desteklenmeyen hesaplama")
####################################################

def create_formula_column(
    self,
    df,
    new_column,
    formula
):

    df = df.copy()

    df[new_column] = df.eval(formula)

    return df

####################################################

def convert_dtype(
    self,
    df,
    column,
    dtype
):

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

####################################################

def fill_forward(
    self,
    df
):

    return df.ffill()

####################################################

def fill_backward(
    self,
    df
):

    return df.bfill()

####################################################

def remove_null_columns(
    self,
    df
):

    return df.dropna(axis=1, how="all")

####################################################

def uppercase(
    self,
    df,
    column
):

    df=df.copy()

    df[column]=df[column].astype(str).str.upper()

    return df

####################################################

def lowercase(
    self,
    df,
    column
):

    df=df.copy()

    df[column]=df[column].astype(str).str.lower()

    return df

####################################################

def trim(
    self,
    df,
    column
):

    df=df.copy()

    df[column]=df[column].astype(str).str.strip()

    return df

####################################################

def remove_spaces(
    self,
    df,
    column
):

    df=df.copy()

    df[column]=df[column].astype(str).str.replace(
        " ",
        "",
        regex=False
    )

    return df
####################################################

def split_column(
    self,
    df,
    column,
    separator,
    new_columns
):

    df = df.copy()

    parts = df[column].astype(str).str.split(
        separator,
        expand=True
    )

    for i, col in enumerate(new_columns):

        if i < parts.shape[1]:
            df[col] = parts[i]

    return df

####################################################

def concat_columns(
    self,
    df,
    columns,
    new_column,
    separator=" "
):

    df = df.copy()

    df[new_column] = df[columns].astype(str).agg(
        separator.join,
        axis=1
    )

    return df

####################################################

def sort_multiple(
    self,
    df,
    columns,
    ascending=True
):

    return df.sort_values(
        by=columns,
        ascending=ascending
    )

####################################################

def remove_negative(
    self,
    df,
    column
):

    return df[
        df[column] >= 0
    ]

####################################################

def remove_zero(
    self,
    df,
    column
):

    return df[
        df[column] != 0
    ]

####################################################

def percentage_column(
    self,
    df,
    column,
    new_column
):

    df=df.copy()

    total=df[column].sum()

    df[new_column]=(

        df[column]

        / total

    ) * 100

    return df

####################################################

def round_column(
    self,
    df,
    column,
    digits
):

    df=df.copy()

    df[column]=df[column].round(digits)

    return df
####################################################

def filter_between(
    self,
    df,
    column,
    min_value,
    max_value
):

    return df[
        (df[column] >= min_value) &
        (df[column] <= max_value)
    ]

####################################################

def top(
    self,
    df,
    count
):

    return df.head(count)

####################################################

def bottom(
    self,
    df,
    count
):

    return df.tail(count)

####################################################

def sample(
    self,
    df,
    count
):

    return df.sample(count)

####################################################

def remove_text(
    self,
    df,
    column,
    text
):

    df=df.copy()

    df[column]=df[column].astype(str).str.replace(
        text,
        "",
        regex=False
    )

    return df

####################################################

def add_text(
    self,
    df,
    column,
    text,
    position="end"
):

    df=df.copy()

    if position=="start":

        df[column]=text+df[column].astype(str)

    else:

        df[column]=df[column].astype(str)+text

    return df

####################################################

def sort_index(
    self,
    df
):

    return df.sort_index()

####################################################

def reset_index(
    self,
    df
):

    return df.reset_index(drop=True)

####################################################

def reverse(
    self,
    df
):

    return df.iloc[::-1].reset_index(drop=True)
####################################################

def detect_outliers(
    self,
    df,
    column
):

    q1 = df[column].quantile(0.25)

    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    low = q1 - 1.5 * iqr

    high = q3 + 1.5 * iqr

    return df[
        (df[column] < low) |
        (df[column] > high)
    ]

####################################################

def remove_outliers(
    self,
    df,
    column
):

    q1 = df[column].quantile(0.25)

    q3 = df[column].quantile(0.75)

    iqr = q3 - q1

    low = q1 - 1.5 * iqr

    high = q3 + 1.5 * iqr

    return df[
        (df[column] >= low) &
        (df[column] <= high)
    ]

####################################################

def duplicate_rows(
    self,
    df
):

    return df[
        df.duplicated(
            keep=False
        )
    ]

####################################################

def null_summary(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "Column":df.columns,

        "Null Count":df.isna().sum().values,

        "Null %":(

            df.isna().sum()

            / len(df)

            *100

        ).round(2)

    })

####################################################

def column_info(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Type":str(df[c].dtype),

            "Unique":df[c].nunique(),

            "Null":df[c].isna().sum()

        })

    return pd.DataFrame(rows)

####################################################

def frequency_table(
    self,
    df,
    column
):

    return (

        df[column]

        .value_counts(dropna=False)

        .reset_index()

    )
####################################################

def find_replace_all(
    self,
    df,
    old_value,
    new_value
):

    return df.replace(
        old_value,
        new_value
    )

####################################################

def sort_columns(
    self,
    df
):

    return df.reindex(
        sorted(df.columns),
        axis=1
    )

####################################################

def transpose(
    self,
    df
):

    return df.T.reset_index()

####################################################

def remove_blank_strings(
    self,
    df
):

    return df.replace(
        r'^\s*$',
        pd.NA,
        regex=True
    ).dropna(how="all")

####################################################

def memory_usage(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "Column":df.columns,

        "Memory(Bytes)":[

            df[c].memory_usage(deep=True)

            for c in df.columns

        ]

    })

####################################################

def dtypes(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "Column":df.columns,

        "Type":[

            str(df[c].dtype)

            for c in df.columns

        ]

    })

####################################################

def correlation(
    self,
    df
):

    return df.corr(numeric_only=True)

####################################################

def remove_constant_columns(
    self,
    df
):

    return df.loc[
        :,
        df.nunique()>1
    ]

####################################################

def duplicate_columns(
    self,
    df
):

    return df.T[
        df.T.duplicated(
            keep=False
        )
    ].T
####################################################

def create_ai_summary(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Type":str(df[c].dtype),

            "Null":int(df[c].isna().sum()),

            "Unique":int(df[c].nunique()),

            "Min":str(df[c].min()) if str(df[c].dtype)!="object" else "",

            "Max":str(df[c].max()) if str(df[c].dtype)!="object" else ""

        })

    return pd.DataFrame(rows)

####################################################

def search_text(

    self,

    df,

    text

):

    import pandas as pd

    mask=pd.Series(False,index=df.index)

    for c in df.columns:

        mask|=df[c].astype(str).str.contains(

            text,

            case=False,

            na=False

        )

    return df[mask]

####################################################

def filter_null(

    self,

    df,

    column

):

    return df[

        df[column].isna()

    ]

####################################################

def filter_not_null(

    self,

    df,

    column

):

    return df[

        df[column].notna()

    ]
####################################################

def auto_clean(
    self,
    df
):

    df = df.copy()

    df = df.drop_duplicates()

    df = df.replace(
        r'^\s*$',
        pd.NA,
        regex=True
    )

    df = df.dropna(
        how="all"
    )

    for c in df.columns:

        if str(df[c].dtype) == "object":

            df[c] = (
                df[c]
                .astype(str)
                .str.strip()
            )

    return df

####################################################

def remove_empty_columns(
    self,
    df
):

    return df.dropna(
        axis=1,
        how="all"
    )

####################################################

def column_statistics(
    self,
    df,
    column
):

    import pandas as pd

    s = df[column]

    return pd.DataFrame({

        "count":[s.count()],

        "null":[s.isna().sum()],

        "unique":[s.nunique()],

        "min":[s.min()],

        "max":[s.max()]

    })

####################################################

def random_rows(
    self,
    df,
    count
):

    return df.sample(

        min(

            count,

            len(df)

        ),

        random_state=42

    )
####################################################

def smart_filter(
    self,
    df,
    column,
    value
):

    s = df[column]

    if str(s.dtype).startswith(("int", "float")):

        try:

            value = float(value)

            return df[s == value]

        except:

            pass

    return df[
        s.astype(str)
        .str.contains(
            str(value),
            case=False,
            na=False
        )
    ]

####################################################

def smart_sort(
    self,
    df,
    column
):

    try:

        return df.sort_values(
            by=column,
            key=lambda x: pd.to_numeric(
                x,
                errors="ignore"
            )
        )

    except:

        return df.sort_values(
            by=column
        )

####################################################

def duplicate_summary(
    self,
    df
):

    import pandas as pd

    d = df.duplicated()

    return pd.DataFrame({

        "Toplam Satır":[len(df)],

        "Tekrar Eden":[int(d.sum())],

        "Tekil":[int(len(df)-d.sum())]

    })

####################################################

def empty_summary(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Empty":int(df[c].isna().sum())

        })

    return pd.DataFrame(rows)

####################################################

def data_quality(
    self,
    df
):

    import pandas as pd

    rows=[]

    total=len(df)

    for c in df.columns:

        rows.append({

            "Column":c,

            "Null":int(df[c].isna().sum()),

            "Unique":int(df[c].nunique()),

            "Duplicate":int(df[c].duplicated().sum()),

            "Fill Rate":round(

                (1-df[c].isna().sum()/total)*100,

                2

            )

        })

    return pd.DataFrame(rows)
####################################################

def auto_detect_date_columns(
    self,
    df
):

    df=df.copy()

    for c in df.columns:

        try:

            converted=pd.to_datetime(
                df[c],
                errors="raise"
            )

            df[c]=converted

        except:

            pass

    return df

####################################################

def auto_detect_numeric(
    self,
    df
):

    df=df.copy()

    for c in df.columns:

        try:

            df[c]=pd.to_numeric(

                df[c],

                errors="ignore"

            )

        except:

            pass

    return df

####################################################

def auto_optimize(
    self,
    df
):

    df=self.auto_detect_numeric(df)

    df=self.auto_detect_date_columns(df)

    return df

####################################################

def top_values(
    self,
    df,
    column,
    count=10
):

    return (

        df[column]

        .value_counts()

        .head(count)

        .reset_index()

    )

####################################################

def bottom_values(
    self,
    df,
    column,
    count=10
):

    return (

        df[column]

        .value_counts()

        .tail(count)

        .reset_index()

    )

####################################################

def detect_numeric_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Numeric":pd.api.types.is_numeric_dtype(

                df[c]

            )

        })

    return pd.DataFrame(rows)
####################################################

def auto_analyze(
    self,
    df
):

    import pandas as pd

    rows=[]

    total_rows=len(df)

    total_columns=len(df.columns)

    duplicate_rows=int(df.duplicated().sum())

    empty_cells=int(df.isna().sum().sum())

    numeric_columns=[]

    text_columns=[]

    date_columns=[]

    for c in df.columns:

        if pd.api.types.is_numeric_dtype(df[c]):

            numeric_columns.append(c)

        elif pd.api.types.is_datetime64_any_dtype(df[c]):

            date_columns.append(c)

        else:

            text_columns.append(c)

    summary={

        "Toplam Satır":[total_rows],

        "Toplam Kolon":[total_columns],

        "Boş Hücre":[empty_cells],

        "Tekrar Eden Satır":[duplicate_rows],

        "Sayısal Kolon":[len(numeric_columns)],

        "Metin Kolonu":[len(text_columns)],

        "Tarih Kolonu":[len(date_columns)]

    }

    return pd.DataFrame(summary)

####################################################

def auto_profile(
    self,
    df
):

    import pandas as pd

    result=[]

    for c in df.columns:

        result.append({

            "Column":c,

            "Type":str(df[c].dtype),

            "Null":int(df[c].isna().sum()),

            "Unique":int(df[c].nunique()),

            "Duplicate":int(df[c].duplicated().sum()),

            "Example":str(df[c].dropna().head(1).tolist())

        })

    return pd.DataFrame(result)
####################################################

def ai_recommendations(
    self,
    df
):

    import pandas as pd

    recommendations=[]

    if df.duplicated().sum()>0:

        recommendations.append(
            "Tekrar eden satırlar bulundu."
        )

    if df.isna().sum().sum()>0:

        recommendations.append(
            "Boş hücreler bulundu."
        )

    for c in df.columns:

        if df[c].nunique()==1:

            recommendations.append(
                f"{c} kolonu tek değerden oluşuyor."
            )

    numeric=df.select_dtypes(include="number").columns

    if len(numeric)==0:

        recommendations.append(
            "Sayısal kolon bulunamadı."
        )

    if len(recommendations)==0:

        recommendations.append(
            "Veri kalitesi iyi görünüyor."
        )

    return pd.DataFrame({

        "Öneriler":recommendations

    })

####################################################

def duplicate_columns_summary(
    self,
    df
):

    import pandas as pd

    duplicated=[]

    cols=list(df.columns)

    for i in range(len(cols)):

        for j in range(i+1,len(cols)):

            if df[cols[i]].equals(df[cols[j]]):

                duplicated.append({

                    "Column1":cols[i],

                    "Column2":cols[j]

                })

    return pd.DataFrame(duplicated)

####################################################

def column_cardinality(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Unique":int(df[c].nunique()),

            "Total":len(df),

            "Cardinality %":round(

                df[c].nunique()/len(df)*100,

                2

            )

        })

    return pd.DataFrame(rows)
####################################################

def suggest_charts(
    self,
    df
):

    import pandas as pd

    charts=[]

    numeric=df.select_dtypes(include="number").columns.tolist()

    text=[]

    for c in df.columns:

        if c not in numeric:

            text.append(c)

    if len(text)>0 and len(numeric)>0:

        charts.append({

            "Chart":"Bar",

            "X":text[0],

            "Y":numeric[0]

        })

        charts.append({

            "Chart":"Line",

            "X":text[0],

            "Y":numeric[0]

        })

    if len(numeric)>=2:

        charts.append({

            "Chart":"Scatter",

            "X":numeric[0],

            "Y":numeric[1]

        })

    if len(text)>0:

        charts.append({

            "Chart":"Pie",

            "X":text[0],

            "Y":numeric[0] if len(numeric)>0 else ""

        })

    return pd.DataFrame(charts)

####################################################

def numeric_summary(
    self,
    df
):

    return df.describe().T.reset_index()

####################################################

def text_summary(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.select_dtypes(include="object").columns:

        rows.append({

            "Column":c,

            "Unique":df[c].nunique(),

            "Longest":df[c].astype(str).str.len().max(),

            "Shortest":df[c].astype(str).str.len().min()

        })

    return pd.DataFrame(rows)
####################################################

def detect_phone_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    keywords=[

        "telefon",

        "phone",

        "gsm",

        "cep",

        "mobile"

    ]

    for c in df.columns:

        found=False

        for k in keywords:

            if k in str(c).lower():

                found=True

        rows.append({

            "Column":c,

            "Phone Column":found

        })

    return pd.DataFrame(rows)

####################################################

def detect_email_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    keywords=[

        "mail",

        "email",

        "e-mail"

    ]

    for c in df.columns:

        found=False

        for k in keywords:

            if k in str(c).lower():

                found=True

        rows.append({

            "Column":c,

            "Email Column":found

        })

    return pd.DataFrame(rows)

####################################################

def detect_date_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Date":

            pd.api.types.is_datetime64_any_dtype(

                df[c]

            )

        })

    return pd.DataFrame(rows)

####################################################

def dataframe_info(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "Rows":[len(df)],

        "Columns":[len(df.columns)],

        "Memory(MB)":[

            round(

                df.memory_usage(

                    deep=True

                ).sum()/1024/1024,

                2

            )

        ]

    })
####################################################

def smart_report(
    self,
    df
):

    import pandas as pd

    numeric=df.select_dtypes(include="number")

    report={}

    report["Toplam Satır"]=len(df)
    report["Toplam Kolon"]=len(df.columns)
    report["Boş Hücre"]=int(df.isna().sum().sum())
    report["Tekrar Eden Satır"]=int(df.duplicated().sum())

    if len(numeric.columns)>0:

        report["Sayısal Kolon"]=len(numeric.columns)
        report["Toplam Sayısal Değer"]=numeric.sum().sum()

    return pd.DataFrame([report])

####################################################

def top_null_columns(
    self,
    df,
    count=10
):

    import pandas as pd

    s=df.isna().sum()

    return (

        s

        .sort_values(

            ascending=False

        )

        .head(count)

        .reset_index()

        .rename(

            columns={

                "index":"Column",

                0:"Null"

            }

        )

    )

####################################################

def top_duplicate_values(
    self,
    df,
    column,
    count=20
):

    return (

        df[column]

        .value_counts()

        .head(count)

        .reset_index()

    )

####################################################

def longest_text(
    self,
    df,
    column,
    count=20
):

    x=df.copy()

    x["__LEN__"]=x[column].astype(str).str.len()

    return (

        x

        .sort_values(

            "__LEN__",

            ascending=False

        )

        .head(count)

        .drop(

            columns="__LEN__"

        )

    )
####################################################

def detect_currency_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    keywords=[

        "fiyat",
        "price",
        "ücret",
        "ucret",
        "tutar",
        "amount",
        "toplam",
        "total",
        "satış",
        "satis",
        "gelir",
        "income"

    ]

    for c in df.columns:

        found=False

        for k in keywords:

            if k in str(c).lower():

                found=True

        rows.append({

            "Column":c,

            "Currency":found

        })

    return pd.DataFrame(rows)

####################################################

def detect_id_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    keywords=[

        "id",

        "kod",

        "code",

        "tc",

        "kimlik",

        "uuid"

    ]

    for c in df.columns:

        found=False

        for k in keywords:

            if k in str(c).lower():

                found=True

        rows.append({

            "Column":c,

            "ID":found

        })

    return pd.DataFrame(rows)

####################################################

def dataset_health(
    self,
    df
):

    import pandas as pd

    total=len(df)

    score=100

    score-=min(

        40,

        int(

            df.isna().sum().sum()

        )

    )

    score-=min(

        30,

        int(

            df.duplicated().sum()

        )

    )

    return pd.DataFrame({

        "Health Score":[

            max(score,0)

        ],

        "Rows":[total],

        "Columns":[len(df.columns)]

    })

####################################################

def column_lengths(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Max Length":

            df[c].astype(str).str.len().max(),

            "Average Length":

            round(

                df[c].astype(str).str.len().mean(),

                2

            )

        })

    return pd.DataFrame(rows)
####################################################

def ai_dataset_score(
    self,
    df
):

    import pandas as pd

    score = 100

    duplicate = int(df.duplicated().sum())

    nulls = int(df.isna().sum().sum())

    if duplicate > 0:
        score -= min(duplicate,20)

    if nulls > 0:
        score -= min(nulls,30)

    numeric = len(
        df.select_dtypes(include="number").columns
    )

    text = len(df.columns)-numeric

    return pd.DataFrame({

        "AI Score":[max(score,0)],

        "Rows":[len(df)],

        "Columns":[len(df.columns)],

        "Numeric":[numeric],

        "Text":[text],

        "Duplicates":[duplicate],

        "Null":[nulls]

    })

####################################################

def ai_find_problems(
    self,
    df
):

    import pandas as pd

    problems=[]

    for c in df.columns:

        if df[c].isna().sum()>0:

            problems.append({

                "Column":c,

                "Problem":"Null Values"

            })

        if df[c].duplicated().sum()>0:

            problems.append({

                "Column":c,

                "Problem":"Duplicate Values"

            })

        if df[c].nunique()==1:

            problems.append({

                "Column":c,

                "Problem":"Constant Column"

            })

    return pd.DataFrame(problems)

####################################################

def ai_best_chart(
    self,
    df
):

    import pandas as pd

    numeric=df.select_dtypes(include="number").columns.tolist()

    text=[]

    for c in df.columns:

        if c not in numeric:

            text.append(c)

    chart="Table"

    x=""

    y=""

    if len(text)>0 and len(numeric)>0:

        chart="Bar"

        x=text[0]

        y=numeric[0]

    elif len(numeric)>=2:

        chart="Scatter"

        x=numeric[0]

        y=numeric[1]

    return pd.DataFrame({

        "Chart":[chart],

        "X":[x],

        "Y":[y]

    })
####################################################

def ai_insights(
    self,
    df
):

    import pandas as pd

    insights=[]

    numeric=df.select_dtypes(include="number").columns

    for c in numeric:

        insights.append({

            "Column":c,

            "Average":round(df[c].mean(),2),

            "Median":round(df[c].median(),2),

            "Min":round(df[c].min(),2),

            "Max":round(df[c].max(),2),

            "Std":round(df[c].std(),2)

        })

    return pd.DataFrame(insights)

####################################################

def ai_missing_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    total=len(df)

    for c in df.columns:

        missing=df[c].isna().sum()

        rows.append({

            "Column":c,

            "Missing":int(missing),

            "Percent":round(

                missing/total*100,

                2

            )

        })

    return pd.DataFrame(rows)

####################################################

def ai_column_score(
    self,
    df
):

    import pandas as pd

    rows=[]

    total=len(df)

    for c in df.columns:

        score=100

        score-=min(

            50,

            int(df[c].isna().sum()/total*100)

        )

        score-=min(

            20,

            int(df[c].duplicated().sum()/total*100)

        )

        rows.append({

            "Column":c,

            "Score":max(score,0)

        })

    return pd.DataFrame(rows)
####################################################

def ai_auto_fix(
    self,
    df
):

    df=df.copy()

    df=df.drop_duplicates()

    df=df.replace(
        r'^\s*$',
        pd.NA,
        regex=True
    )

    df=df.dropna(
        how="all"
    )

    for c in df.columns:

        if str(df[c].dtype)=="object":

            df[c]=(

                df[c]

                .astype(str)

                .str.strip()

            )

    return df

####################################################

def ai_detect_column_types(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        dtype="Text"

        if pd.api.types.is_numeric_dtype(df[c]):

            dtype="Numeric"

        elif pd.api.types.is_datetime64_any_dtype(df[c]):

            dtype="Date"

        rows.append({

            "Column":c,

            "Detected":dtype

        })

    return pd.DataFrame(rows)

####################################################

def ai_empty_rows(
    self,
    df
):

    return df[

        df.isna()

        .all(axis=1)

    ]

####################################################

def ai_duplicate_report(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "Duplicate Rows":[

            int(

                df.duplicated().sum()

            )

        ],

        "Duplicate %":[

            round(

                df.duplicated().sum()/len(df)*100,

                2

            )

        ]

    })
####################################################

def ai_business_summary(
    self,
    df
):

    import pandas as pd

    summary=[]

    numeric=df.select_dtypes(include="number").columns

    for c in numeric:

        summary.append({

            "Metric":c,

            "Total":round(df[c].sum(),2),

            "Average":round(df[c].mean(),2),

            "Maximum":round(df[c].max(),2),

            "Minimum":round(df[c].min(),2)

        })

    return pd.DataFrame(summary)

####################################################

def ai_column_relationships(
    self,
    df
):

    import pandas as pd

    corr=df.corr(numeric_only=True)

    rows=[]

    cols=list(corr.columns)

    for i in range(len(cols)):

        for j in range(i+1,len(cols)):

            rows.append({

                "Column1":cols[i],

                "Column2":cols[j],

                "Correlation":round(

                    corr.iloc[i,j],

                    4

                )

            })

    return pd.DataFrame(rows)

####################################################

def ai_top_categories(
    self,
    df,
    column,
    count=10
):

    return (

        df[column]

        .value_counts()

        .head(count)

        .reset_index()

        .rename(

            columns={

                "index":"Category",

                column:"Count"

            }

        )

    )

####################################################

def ai_bottom_categories(
    self,
    df,
    column,
    count=10
):

    return (

        df[column]

        .value_counts()

        .tail(count)

        .reset_index()

        .rename(

            columns={

                "index":"Category",

                column:"Count"

            }

        )

    )
####################################################

def ai_generate_sql(
    self,
    df,
    table_name="data"
):

    import pandas as pd

    rows=[]

    type_map={

        "int64":"INTEGER",
        "float64":"REAL",
        "object":"TEXT",
        "bool":"BOOLEAN",
        "datetime64[ns]":"DATETIME"

    }

    for c in df.columns:

        dtype=str(df[c].dtype)

        sql_type=type_map.get(dtype,"TEXT")

        rows.append(

            f"{c} {sql_type}"

        )

    sql="CREATE TABLE "+table_name+" (\n"

    sql+=",\n".join(rows)

    sql+="\n);"

    return pd.DataFrame({

        "SQL":[sql]

    })

####################################################

def ai_column_dictionary(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Type":str(df[c].dtype),

            "Null":int(df[c].isna().sum()),

            "Unique":int(df[c].nunique()),

            "Example":str(

                df[c]

                .dropna()

                .head(1)

                .tolist()

            )

        })

    return pd.DataFrame(rows)

####################################################

def ai_detect_primary_key(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Primary Key Candidate":

            df[c].is_unique

        })

    return pd.DataFrame(rows)

####################################################

def ai_detect_empty_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Empty":

            df[c].isna().all()

        })

    return pd.DataFrame(rows)
####################################################

def ai_dashboard_summary(
    self,
    df
):

    import pandas as pd

    numeric=df.select_dtypes(include="number")

    result={

        "Rows":len(df),

        "Columns":len(df.columns),

        "Missing":int(df.isna().sum().sum()),

        "Duplicates":int(df.duplicated().sum())

    }

    for c in numeric.columns[:5]:

        result[f"{c} Toplam"]=round(

            numeric[c].sum(),

            2

        )

    return pd.DataFrame([result])

####################################################

def ai_kpi(
    self,
    df,
    column
):

    import pandas as pd

    s=df[column]

    return pd.DataFrame({

        "Sum":[round(s.sum(),2)],

        "Average":[round(s.mean(),2)],

        "Median":[round(s.median(),2)],

        "Maximum":[round(s.max(),2)],

        "Minimum":[round(s.min(),2)]

    })

####################################################

def ai_find_anomalies(
    self,
    df,
    column
):

    q1=df[column].quantile(.25)

    q3=df[column].quantile(.75)

    iqr=q3-q1

    low=q1-1.5*iqr

    high=q3+1.5*iqr

    return df[

        (df[column]<low)

        |

        (df[column]>high)

    ]

####################################################

def ai_duplicate_cells(
    self,
    df,
    column
):

    return df[

        df[column].duplicated(

            keep=False

        )

    ]
####################################################

def ai_clean_column_names(
    self,
    df
):

    df=df.copy()

    cols=[]

    for c in df.columns:

        c=str(c)

        c=c.strip()

        c=c.replace(" ","_")

        c=c.replace("-","_")

        c=c.replace("/","_")

        cols.append(c.upper())

    df.columns=cols

    return df

####################################################

def ai_remove_full_duplicates(
    self,
    df
):

    return df.drop_duplicates(
        keep="first"
    )

####################################################

def ai_sort_all_columns(
    self,
    df
):

    return df.reindex(
        sorted(df.columns),
        axis=1
    )

####################################################

def ai_detect_boolean_columns(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        u=df[c].dropna().unique()

        rows.append({

            "Column":c,

            "Boolean":

            len(u)<=2

        })

    return pd.DataFrame(rows)

####################################################

def ai_column_summary(
    self,
    df
):

    import pandas as pd

    rows=[]

    for c in df.columns:

        rows.append({

            "Column":c,

            "Type":str(df[c].dtype),

            "Rows":len(df),

            "Null":int(df[c].isna().sum()),

            "Unique":int(df[c].nunique())

        })

    return pd.DataFrame(rows)
####################################################

def ai_detect_currency(
    self,
    df,
    column
):

    import pandas as pd

    s=df[column].astype(str)

    rows=[]

    currency=[

        "₺",

        "$",

        "€",

        "£"

    ]

    for item in currency:

        rows.append({

            "Currency":item,

            "Count":int(

                s.str.contains(

                    item,

                    regex=False,

                    na=False

                ).sum()

            )

        })

    return pd.DataFrame(rows)

####################################################

def ai_text_statistics(
    self,
    df,
    column
):

    import pandas as pd

    s=df[column].astype(str)

    return pd.DataFrame({

        "Average Length":[

            round(

                s.str.len().mean(),

                2

            )

        ],

        "Maximum Length":[

            int(

                s.str.len().max()

            )

        ],

        "Minimum Length":[

            int(

                s.str.len().min()

            )

        ],

        "Unique":[

            int(

                s.nunique()

            )

        ]

    })

####################################################

def ai_numeric_statistics(
    self,
    df,
    column
):

    import pandas as pd

    s=df[column]

    return pd.DataFrame({

        "Sum":[s.sum()],

        "Average":[round(s.mean(),2)],

        "Median":[round(s.median(),2)],

        "Std":[round(s.std(),2)],

        "Variance":[round(s.var(),2)]

    })

####################################################

def ai_export_json(
    self,
    df
):

    import pandas as pd

    return pd.DataFrame({

        "JSON":[

            df.to_json(

                orient="records",

                force_ascii=False

            )

        ]

    })