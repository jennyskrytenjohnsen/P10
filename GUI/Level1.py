import tkinter as tk
import customtkinter as ctk

class Level1ScreenView(ctk.CTkFrame):
    # Constructor
    def __init__(self, parent, controller):
        # Atributter
        super().__init__(parent)
        # ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.headlinetext = ctk.CTkLabel(master=self, text="Variables affecting ICU admission risk", font=("TkDefaultFont", 28))
        self.headlinetext.place(relx=0.5, rely=0.03, anchor=ctk.CENTER)

        self.canvas = ctk.CTkCanvas(self, width=500, height=500, background='#DBDBDB', borderwidth=0, highlightthickness=0)
        self.line = self.canvas.create_line(250, 0, 250, 500, fill="black", width=3)  # Long vertical line at x=250
        self.canvas.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)  # Centering canvas




        self.respiratorytext = ctk.CTkLabel(master=self, text="Respiratory", font=("TkDefaultFont", 14, "bold"))
        self.respiratorytext.place(relx=0.12, rely=0.1, anchor=ctk.CENTER)
        
        self.circulatorytext = ctk.CTkLabel(master=self, text="Circulatory", font=("TkDefaultFont", 14, "bold"))
        self.circulatorytext.place(relx=0.38, rely=0.1, anchor=ctk.CENTER)
        
        self.renaltext = ctk.CTkLabel(master=self, text="Renal", font=("TkDefaultFont", 14, "bold"))
        self.renaltext.place(relx=0.64, rely=0.1, anchor=ctk.CENTER)
        
        self.demographictext = ctk.CTkLabel(master=self, text="Demographic", font=("TkDefaultFont", 14, "bold"))
        self.demographictext.place(relx=0.90, rely=0.1, anchor=ctk.CENTER)
        
        self.otherstext = ctk.CTkLabel(master=self, text="Others", font=("TkDefaultFont", 14, "bold"))
        self.otherstext.place(relx=0.90, rely=0.34, anchor=ctk.CENTER)

        self.pretext = ctk.CTkLabel(master=self, text="Preoperative", font=("TkDefaultFont", 14, "bold"))
        self.pretext.place(relx=0.03, rely=0.3, anchor=ctk.CENTER)

        self.peritext = ctk.CTkLabel(master=self, text="Perioperative", font=("TkDefaultFont", 14, "bold"))
        self.peritext.place(relx=0.03, rely=0.7, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Age", font=("TkDefaultFont", 14), fg_color="lime green")
        self.inspirotracktext.place(relx=0.90, rely=0.13, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Sex", font=("TkDefaultFont", 14), fg_color="orange")
        self.inspirotracktext.place(relx=0.90, rely=0.17, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Height", font=("TkDefaultFont", 14), fg_color="lime green")
        self.inspirotracktext.place(relx=0.90, rely=0.21, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Weight", font=("TkDefaultFont", 14), fg_color="red")
        self.inspirotracktext.place(relx=0.90, rely=0.25, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="BMI", font=("TkDefaultFont", 14), fg_color="red")
        self.inspirotracktext.place(relx=0.90, rely=0.29, anchor=ctk.CENTER)

        self.loginbutton = ctk.CTkButton(master=self, text="Front page \U0001F3E0", command=self.controller.loginbutton_function)
        self.loginbutton.place(relx=0.05, rely=0.03, anchor=ctk.CENTER)

        self.createaccount_button = ctk.CTkButton(master=self, text="View values", command=self.controller.goto_create_account_screen)
        self.createaccount_button.place(relx=0.95, rely=0.03, anchor=ctk.CENTER)


class Level1ScreenController():
    # Constructor
    def __init__(self, parent):
        self.parent = parent
        self.view = Level1ScreenView(parent=self.parent, controller=self)
       
    # VI SKAL HAVE EN GOTO_SCENE / create account scene eller home scene funktion
   
    def loginbutton_function(self):
        self.parent.show_scene("MainScreen")

    
    def goto_create_account_screen(self):
        self.parent.show_scene("Level2Scene")


    def close(self):
        print("do nothing?")

