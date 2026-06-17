from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp  # imported to handle device-independent pixel scaling

# Global variables to pass results between popup engines dynamically
last_calculated_ff = 0.0
last_calculated_wt = 0.0

# --- SCREEN 1: LOGIN (RESPONSIVE & BALANCED) ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Outer layout forces centering on all mobile displays
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=dp(24))
        
        # Setting a rigid width hint but letting height respond naturally to spacing
        login_box = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(0.85, None))
        login_box.bind(minimum_height=login_box.setter('height'))
        
        login_box.add_widget(Label(text="WELCOME", font_size=dp(28), bold=True, color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(50)))
        
        # Using standardized mobile-friendly input field heights (dp(45))
        self.username = TextInput(hint_text="Username", multiline=False, font_size=dp(16), size_hint_y=None, height=dp(45), padding=[dp(10), dp(10), dp(10), dp(10)])
        login_box.add_widget(self.username)
        
        self.password = TextInput(hint_text="Password", password=True, multiline=False, font_size=dp(16), size_hint_y=None, height=dp(45), padding=[dp(10), dp(10), dp(10), dp(10)])
        login_box.add_widget(self.password)
        
        btn = Button(text="LOGIN", font_size=dp(18), bold=True, background_color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(50))
        btn.bind(on_press=self.check_login)
        login_box.add_widget(btn)
        
        self.error_msg = Label(text="", color=(1, 0, 0, 1), font_size=dp(14), size_hint_y=None, height=dp(30))
        login_box.add_widget(self.error_msg)
        
        root_anchor.add_widget(login_box)
        self.add_widget(root_anchor)

    def check_login(self, instance):
        if self.username.text == "admin" and self.password.text == "123":
            self.manager.current = 'dashboard'
        else:
            self.error_msg.text = "Try again! (admin / 123)"


