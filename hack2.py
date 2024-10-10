import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime

# Function to calculate time differences in minutes
def calculate_minutes(start_time, end_time):
    time_format = "%m/%d/%Y %H:%M"
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)
    return (end - start).total_seconds() / 60.0

# CALculation and analysis fucntion
def perform_analysis():
    try:
        sentiment_df = pd.read_csv(sentiment_file_path)
        reason_df = pd.read_csv(reason_file_path)
        customers_df = pd.read_csv(customers_file_path)
        calls_df = pd.read_csv(calls_file_path)

        # Merge the dataframes
        merged_df = calls_df.merge(sentiment_df, on='call_id', how='left') \
                            .merge(reason_df, on='call_id', how='left') \
                            .merge(customers_df, on='customer_id', how='left')

        # Calculate AHT and AST
        merged_df['AHT'] = merged_df.apply(lambda row: calculate_minutes(row['agent_assigned_datetime'], row['call_end_datetime']), axis=1)
        merged_df['AST'] = merged_df.apply(lambda row: calculate_minutes(row['call_start_datetime'], row['agent_assigned_datetime']), axis=1)

        # Group by call reasons to get average AHT and AST
        aht_ast_by_reason = merged_df.groupby('primary_call_reason')[['AHT', 'AST']].mean().reset_index()

        # count of each call reason
        call_reason_counts = merged_df['primary_call_reason'].value_counts().reset_index()
        call_reason_counts.columns = ['primary_call_reason', 'count']

        # Merge with AHT/AST data
        aht_ast_with_counts = aht_ast_by_reason.merge(call_reason_counts, on='primary_call_reason')

        # Find the most and least frequent call reasons
        most_frequent_reason = aht_ast_with_counts.loc[aht_ast_with_counts['count'].idxmax()]
        least_frequent_reason = aht_ast_with_counts.loc[aht_ast_with_counts['count'].idxmin()]

        # Calculate percentage difference in AHT
        percentage_diff_aht = ((most_frequent_reason['AHT'] - least_frequent_reason['AHT']) / least_frequent_reason['AHT']) * 100

        # printing
        messagebox.showinfo("Analysis Complete", f"Most Frequent Call Reason: {most_frequent_reason['primary_call_reason']} with AHT: {most_frequent_reason['AHT']}\n"
                                                 f"Least Frequent Call Reason: {least_frequent_reason['primary_call_reason']} with AHT: {least_frequent_reason['AHT']}\n"
                                                 f"Percentage Difference in AHT: {percentage_diff_aht:.2f}%")
    except Exception as e:
        messagebox.showerror("Error", f"Ohhooo! An error occurred during analysis: {str(e)}")

# File selection functions
def select_sentiment_file():
    global sentiment_file_path
    sentiment_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    sentiment_label.config(text=sentiment_file_path)

def select_reason_file():
    global reason_file_path
    reason_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    reason_label.config(text=reason_file_path)

def select_customers_file():
    global customers_file_path
    customers_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    customers_label.config(text=customers_file_path)

def select_calls_file():
    global calls_file_path
    calls_file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    calls_label.config(text=calls_file_path)


app = tk.Tk()
app.title("Call Center Data Analysis Tool")

# Instructions
instruction_label = tk.Label(app, text="Select all required CSV files for analysis:")
instruction_label.pack()

# file selection buttons
sentiment_button = tk.Button(app, text="Select Sentiment File", command=select_sentiment_file)
sentiment_button.pack()
sentiment_label = tk.Label(app, text="No file selected")
sentiment_label.pack()

reason_button = tk.Button(app, text="Select Reason File", command=select_reason_file)
reason_button.pack()
reason_label = tk.Label(app, text="No file selected")
reason_label.pack()

customers_button = tk.Button(app, text="Select Customers File", command=select_customers_file)
customers_button.pack()
customers_label = tk.Label(app, text="No file selected")
customers_label.pack()

calls_button = tk.Button(app, text="Select Calls File", command=select_calls_file)
calls_button.pack()
calls_label = tk.Label(app, text="No file selected")
calls_label.pack()

# Analysis button
analyze_button = tk.Button(app, text="Perform Analysis", command=perform_analysis)
analyze_button.pack()

# Run the application
app.mainloop()
