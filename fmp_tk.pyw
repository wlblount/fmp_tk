# V 1.1.2  added fmp_earnSym() to the lineup 11/18/24

import tkinter as tk
from tkinter import scrolledtext, ttk
import fmp  # Assuming fmp.py contains functions like fmp_intra(), fmp_profF(), fmp_search()
from tabulate import tabulate
import pandas as pd


def update_window_for_function(*args):
    selected_function = function_selector.get()
    if selected_function == "Intraday Data":
        period_selector_label.pack(after=search_entry, pady=5)
        period_selector.pack(after=period_selector_label, pady=5)
    else:
        period_selector_label.pack_forget()
        period_selector.pack_forget()

def run_selected_function():
    # Clear previous content
    output_text.delete('1.0', tk.END)
    description_text.delete('1.0', tk.END)

    # Get the selected function and search term from the input fields
    selected_function = function_selector.get()
    search_string = search_entry.get()
    selected_period = period_selector.get()

    try:
        if selected_function == "Intraday Data":
            # Call the function for intraday data
            df = fmp.fmp_intra(search_string, period=selected_period)
            if not df.empty:
                # Format and display the data
                df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float).round(3).applymap(lambda x: f"{x:.3f}")
                df['volume'] = df['volume'].apply(lambda x: f"{int(x):,}").str.rjust(15)
                tabulated_result = tabulate(df, headers='keys', tablefmt='fancy_grid', numalign='left', stralign='left')
                output_text.insert(tk.END, tabulated_result)
            else:
                output_text.insert(tk.END, "No intraday data found for the given symbol.")

            # Update window options for Intraday Data
            period_selector_label.pack(after=search_entry, pady=5)
            period_selector.pack(after=period_selector_label, pady=5)
            description_label.pack_forget()
            description_text.pack_forget()
            output_text.config(width=110, height=25)
            root.geometry("900x700")

        elif selected_function == "Company Profile":
            # Call the function for company profile data
            data = fmp.fmp_profF(search_string)
            if data:
                # Format and display the data excluding 'description'
                table_data = [(key, f"{value:,}" if key == 'mktCap' else value) for key, value in data.items() if key != 'description']
                tabulated_result = tabulate(table_data, headers=['Field', 'Value'], tablefmt='fancy_grid', numalign='left', stralign='left')
                output_text.insert(tk.END, tabulated_result)
                
                # Insert the description into the separate description text widget
                if 'description' in data:
                    description_text.insert(tk.END, data['description'])
            else:
                output_text.insert(tk.END, "No profile data found for the given symbol.")

            # Update window options for Company Profile
            period_selector_label.pack_forget()
            period_selector.pack_forget()
            description_label.pack(pady=5)
            description_text.pack(pady=10)
            output_text.config(width=110, height=15)
            root.geometry("900x700")

        elif selected_function == "Search Data":
            # Call the function for general search data
            df = fmp.fmp_search(search_string)
            if not df.empty:
                tabulated_result = tabulate(df, headers='keys', tablefmt='fancy_grid', numalign='left', stralign='left')
                output_text.insert(tk.END, tabulated_result)
            else:
                output_text.insert(tk.END, "No search results found for the given term.")

            # Update window options for Search Data
            period_selector_label.pack_forget()
            period_selector.pack_forget()
            description_label.pack_forget()
            description_text.pack_forget()
            output_text.config(width=100, height=20)
            root.geometry("900x700")

        elif selected_function == "Earnings Dates":
            # Call the function for company profile data
            df = fmp.fmp_earnSym(search_string)
            if not df.empty:
                # Drop unnecessary columns and reformat DataFrame
                df_modified = df.drop(columns=['symbol']).reset_index(drop=True)
                df_modified.rename(columns={
                    'epsEstimated': 'epsEst',
                    'revenue' : 'rev (mil)',
                    'revenueEstimated': 'revEst (mil)',
                    'fiscalDateEnding': 'fiscal',
                    'updatedFromDate': 'updated',
                }, inplace=True)
                df_modified['rev (mil)'] = df_modified['rev (mil)'].div(1_000_000).round(0).fillna(0).apply(lambda x: f"{int(x):,}" if not pd.isna(x) else "N/A")
                df_modified['revEst (mil)'] = df_modified['revEst (mil)'].div(1_000_000).round(0).fillna(0).apply(lambda x: f"{int(x):,}" if not pd.isna(x) else "N/A")
                df_modified = df_modified[['date', 'time', 'eps', 'epsEst', 'rev (mil)', 'revEst (mil)', 'fiscal', 'updated']]
                tabulated_result = tabulate(df_modified, headers='keys', tablefmt='fancy_grid', numalign='left', stralign='left')
                output_text.insert(tk.END, tabulated_result)
            else:
                output_text.insert(tk.END, "No search results found for the given term.")

            # Update window options for Company Profile
            period_selector_label.pack_forget()
            period_selector.pack_forget()
            description_label.pack_forget()  # Hide company description label
            description_text.pack_forget()   # Hide company description text
            output_text.config(width=110, height=15)
            root.geometry("900x700")

    except Exception as e:
        # Handle errors
        output_text.insert(tk.END, f"An error occurred: {e}")


# Create the main window
root = tk.Tk()
root.title("FMP Multi-Function Tool")
root.geometry("900x700")

# Function selection dropdown
function_selector_label = tk.Label(root, text="Select FMP Function:")
function_selector_label.pack(pady=5)

function_selector = ttk.Combobox(root, values=["Intraday Data", "Company Profile", "Search Data", "Earnings Dates"])
function_selector.pack(pady=5)
function_selector.current(0)  # Set default selection

# Bind function selection to update the window based on selected function
function_selector.bind("<<ComboboxSelected>>", update_window_for_function)

# Create entry widget for search term
search_label = tk.Label(root, text="Enter Stock Symbol:")
search_label.pack(pady=5)

search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

# Set focus to the search entry when the application starts
search_entry.focus_set()

# Period selection dropdown for intraday data
period_selector_label = tk.Label(root, text="Select Time Period:")
period_selector = ttk.Combobox(root, values=["1min", "5min", "15min", "30min", "1hour", "1day"])
period_selector.current(3)  # Set default selection to '30min'
period_selector_label.pack_forget()
period_selector.pack_forget()

# Update the window based on the initial function selection
root.after(0, update_window_for_function)

# Create button to trigger the selected function
search_button = tk.Button(root, text="Run", command=run_selected_function)
search_button.pack(pady=5)

# Bind the Return key to the search button
root.bind('<Return>', lambda event: search_button.invoke())

# Create a scrolled text widget to display output
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=15)
output_text.pack(pady=10)

# Create a separate scrolled text widget to display the description (if applicable)
description_label = tk.Label(root, text="Company Description (if available):")
description_label.pack(pady=5)

description_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=10)
description_text.pack(pady=10)

# Run the GUI event loop
root.mainloop()
