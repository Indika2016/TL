from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window

# Simulating a mobile portrait screen layout
Window.size = (360, 640)

# --- SCREEN 1: LOGIN ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        layout.add_widget(Label(text="WELCOME", font_size=40, color=(0, 0.7, 1, 1)))
        
        self.username = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.username)
        
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.password)
        
        btn = Button(text="LOGIN", size_hint_y=None, height=60, background_color=(0, 0.7, 1, 1))
        btn.bind(on_press=self.check_login)
        layout.add_widget(btn)
        
        self.error_msg = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.error_msg)
        
        self.add_widget(layout)

    def check_login(self, instance):
        if self.username.text == "admin" and self.password.text == "123":
            self.manager.current = 'dashboard'
        else:
            self.error_msg.text = "Try again! (admin / 123)"


# --- SCREEN 2: DASHBOARD (4 LARGE BOXES) ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        main_layout.add_widget(Label(text="Select Calculator", font_size=24, size_hint_y=None, height=40))
        
        from kivy.uix.gridlayout import GridLayout
        grid = GridLayout(cols=2, rows=2, spacing=15)
        
        btn1 = Button(text="01.\nFF Calculator", halign='center', font_size=18, background_color=(0.1, 0.5, 0.8, 1))
        btn2 = Button(text="02.\nWater Temp.\nCalculator", halign='center', font_size=18, background_color=(0.1, 0.6, 0.6, 1))
        btn3 = Button(text="03.\nIce Temp.\nCalculator", halign='center', font_size=18, background_color=(0.2, 0.5, 0.7, 1))
        btn4 = Button(text="04.\nRecipe\nCalculator", halign='center', font_size=18, background_color=(0.3, 0.4, 0.6, 1))
        
        # Binding both buttons to their respective popups
        btn1.bind(on_press=self.open_ff_popup)
        btn2.bind(on_press=self.open_water_temp_popup)
        
        # Placeholders for remaining modules
        btn3.bind(on_press=self.open_placeholder_msg)
        btn4.bind(on_press=self.open_placeholder_msg)
        
        grid.add_widget(btn1)
        grid.add_widget(btn2)
        grid.add_widget(btn3)
        grid.add_widget(btn4)
        
        main_layout.add_widget(grid)
        
        logout_btn = Button(text="Logout", size_hint_y=None, height=45, background_color=(0.8, 0.2, 0.2, 1))
        logout_btn.bind(on_press=self.logout)
        main_layout.add_widget(logout_btn)
        
        self.add_widget(main_layout)
        
    # --- POPUP DESIGN FOR BOX 01: FF CALCULATOR ---
    def open_ff_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row1.add_widget(Label(text="01. WT:", size_hint_x=0.3))
        self.input_wt = TextInput(hint_text="Enter WT", multiline=False, input_filter='float', size_hint_x=0.7)
        row1.add_widget(self.input_wt)
        popup_layout.add_widget(row1)
        
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row2.add_widget(Label(text="02. FT:", size_hint_x=0.3))
        self.input_ft = TextInput(hint_text="Enter FT", multiline=False, input_filter='float', size_hint_x=0.7)
        row2.add_widget(self.input_ft)
        popup_layout.add_widget(row2)
        
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row3.add_widget(Label(text="03. ADT:", size_hint_x=0.3))
        self.input_adt = TextInput(hint_text="Enter ADT", multiline=False, input_filter='float', size_hint_x=0.7)
        row3.add_widget(self.input_adt)
        popup_layout.add_widget(row3)
        
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row4.add_widget(Label(text="04. FF:", size_hint_x=0.3))
        self.input_ff = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.7, background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(self.input_ff)
        popup_layout.add_widget(row4)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.8, 0.2, 1), font_size=16)
        calc_btn.bind(on_press=self.process_ff_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.ff_popup = Popup(title="01. FF Calculator Engine", content=popup_layout, size_hint=(0.95, 0.8), auto_dismiss=False)
        close_btn.bind(on_press=self.ff_popup.dismiss)
        self.ff_popup.open()

    def process_ff_calculation(self, instance):
        try:
            wt_val = float(self.input_wt.text) if self.input_wt.text else 0.0
            ft_val = float(self.input_ft.text) if self.input_ft.text else 0.0
            adt_val = float(self.input_adt.text) if self.input_adt.text else 0.0
            ff_result = (3 * adt_val) - ft_val - wt_val - ft_val
            self.input_ff.text = str(round(ff_result, 2))
        except ValueError:
            self.input_ff.text = "Error"


    # --- NEW: POPUP DESIGN FOR BOX 02: WATER TEMP CALCULATOR ---
    def open_water_temp_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Row 1: DDT (Input)
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row1.add_widget(Label(text="01. DDT:", size_hint_x=0.3))
        self.input_ddt = TextInput(hint_text="Enter DDT", multiline=False, input_filter='float', size_hint_x=0.7)
        row1.add_widget(self.input_ddt)
        popup_layout.add_widget(row1)
        
        # Row 2: RT (Input)
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row2.add_widget(Label(text="02. RT:", size_hint_x=0.3))
        self.input_rt = TextInput(hint_text="Enter RT", multiline=False, input_filter='float', size_hint_x=0.7)
        row2.add_widget(self.input_rt)
        popup_layout.add_widget(row2)
        
        # Row 3: FT (Input)
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row3.add_widget(Label(text="03. FT:", size_hint_x=0.3))
        self.input_ft_water = TextInput(hint_text="Enter FT", multiline=False, input_filter='float', size_hint_x=0.7)
        row3.add_widget(self.input_ft_water)
        popup_layout.add_widget(row3)
        
        # Row 4: FF (Input)
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row4.add_widget(Label(text="04. FF:", size_hint_x=0.3))
        self.input_ff_water = TextInput(hint_text="Enter FF", multiline=False, input_filter='float', size_hint_x=0.7)
        row4.add_widget(self.input_ff_water)
        popup_layout.add_widget(row4)
        
        # Row 5: Cal WT (Read-Only Output Display Box)
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row5.add_widget(Label(text="05. Cal WT:", size_hint_x=0.3))
        self.input_cal_wt = TextInput(
            hint_text="Result will appear here", 
            multiline=False, 
            readonly=True, 
            size_hint_x=0.7,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        row5.add_widget(self.input_cal_wt)
        popup_layout.add_widget(row5)
        
        # Spacer block
        popup_layout.add_widget(Label()) 

        # Bottom Action buttons layout
        action_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        
        calc_btn = Button(text="Calculate", background_color=(0.1, 0.6, 0.6, 1), font_size=16)
        calc_btn.bind(on_press=self.process_water_calculation)
        
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.water_popup = Popup(
            title="02. Water Temp Calculator Engine",
            content=popup_layout,
            size_hint=(0.95, 0.85), # Slightly taller to comfortably fit 5 fields
            auto_dismiss=False
        )
        close_btn.bind(on_press=self.water_popup.dismiss)
        self.water_popup.open()

    def process_water_calculation(self, instance):
        try:
            # Convert inputs into mathematical float decimals
            ddt_val = float(self.input_ddt.text) if self.input_ddt.text else 0.0
            rt_val = float(self.input_rt.text) if self.input_rt.text else 0.0
            ft_val = float(self.input_ft_water.text) if self.input_ft_water.text else 0.0
            ff_val = float(self.input_ff_water.text) if self.input_ff_water.text else 0.0
            
            # Using your mathematical formula: 3*DDT - RT - FT - FF
            cal_wt_result = (3 * ddt_val) - rt_val - ft_val - ff_val
            
            # Update the read-only box with the final result
            self.input_cal_wt.text = str(round(cal_wt_result, 2))
            
        except ValueError:
            self.input_cal_wt.text = "Error"

    def open_placeholder_msg(self, instance):
        print("Module '{instance.text.replace('\n', ' ')}' under development.")

    def logout(self, instance):
        self.manager.current = 'login'


# --- APP MANAGER ---
class MyMainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm


if __name__ == '__main__':
    MyMainApp().run()
    