import pandas as pd
import streamlit as st
import io

# Streamlit UI
st.title("BTI & BTR COMPARISON")
st.write("Upload two or four Excel files to compare unmatched records.")

# Upload files
file_a = st.file_uploader("Upload AX BTI File", type=["xlsx", "csv"])
file_b = st.file_uploader("Upload POS BTI File", type=["xlsx", "csv"])
file_c = st.file_uploader("Upload AX BTR File", type=["xlsx", "csv"])
file_d = st.file_uploader("Upload POS BTR File", type=["xlsx", "csv"])

# Function to read uploaded files
def read_file(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file, dtype=str, encoding='ISO-8859-1')
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file, dtype=str)
    else:
        st.error("Unsupported file format. Please upload CSV or Excel files.")
        return None

# Comparison function
def compare_files(df1, column1, df2, column2):
    if df1 is None or df2 is None:
        return None, None

    df1[column1] = df1[column1].str.strip().str.upper()
    df2[column2] = df2[column2].str.strip().str.upper()

    unmatched_1_to_2 = df1[~df1[column1].isin(df2[column2])]
    unmatched_2_to_1 = df2[~df2[column2].isin(df1[column1])]

    return unmatched_1_to_2, unmatched_2_to_1

# Process and Compare
if st.button("Compare Files"):
    results = {}
    
    # Process AX vs POS BTI if both files are uploaded
    if file_a and file_b:
        df_a = read_file(file_a)
        df_b = read_file(file_b)
        unmatched_a_to_b, unmatched_b_to_a = compare_files(df_a, 'referencedocno', df_b, 'TRNO')
        results["BTI MISSING POS"] = unmatched_a_to_b
        results["BTI MISSING AX"] = unmatched_b_to_a
    
    # Process AX vs POS BTR if both files are uploaded
    if file_c and file_d:
        df_c = read_file(file_c)
        df_d = read_file(file_d)
        unmatched_c_to_d, unmatched_d_to_c = compare_files(df_c, 'referencedocno', df_d, 'TRNO')
        results["BTR MISSING POS"] = unmatched_c_to_d
        results["BTR MISSING AX"] = unmatched_d_to_c
    
    if results:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in results.items():
                if df is not None and not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)

        # Download button
        st.download_button(
            label="📥 Download Comparison Results",
            data=output,
            file_name="comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("Comparison completed! Click the button above to download the results.")
    else:
        st.error("Please upload at least two files (AX vs POS BTI or AX vs POS BTR) to compare.")
