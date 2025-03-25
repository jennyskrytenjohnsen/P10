import tkinter as tk
import customtkinter as ctk

class SelectPatientScreenView(ctk.CTkFrame):
    # Constructor
    def __init__(self, parent, controller):
        # Atributter
        super().__init__(parent)
        # ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Select patient", font=("TkDefaultFont", 28))
        self.inspirotracktext.place(relx=0.5, rely=0.03, anchor=ctk.CENTER)

        self.frontpagebutton = ctk.CTkButton(master=self, text="Front page \U0001F3E0", command=self.controller.frontpagebutton_function)
        self.frontpagebutton.place(relx=0.05, rely=0.03, anchor=ctk.CENTER)

        self.createaccount_button = ctk.CTkButton(master=self, text="Anne Pernille Jensen 141598-1334", command=self.controller.goto_create_account_screen)
        self.createaccount_button.place(relx=0.45, rely=0.6, anchor=ctk.CENTER)


class SelectPatientController():
    # Constructor
    def __init__(self, parent):
        self.parent = parent
        self.view = SelectPatientScreenView(parent=self.parent, controller=self)
   
    def frontpagebutton_function(self):
        self.parent.show_scene("MainScreen")

    
    def goto_create_account_screen(self):
        self.parent.show_scene("Level1Scene")


    def close(self):
        print("do nothing?")

