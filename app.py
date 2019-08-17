from tkinter import*
from tkinter import messagebox,simpledialog

import numpy as np
import datetime
import pandas as pd
import sqlite3
entry_range=35
db_path="//mygbynbyn1ms000.corp.lumileds.org/Operations/Daily Reports/Equipment Downtime Details/film.db"
#db_path="film.db"
OPTIONS=['DB_to_Freezer#1','DB_to_Freezer#2','DB_to_Freezer#8','Freezer#1_to_Prod','Freezer#2_to_Prod','Freezer#8_to_Prod',
           'Prod_to_Freezer#1', 'Prod_to_Freezer#2','Prod_to_Freezer#8','Freezer#1_to_DB','Freezer#2_to_DB','Freezer#8_to_DB']
pw_list=['chan12345']

def connect():
    pw = simpledialog.askstring("Password", "Enter your password")
    if pw in pw_list:
        try:
            conn=sqlite3.connect(db_path)
            cur=conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS tranx (Part text, FilmID text, Qty integer,Movement text, Trx text, Employee text, Remark text)")
            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "Error. Please contact huan-yang.chan@lumileds.com")

def option_changed(*args):
    a=str(variable.get())
    return a

def focus_next_window(event):
    event.widget.tk_focusNext().focus()
    return("break")

def clear_entry():
    EMP.delete(0, END)
    for i in range(entry_range):
        PARTS[i].delete(0, END)
        IDS[i].delete(0, END)
        QTYS[i].delete(0, END)
        RMKS[i].delete(0, END)
    messagebox.showinfo("Complete", "Clear all entry successfully")

def delete_query():
    pw = simpledialog.askstring("Password", "Enter your password")
    if pw in pw_list:
        query=simpledialog.askstring("Query", "Enter your query")
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Execute Query successfully")
        except:
            messagebox.showinfo("Error", "Error. Please contact huan-yang.chan@lumileds.com")

def download_inventory():
    currentDT = (datetime.datetime.now()).strftime("%Y-%m-%d %H-%M-%S")
    MsgBox = messagebox.askquestion ('Download File','Are you sure you want to download???',icon = 'warning')
    if MsgBox == 'yes':
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM tranx"
            df = (pd.read_sql(query, conn)).drop_duplicates(subset=['FilmID'], keep='last')
            conn.close()
            df.to_csv(currentDT+' Film_LastMovement.csv',index=False)
            messagebox.showinfo("Success", "File downloaded successfully")
        except:
            messagebox.showinfo("Error", "Error. Please contact huan-yang.chan@lumileds.com")

def download_all():
    currentDT = (datetime.datetime.now()).strftime("%Y-%m-%d %H-%M-%S")
    MsgBox = messagebox.askquestion ('Download File','Are you sure you want to download???',icon = 'warning')
    if MsgBox == 'yes':
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM tranx"
            df = (pd.read_sql(query, conn))
            conn.close()
            df.to_csv(currentDT+' All_Film_Transaction.csv',index=False)
            messagebox.showinfo("Success", "File downloaded successfully")
        except:
            messagebox.showinfo("Error", "Error. Please contact huan-yang.chan@lumileds.com")

