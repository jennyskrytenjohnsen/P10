import customtkinter as ctk
from MainScreen import MainScreenController
from Level1 import Level1ScreenController

# from Mysql_database import Mysql
# from training_screen_controller import TrainingScreenController
# from login_controller import LoginScreenController
# from createaccount_controller import CreateAccountController
# from homescreen_controller import HomeScreenController
# from calibration_screen_controller import CalibrationScreenController
# from training_settings_controller import TrainingSettingsController
# from setup_device_settings_controller import SetUpDeviceSettingsController
# from completed_training_controller import CompletedTrainingController
# # from training_log_controller import TrainingLogController
# from training_log_controller import TrainingLogController


class SceneMaster(ctk.CTk):
    # constructor
    def __init__(self):
        ctk.CTk.__init__(self)
        # Attributes
        # self.Database_connection = Mysql()
        # Establish one connection to the database, rest of the code will use him directly.
        # initialize the current scene to None
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
            # remove the current scene from the window
            # if self.current_scene.view.winfo_exists():
            # self.current_scene.view.pack_forget()
            self.current_scene.view.destroy()

        # TILFØJ DE RESTERENDE TIL DENNE STORE IF ELIF .. lav dem om til en dictonary som vist af botten: https://i.ibb.co/2hScVXV/image.png
        # always create a new instance of the scene controller
        # order does not matter
        if scene_name == "MainScreen":
            self.current_scene = MainScreenController(self)
        elif scene_name == "Level1Scene":
            self.current_scene = Level1ScreenController(self)
        # elif scene_name == "HomeScene":
        #     self.current_scene = HomeScreenController(self)
        # elif scene_name == "TrainingScene":
        #     self.current_scene = TrainingScreenController(self)
        # elif scene_name == "CalibrationScene":
        #     self.current_scene = CalibrationScreenController(self)
        # elif scene_name == "TrainingSettingsScene":
        #     self.current_scene = TrainingSettingsController(self)
        # elif scene_name == "SetUpDeviceSettingsScene":
        #     self.current_scene = SetUpDeviceSettingsController(self)
        # elif scene_name == "CompletedTrainingScene":
        #      self.current_scene = CompletedTrainingController(self)
        # elif scene_name == "TrainingLogScene":
        #     self.current_scene = TrainingLogController(self)

        # change scene to the requested scene (every controller/scene has a .view attribute that references that screens View)
        self.current_scene.view.pack(fill="both", expand=True)


# if this script is being run directly, create a SceneMaster instance and start the GUI event loop
if __name__ == '__main__':
    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("green") 
    app = SceneMaster()
    app.geometry("400x500+10+20") # 6:19 aspect ratio på mobiler
    app.title("InspiroTrack")
    app.mainloop()
