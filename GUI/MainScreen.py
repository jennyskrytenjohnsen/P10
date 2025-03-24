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

        self.inspirotracktext = ctk.CTkLabel(master=self, text="Risk of ICU admission", font=("TkDefaultFont", 28))
        self.inspirotracktext.place(relx=0.5, rely=0.03, anchor=ctk.CENTER)

        self.loginbutton = ctk.CTkButton(master=self, text="View variables", command=self.controller.level1button_function)
        self.loginbutton.place(relx=0.95, rely=0.03, anchor=ctk.CENTER)

        self.createaccount_button = ctk.CTkButton(master=self, text="Select patient", command=self.controller.goto_level2_screen)
        self.createaccount_button.place(relx=0.05, rely=0.03, anchor=ctk.CENTER)

        self.canvas = ctk.CTkCanvas(self, width=500, height=500, background='#DBDBDB', borderwidth=0, highlightthickness=0)
        self.circle_with_number = self.canvas.create_oval(50, 50, 500, 500, outline="black", fill="red")
        self.risk_score = ctk.CTkLabel(self.canvas, font=("Helvetica", 50), fg_color="red")
        self.risk_score.place(relx=0.29, rely=0.35)
        self.canvas.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)


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
