import tkinter as tk
from tkinter import ttk, filedialog, Button, Entry, StringVar
import csv

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("БВП Data Analysis")
        self.data = {}  # use dictionary to avoid duplicates
        self.modified_data = {}  # Add this line to initialize the new dictionary
        self.filtered_data = None

        self.search_term = StringVar()
        self.gdp_filter = StringVar()

        self.sort_by = None  # column to sort by
        self.sort_order = False  # False = ascending, True = descending

        # Layout using grid system for better organisation

        # row 0
        ttk.Label(self, text="Търси:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.search_entry = Entry(self, textvariable=self.search_term)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky='we')
        self.search_button = Button(self, text="Търси", command=self.search)
        self.search_button.grid(row=0, column=2, padx=10, pady=10, sticky='w')

        # row 1
        ttk.Label(self, text="Филтрирай по БВП:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.filter_gdp_entry = Entry(self, textvariable=self.gdp_filter)
        self.filter_gdp_entry.grid(row=1, column=1, padx=10, pady=10, sticky='we')
        self.filter_gdp_button = Button(self, text="Филтрирай", command=self.filter_gdp)
        self.filter_gdp_button.grid(row=1, column=2, padx=10, pady=10, sticky='w')

        # row 2
        self.treeview = ttk.Treeview(self)
        self.treeview.grid(row=2, column=0, padx=10, pady=10, columnspan=3, sticky='nsew')

        # row 3
        self.load_button = Button(self, text="Зареди файл", command=self.load_file)
        self.load_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.save_button = Button(self, text="Запази файл", command=self.save_file)
        self.save_button.grid(row=3, column=1, padx=10, pady=10, sticky='e')
        self.save_filtered_button = Button(self, text="Запази филтрирани данни", command=self.save_filtered)
        self.save_filtered_button.grid(row=3, column=2, padx=10, pady=10, sticky='e')

        # Configure column weights (affects resizing behavior)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        # Configure row weights (affects resizing behavior)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=5)  # treeview will take up most space
        self.grid_rowconfigure(3, weight=1)

        self.geometry('800x600')

    def search(self):
        term = self.search_term.get().lower()
        result = {k: v for k, v in self.data.items() if term in k.lower() or term in (str(value).lower() for value in v.values())}
        self.update_treeview(result)
        self.modified_data = result  # Add this line to store the search result

    # Do the same in the filter_gdp function:
    def filter_gdp(self):
        gdp = self.gdp_filter.get()
        if not gdp.replace('.','',1).isdigit():
            print("Invalid GDP value")
            return
        gdp = float(gdp)
        self.filtered_data = {k: v for k, v in self.data.items() if float(v['GDP']) > gdp}
        self.update_treeview(self.filtered_data)
        self.modified_data = self.filtered_data  # Add this line to store the filtered data

    # And in the sort_by_column function, after the line that sorts the data:
    def sort_by_column(self, column):
        # toggle sort order
        self.sort_order = not self.sort_order if column == self.sort_by else False
        self.sort_by = column
        # sort data
        data = dict(sorted(self.data.items(),
                           key=lambda x: float(x[1].get(column, "")) if x[1].get(column, "").replace('.','',1).isdigit() else x[1].get(column, ""),
                           reverse=self.sort_order))
        self.update_treeview(data)
        self.modified_data = data  # Add this line to store the sorted data

    # Finally, modify the save_filtered function to save the modified data:
    def save_filtered(self):
        if not self.modified_data:  # if the modified_data dictionary is empty
            print("No modified data to save")
            return
        self.save_file(self.modified_data)  # save the modified data
        
    
    

    def save_file(self, data=None):
        if data is None:
            data = self.data
        filename = filedialog.asksaveasfilename()
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=list(next(iter(data.values())).keys()))
            writer.writeheader()
            writer.writerows(data.values())


    def load_file(self):
        filenames = filedialog.askopenfilenames()  # allow selection of multiple files
        for filename in filenames:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Country'] not in self.data:
                        self.data[row['Country']] = row
                    else:
                        self.data[row['Country']].update(row)
        self.update_treeview()

    def update_treeview(self, data=None):
        if data is None:
            data = self.data
        self.treeview.delete(*self.treeview.get_children())  # delete current rows
        columns = list(next(iter(data.values())).keys())
        self.treeview['columns'] = columns  # set columns
        self.treeview.column("#0", width=0)  # hide the '#' column
        for col in columns:
            self.treeview.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))  # set column headers
        for country, row_data in data.items():
            self.treeview.insert("", tk.END, values=list(row_data.values()))  # insert new rows




    

if __name__ == "__main__":
    app = Application()
    app.mainloop()
