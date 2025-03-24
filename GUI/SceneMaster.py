import customtkinter as ctk
from MainScreen import MainScreenController
from Level1 import Level1ScreenController
from Level2 import Level2ScreenController

class SceneMaster(ctk.CTk):
    # constructor
    def __init__(self):
        ctk.CTk.__init__(self)
        self.current_scene = None
        # show the first scene"
        self.show_scene("MainScreen")

        # Attributes to be used
        self.username_logged_in = None
        self.reps_completed = None
        self.sets_completed = None
        self.resistance_level_completed = None
        self.reps_goal_from_database = None
        self.sets_goal_from_database = None

    def show_scene(self, scene_name):
        # remove the current scene from the window
        if self.current_scene is not None:
            # close any resources used by the current scene
            self.current_scene.close()
            self.current_scene.view.destroy()

        if scene_name == "MainScreen":
            self.current_scene = MainScreenController(self)
        elif scene_name == "Level1Scene":
            self.current_scene = Level1ScreenController(self)
        elif scene_name == "Level2Scene":
            self.current_scene = Level2ScreenController(self)

        # change scene to the requested scene
        self.current_scene.view.pack(fill="both", expand=True)


# if this script is being run directly, create a SceneMaster instance and start the GUI event loop
if __name__ == '__main__':
    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("blue") 
    app = SceneMaster()
    app.geometry("1530x750+1+2") 
    app.title("SurgiCare")
    app.mainloop()
