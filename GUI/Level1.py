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

        self.loginbutton = ctk.CTkButton(master=self, text="Login", command=self.controller.loginbutton_function)
        self.loginbutton.place(relx=0.5, rely=0.75, anchor=ctk.CENTER)

        self.createaccount_button = ctk.CTkButton(master=self, text="Create account", command=self.controller.goto_create_account_screen)
        self.createaccount_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)


class Level1ScreenController():
    # Constructor
    def __init__(self, parent):
        self.parent = parent
        self.view = Level1ScreenView(parent=self.parent, controller=self)
       
    # VI SKAL HAVE EN GOTO_SCENE / create account scene eller home scene funktion
   
    def loginbutton_function(self):
        self.parent.show_scene("MainScreen")

    
    def goto_create_account_screen(self):
        self.parent.show_scene("HomeScene")


    def close(self):
        print("do nothing?")