# --- SCREEN 2: DASHBOARD (RESPONSIVE GRID & LARGER FONTS) ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        main_layout.add_widget(Label(text="Select Calculator", font_size=dp(24), bold=True, size_hint_y=0.15))
        
        from kivy.uix.gridlayout import GridLayout
        # Clean Grid using proportional sizing constraints
        grid = GridLayout(cols=2, rows=2, spacing=dp(16), size_hint_y=0.7)
        
        # Bumped button text font sizes to dp(18) with line alignment parameters
        btn1 = Button(text="01.\nFF Calculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.5, 0.8, 1))
        btn2 = Button(text="02.\nWater Temp.\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.6, 0.6, 1))
        btn3 = Button(text="03.\nIce Temp.\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.2, 0.5, 0.7, 1))
        btn4 = Button(text="04.\nRecipe\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.3, 0.4, 0.6, 1))
        
        # Ensure multi-line strings align neatly in the middle of grids
        for btn in [btn1, btn2, btn3, btn4]:
            btn.bind(size=btn.setter('text_size'))
            
        btn1.bind(on_press=self.open_ff_popup)
        btn2.bind(on_press=self.open_water_temp_popup)
        btn3.bind(on_press=self.open_ice_temp_popup)
        btn4.bind(on_press=self.open_placeholder_msg)
        
        grid.add_widget(btn1)
        grid.add_widget(btn2)
        grid.add_widget(btn3)
        grid.add_widget(btn4)
        
        main_layout.add_widget(grid)
        
        logout_btn = Button(text="Logout", size_hint_y=0.15, font_size=dp(16), background_color=(0.8, 0.2, 0.2, 1))
        logout_btn.bind(on_press=self.logout)
        main_layout.add_widget(logout_btn)
        
        self.add_widget(main_layout)
        
    # --- POPUP DESIGN FOR BOX 01: FF CALCULATOR ---
    def open_ff_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        fields = [
            ("01. WT:", "Enter WT"),
            ("02. FT:", "Enter FT"),
            ("03. ADT:", "Enter ADT")
        ]
        
        self.ff_inputs = {}
        for label_text, hint in fields:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
            row.add_widget(Label(text=label_text, size_hint_x=0.35, font_size=dp(16), halign='left'))
            txt_in = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=dp(15))
            self.ff_inputs[label_text] = txt_in
            row.add_widget(txt_in)
            popup_layout.add_widget(row)
            
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row4.add_widget(Label(text="04. FF:", size_hint_x=0.35, font_size=dp(16)))
        self.input_ff = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.65, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(self.input_ff)
        popup_layout.add_widget(row4)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.8, 0.2, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_ff_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(16))
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.ff_popup = Popup(title="01. FF Calculator Engine", content=popup_layout, size_hint=(0.95, 0.85), auto_dismiss=False)
        close_btn.bind(on_press=self.ff_popup.dismiss)
        self.ff_popup.open()

    def process_ff_calculation(self, instance):
        global last_calculated_ff
        try:
            wt_val = float(self.ff_inputs["01. WT:"].text) if self.ff_inputs["01. WT:"].text else 0.0
            ft_val = float(self.ff_inputs["02. FT:"].text) if self.ff_inputs["02. FT:"].text else 0.0
            adt_val = float(self.ff_inputs["03. ADT:"].text) if self.ff_inputs["03. ADT:"].text else 0.0
            ff_result = (3 * adt_val) - ft_val - wt_val - ft_val
            
            last_calculated_ff = ff_result
            self.input_ff.text = str(round(ff_result, 2))
        except ValueError:
            self.input_ff.text = "Error"

    # --- POPUP DESIGN FOR BOX 02: WATER TEMP CALCULATOR ---
    def open_water_temp_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Row 1-3 Layout Structure
        water_fields = [
            ("01. DDT:", "Enter DDT"),
            ("02. RT:", "Enter RT"),
            ("03. FT:", "Enter FT")
        ]
        self.w_inputs = {}
        for label, hint in water_fields:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
            row.add_widget(Label(text=label, size_hint_x=0.35, font_size=dp(16)))
            txt = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=dp(15))
            self.w_inputs[label] = txt
            row.add_widget(txt)
            popup_layout.add_widget(row)
            
        # Row 4: FF (with optimized responsive link button size)
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row4.add_widget(Label(text="04. FF:", size_hint_x=0.35, font_size=dp(16)))
        self.input_ff_water = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.45, font_size=dp(15))
        get_ff_btn = Button(text="Get", size_hint_x=0.2, font_size=dp(14), background_color=(0, 0.7, 1, 1))
        get_ff_btn.bind(on_press=self.fetch_ff_data)
        row4.add_widget(self.input_ff_water)
        row4.add_widget(get_ff_btn)
        popup_layout.add_widget(row4)
        
        # Row 5: Cal WT
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row5.add_widget(Label(text="05. Cal WT:", size_hint_x=0.35, font_size=dp(16)))
        self.input_cal_wt = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.65, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(self.input_cal_wt)
        popup_layout.add_widget(row5)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.1, 0.6, 0.6, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_water_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(16))
        
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
            ddt_val = float(self.w_inputs["01. DDT:"].text) if self.w_inputs["01. DDT:"].text else 0.0
            rt_val = float(self.w_inputs["02. RT:"].text) if self.w_inputs["02. RT:"].text else 0.0
            ft_val = float(self.w_inputs["03. FT:"].text) if self.w_inputs["03. FT:"].text else 0.0
            ff_val = float(self.input_ff_water.text) if self.input_ff_water.text else 0.0
            
            cal_wt_result = (3 * ddt_val) - rt_val - ft_val - ff_val
            last_calculated_wt = cal_wt_result
            
            self.input_cal_wt.text = str(round(cal_wt_result, 2))
        except ValueError:
            self.input_cal_wt.text = "Error"


    # --- POPUP DESIGN FOR BOX 03: ICE TEMP CALCULATOR ---
    def open_ice_temp_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Row 1: Req Water Weight
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row1.add_widget(Label(text="01. Req Water Wt:", size_hint_x=0.4, font_size=dp(15)))
        self.input_req_water = TextInput(hint_text="Enter Weight", multiline=False, input_filter='float', font_size=dp(15))
        row1.add_widget(self.input_req_water)
        popup_layout.add_widget(row1)
        
        # Row 2: WT
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=dp(10))
        row2.add_widget(Label(text="02. WT:", size_hint_x=0.4, font_size=dp(15)))
        self.input_ice_wt = TextInput(hint_text="Enter WT", multiline=False, input_filter='float', font_size=dp(15))
        row2.add_widget(self.input_ice_wt)
        popup_layout.add_widget(row2)
        
        # Row 3: Cal WT
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row3.add_widget(Label(text="03. Cal WT:", size_hint_x=0.4, font_size=dp(15)))
        self.input_ice_cal_wt = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.4, font_size=dp(15))
        get_wt_btn = Button(text="Get", size_hint_x=0.2, font_size=dp(14), background_color=(0, 0.7, 1, 1))
        get_wt_btn.bind(on_press=self.fetch_wt_data)
        row3.add_widget(self.input_ice_cal_wt)
        row3.add_widget(get_wt_btn)
        popup_layout.add_widget(row3)
        
        # Row 4: Calculated Ice Weight
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row4.add_widget(Label(text="04. Calc Ice Wt:", size_hint_x=0.4, font_size=dp(15)))
        self.output_calc_ice = TextInput(hint_text="Result", multiline=False, readonly=True, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(self.output_calc_ice)
        popup_layout.add_widget(row4)
        
        # Row 5: Calculated Water Weight
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        row5.add_widget(Label(text="05. Calc Water Wt:", size_hint_x=0.4, font_size=dp(15)))
        self.output_calc_water = TextInput(hint_text="Result", multiline=False, readonly=True, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(self.output_calc_water)
        popup_layout.add_widget(row5)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.5, 0.7, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_ice_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(16))
        
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
