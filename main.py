from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# Global variables to pass results between popup engines dynamically
last_calculated_ff = 0.0
last_calculated_wt = 0.0

# --- SCREEN 1: LOGIN (FIXED SIZING) ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Outer anchor layout forces the login box to remain perfectly centered on mobile
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=20)
        
        # Main login box restricted to 85% width and 50% height of any screen size
        login_box = BoxLayout(orientation='vertical', spacing=15, size_hint=(0.85, 0.5))
        
        login_box.add_widget(Label(text="WELCOME", font_size=32, bold=True, color=(0, 0.7, 1, 1), size_hint_y=0.2))
        
        self.username = TextInput(hint_text="Username", multiline=False, size_hint_y=0.18, font_size=18, padding=[10, 10, 10, 10])
        login_box.add_widget(self.username)
        
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=0.18, font_size=18, padding=[10, 10, 10, 10])
        login_box.add_widget(self.password)
        
        btn = Button(text="LOGIN", size_hint_y=0.2, font_size=20, bold=True, background_color=(0, 0.7, 1, 1))
        btn.bind(on_press=self.check_login)
        login_box.add_widget(btn)
        
        self.error_msg = Label(text="", color=(1, 0, 0, 1), size_hint_y=0.12, font_size=16)
        login_box.add_widget(self.error_msg)
        
        root_anchor.add_widget(login_box)
        self.add_widget(root_anchor)

    def check_login(self, instance):
        if self.username.text == "admin" and self.password.text == "123":
            self.manager.current = 'dashboard'
        else:
            self.error_msg.text = "Try again! (admin / 123)"


