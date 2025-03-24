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

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Variables affecting ICU admission risk", font=("TkDefaultFont", 28))
        self.inspirotracktext.place(relx=0.5, rely=0.03, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Respiratory", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.12, rely=0.1, anchor=ctk.CENTER)
        
        self.inspirotracktext = ctk.CTkLabel(master=self, text="Circulatory", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.32, rely=0.1, anchor=ctk.CENTER)
        
        self.inspirotracktext = ctk.CTkLabel(master=self, text="Renal", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.52, rely=0.1, anchor=ctk.CENTER)
        
        self.inspirotracktext = ctk.CTkLabel(master=self, text="Demographic", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.72, rely=0.1, anchor=ctk.CENTER)
        
        self.inspirotracktext = ctk.CTkLabel(master=self, text="Others", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.92, rely=0.1, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Preoperative", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.03, rely=0.3, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Perioperative", font=("TkDefaultFont", 14))
        self.inspirotracktext.place(relx=0.03, rely=0.7, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Test variable1", font=("TkDefaultFont", 14), fg_color="red")
        self.inspirotracktext.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Test variable2", font=("TkDefaultFont", 14), fg_color="orange")
        self.inspirotracktext.place(relx=0.5, rely=0.8, anchor=ctk.CENTER)

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Test variable3", font=("TkDefaultFont", 14), fg_color="lime green")
        self.inspirotracktext.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

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

