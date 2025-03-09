import tkinter as tk
import customtkinter as ctk

class MainScreenView(ctk.CTkFrame):
    # Constructor
    def __init__(self, parent, controller):
        # Atributter
        super().__init__(parent)
        # ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.inspirotracktext = ctk.CTkLabel(master=self, text="InspiroTrack", font=("TkDefaultFont", 28))
        self.inspirotracktext.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

        self.loginbutton = ctk.CTkButton(master=self, text="Level1", command=self.controller.level1button_function)
        self.loginbutton.place(relx=0.5, rely=0.75, anchor=ctk.CENTER)

        self.createaccount_button = ctk.CTkButton(master=self, text="Level2", command=self.controller.goto_level2_screen)
        self.createaccount_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)


class MainScreenController():
    # Constructor
    def __init__(self, parent):
        self.parent = parent
        self.view = MainScreenView(parent=self.parent, controller=self)
        
    def level1button_function(self):
        self.parent.show_scene("Level1Scene")

    def goto_level2_screen(self):
        self.parent.show_scene("Level2Scene")
    
    def close(self):
        print("do nothing?")