# --- SCREEN 2: DASHBOARD (FIXED SIZING) ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        main_layout.add_widget(Label(text="Select Calculator", font_size=26, bold=True, size_hint_y=0.1))
        
        from kivy.uix.gridlayout import GridLayout
        # Grid takes up 75% of the screen height dynamically
        grid = GridLayout(cols=2, rows=2, spacing=15, size_hint_y=0.75)
        
        btn1 = Button(text="01.\nFF Calculator", halign='center', font_size=18, background_color=(0.1, 0.5, 0.8, 1))
        btn2 = Button(text="02.\nWater Temp.\nCalculator", halign='center', font_size=18, background_color=(0.1, 0.6, 0.6, 1))
        btn3 = Button(text="03.\nIce Temp.\nCalculator", halign='center', font_size=18, background_color=(0.2, 0.5, 0.7, 1))
        btn4 = Button(text="04.\nRecipe\nCalculator", halign='center', font_size=18, background_color=(0.3, 0.4, 0.6, 1))
        
        btn1.bind(on_press=self.open_ff_popup)
        btn2.bind(on_press=self.open_water_temp_popup)
        btn3.bind(on_press=self.open_ice_temp_popup)
        btn4.bind(on_press=self.open_placeholder_msg)
        
        grid.add_widget(btn1)
        grid.add_widget(btn2)
        grid.add_widget(btn3)
        grid.add_widget(btn4)
        
        main_layout.add_widget(grid)
        
        logout_btn = Button(text="Logout", size_hint_y=0.1, font_size=18, background_color=(0.8, 0.2, 0.2, 1))
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
        global last_calculated_ff
        try:
            wt_val = float(self.input_wt.text) if self.input_wt.text else 0.0
            ft_val = float(self.input_ft.text) if self.input_ft.text else 0.0
            adt_val = float(self.input_adt.text) if self.input_adt.text else 0.0
            ff_result = (3 * adt_val) - ft_val - wt_val - ft_val
            
            last_calculated_ff = ff_result
            self.input_ff.text = str(round(ff_result, 2))
        except ValueError:
            self.input_ff.text = "Error"

    # --- POPUP DESIGN FOR BOX 02: WATER TEMP CALCULATOR ---
    def open_water_temp_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row1.add_widget(Label(text="01. DDT:", size_hint_x=0.4))
        self.input_ddt = TextInput(hint_text="Enter DDT", multiline=False, input_filter='float', size_hint_x=0.6)
        row1.add_widget(self.input_ddt)
        popup_layout.add_widget(row1)
        
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row2.add_widget(Label(text="02. RT:", size_hint_x=0.4))
        self.input_rt = TextInput(hint_text="Enter RT", multiline=False, input_filter='float', size_hint_x=0.6)
        row2.add_widget(self.input_rt)
        popup_layout.add_widget(row2)
        
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row3.add_widget(Label(text="03. FT:", size_hint_x=0.4))
        self.input_ft_water = TextInput(hint_text="Enter FT", multiline=False, input_filter='float', size_hint_x=0.6)
        row3.add_widget(self.input_ft_water)
        popup_layout.add_widget(row3)
        
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row4.add_widget(Label(text="04. FF:", size_hint_x=0.4))
        self.input_ff_water = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.45)
        get_ff_btn = Button(text="Get", size_hint_x=0.15, background_color=(0, 0.7, 1, 1))
        get_ff_btn.bind(on_press=self.fetch_ff_data)
        row4.add_widget(self.input_ff_water)
        row4.add_widget(get_ff_btn)
        popup_layout.add_widget(row4)
        
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row5.add_widget(Label(text="05. Cal WT:", size_hint_x=0.4))
        self.input_cal_wt = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.6, background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(self.input_cal_wt)
        popup_layout.add_widget(row5)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        calc_btn = Button(text="Calculate", background_color=(0.1, 0.6, 0.6, 1), font_size=16)
        calc_btn.bind(on_press=self.process_water_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.water_popup = Popup(title="02. Water Temp Calculator", content=popup_layout, size_hint=(0.95, 0.85), auto_dismiss=False)
        close_btn.bind(on_press=self.water_popup.dismiss)
        self.water_popup.open()

    def fetch_ff_data(self, instance):
        global last_calculated_ff
        self.input_ff_water.text = str(round(last_calculated_ff, 2))

    def process_water_calculation(self, instance):
        global last_calculated_wt
        try:
            ddt_val = float(self.input_ddt.text) if self.input_ddt.text else 0.0
            rt_val = float(self.input_rt.text) if self.input_rt.text else 0.0
            ft_val = float(self.input_ft_water.text) if self.input_ft_water.text else 0.0
            ff_val = float(self.input_ff_water.text) if self.input_ff_water.text else 0.0
            
            cal_wt_result = (3 * ddt_val) - rt_val - ft_val - ff_val
            last_calculated_wt = cal_wt_result
            
            self.input_cal_wt.text = str(round(cal_wt_result, 2))
        except ValueError:
            self.input_cal_wt.text = "Error"


    # --- POPUP DESIGN FOR BOX 03: ICE TEMP CALCULATOR ---
    def open_ice_temp_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row1.add_widget(Label(text="01. Req Water Wt:", size_hint_x=0.4))
        self.input_req_water = TextInput(hint_text="Enter Weight", multiline=False, input_filter='float', size_hint_x=0.6)
        row1.add_widget(self.input_req_water)
        popup_layout.add_widget(row1)
        
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row2.add_widget(Label(text="02. WT:", size_hint_x=0.4))
        self.input_ice_wt = TextInput(hint_text="Enter WT", multiline=False, input_filter='float', size_hint_x=0.6)
        row2.add_widget(self.input_ice_wt)
        popup_layout.add_widget(row2)
        
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row3.add_widget(Label(text="03. Cal WT:", size_hint_x=0.4))
        self.input_ice_cal_wt = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.45)
        get_wt_btn = Button(text="Get", size_hint_x=0.15, background_color=(0, 0.7, 1, 1))
        get_wt_btn.bind(on_press=self.fetch_wt_data)
        row3.add_widget(self.input_ice_cal_wt)
        row3.add_widget(get_wt_btn)
        popup_layout.add_widget(row3)
        
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row4.add_widget(Label(text="04. Calc Ice Wt:", size_hint_x=0.4))
        self.output_calc_ice = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.6, background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(self.output_calc_ice)
        popup_layout.add_widget(row4)
        
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        row5.add_widget(Label(text="05. Calc Water Wt:", size_hint_x=0.4))
        self.output_calc_water = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.6, background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(self.output_calc_water)
        popup_layout.add_widget(row5)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=55)
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.5, 0.7, 1), font_size=16)
        calc_btn.bind(on_press=self.process_ice_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.ice_popup = Popup(title="03. Ice Temp Calculator Engine", content=popup_layout, size_hint=(0.95, 0.85), auto_dismiss=False)
        close_btn.bind(on_press=self.ice_popup.dismiss)
        self.ice_popup.open()

    def fetch_wt_data(self, instance):
        global last_calculated_wt
        self.input_ice_cal_wt.text = str(round(last_calculated_wt, 2))

    def process_ice_calculation(self, instance):
        try:
            req_water = float(self.input_req_water.text) if self.input_req_water.text else 0.0
            wt_val = float(self.input_ice_wt.text) if self.input_ice_wt.text else 0.0
            cal_wt = float(self.input_ice_cal_wt.text) if self.input_ice_cal_wt.text else 0.0
            
            if (wt_val + 80) == 0:
                self.output_calc_ice.text = "Error: Div by 0"
                self.output_calc_water.text = "Error"
                return

            ice_weight = req_water * (wt_val - cal_wt) / (wt_val + 80)
            water_weight = req_water - ice_weight
            
            self.output_calc_ice.text = str(round(ice_weight, 2))
            self.output_calc_water.text = str(round(water_weight, 2))
        except ValueError:
            self.output_calc_ice.text = "Error"
            self.output_calc_water.text = "Error"

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