def export_to_database():
    currentDT=(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    employeeid=emp.get()
    datalist0=[]
    datalist1=[]
    datalist2=[]
    datalist3=[]
    datalist4=[]
    errcount=0

    MsgBox = messagebox.askquestion ('Upload to database','Are you sure you want to upload???',icon = 'warning')
    if MsgBox == 'yes':
        # Append used row only
        if len(employeeid)>0:
            for i in range(entry_range):
                if (len(PARTS[i].get().strip())+len(IDS[i].get().strip())+len(QTYS[i].get().strip()))>0:
                    datalist0.append("Row {}".format(i+1))
                    datalist1.append(PARTS[i].get().strip())
                    datalist2.append(IDS[i].get().strip())
                    datalist3.append(QTYS[i].get().strip())
                    datalist4.append(RMKS[i].get().strip())
            matrix = np.column_stack((datalist0, datalist1, datalist2, datalist3, datalist4))
            # print (matrix)
            # print (matrix[0][0])
            # print (matrix.shape[0])

            for i in range(matrix.shape[0]):
                # Validate column Part#
                if len(matrix[i][1])==0:
                    messagebox.showinfo("Error","Part#-{} is blank".format(matrix[i][0]))
                    errcount=errcount+1
                # Validate column Film ID
                if len(matrix[i][2]) == 0:
                    messagebox.showinfo("Error","Film ID-{} is blank".format(matrix[i][0]))
                    errcount = errcount + 1
                # Validate column Qty
                try:
                    int(matrix[i][3])
                except ValueError:
                    messagebox.showinfo("Error","Qty-{} is not integer".format(matrix[i][0]))
                    errcount = errcount + 1
            #If no error export to database
            if errcount==0:
                df=pd.DataFrame(data=matrix[:,1:],
                                columns=["Part","FilmID","Qty","Remark"])
                df['Movement'] = option_changed()
                df['Trx'] = currentDT
                df['Employee'] = employeeid
                print(df)
                try:
                    conn = sqlite3.connect(db_path)
                    df.to_sql('tranx', conn, if_exists='append', index=False)
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Upload to database successfully")
                    clear_entry()
                except:
                    messagebox.showinfo("Error", "Database not connected. Please contact huan-yang.chan@lumileds.com")
        else:
            messagebox.showinfo("Error", "Employee ID is blank")

window=Tk()
window.wm_title("Film Tracking")

lb1=Label(window,text="Employee ID:")
lb1.grid(row=0,column=1)

emp=StringVar()
EMP = Entry(window, textvariable=emp)
EMP.grid(row=0, column=2, padx=3)

lb2=Label(window,text="Movement:")
lb2.grid(row=2,column=1)

variable = StringVar()
variable.set(OPTIONS[0]) # default value
variable.trace("w", option_changed)
w = OptionMenu(window, variable, *OPTIONS)
w.grid(row=2, column=2, padx=3)

lb3=Label(window,text="Part#")
lb3.grid(row=4,column=1)

lb4=Label(window,text="Film ID")
lb4.grid(row=4,column=2)

lb5=Label(window,text="Qty")
lb5.grid(row=4,column=3)

lb6=Label(window,text="Remark")
lb6.grid(row=4,column=4)

PARTS=[]
IDS=[]
QTYS=[]
RMKS=[]
for i in range(entry_range):
    ROW = Label(window,text="R{0}".format(i+1))
    ROW.grid(row=i+5, column=0)

    PART = Entry(window,textvariable="part{0}".format(i+1))
    PART.grid(row=i+5, column=1,padx=3)
    PARTS.append(PART)
    PART.bind("<Return>", focus_next_window)

    ID = Entry(window,textvariable="id{0}".format(i+1))
    ID.grid(row=i+5, column=2,padx=3)
    IDS.append(ID)
    ID.bind("<Return>", focus_next_window)

    QTY = Entry(window,textvariable="qty{0}".format(i+1),width=8)
    QTY.grid(row=i+5, column=3,padx=3)
    QTYS.append(QTY)
    QTY.bind("<Return>", focus_next_window)

    RMK = Entry(window,textvariable="rmk{0}".format(i+1),width=40,takefocus=0)
    RMK.grid(row=i+5, column=4,padx=3)
    RMKS.append(RMK)

b1=Button(window,text="Download Report (Last Movement)", width=30,command=download_inventory)
b1.grid(row=0,column=5,padx=3,pady=1)

b2=Button(window,text="Download Report (All Transaction)", width=30,command=download_all)
b2.grid(row=1,column=5,padx=3,pady=1)

b3=Button(window,text="Create Database", width=30,command=connect)
b3.grid(row=2,column=5,padx=3,pady=1)

b4=Button(window,text="Delete", width=30,command=delete_query)
b4.grid(row=3,column=5,padx=3,pady=1)

b5=Button(window,text="Export", width=30,command=export_to_database)
b5.grid(row=7,column=5,padx=3)

b6=Button(window,text="Clear", width=30,command=clear_entry)
b6.grid(row=10,column=5,padx=3)

window.mainloop()

