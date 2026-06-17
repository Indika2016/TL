from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.metrics import dp  

# Global variables to pass results between popup engines dynamically
last_calculated_ff = 0.0
last_calculated_wt = 0.0

# --- SCREEN 1: LOGIN ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=dp(24))
        login_box = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(0.85, None))
        login_box.bind(minimum_height=login_box.setter('height'))
        
        login_box.add_widget(Label(text="WELCOME", font_size=dp(28), bold=True, color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(50)))
        
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


# --- SCREEN 2: DASHBOARD ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.saved_recipes_db = {}
        self._calculating = False  
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        main_layout.add_widget(Label(text="Select Calculator", font_size=dp(24), bold=True, size_hint_y=0.15))
        
        grid = GridLayout(cols=2, rows=2, spacing=dp(16), size_hint_y=0.7)
        
        btn1 = Button(text="01.\nFF Calculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.5, 0.8, 1))
        btn2 = Button(text="02.\nWater Temp.\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.6, 0.6, 1))
        btn3 = Button(text="03.\nIce Temp.\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.2, 0.5, 0.7, 1))
        btn4 = Button(text="04.\nRecipe\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.3, 0.4, 0.6, 1))
        
        for btn in [btn1, btn2, btn3, btn4]:
            btn.bind(size=btn.setter('text_size'))
            
        btn1.bind(on_press=self.open_ff_popup)
        btn2.bind(on_press=self.open_water_temp_popup)
        btn3.bind(on_press=self.open_ice_temp_popup)
        btn4.bind(on_press=self.open_recipe_popup)
        
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
            lbl = Label(text=label_text, size_hint_x=0.35, font_size=dp(16), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            txt_in = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=dp(15))
            self.ff_inputs[label_text] = txt_in
            row.add_widget(lbl)
            row.add_widget(txt_in)
            popup_layout.add_widget(row)
            
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl4 = Label(text="04. FF:", size_hint_x=0.35, font_size=dp(16), halign='left', valign='middle')
        lbl4.bind(size=lbl4.setter('text_size'))
        self.input_ff = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.65, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(lbl4)
        row4.add_widget(self.input_ff)
        popup_layout.add_widget(row4)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.8, 0.2, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_ff_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
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
        
        water_fields = [
            ("01. DDT:", "Enter DDT"),
            ("02. RT:", "Enter RT"),
            ("03. FT:", "Enter FT")
        ]
        self.w_inputs = {}
        for label, hint in water_fields:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
            lbl = Label(text=label, size_hint_x=0.45, font_size=dp(16), halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            txt = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=dp(15))
            self.w_inputs[label] = txt
            row.add_widget(lbl)
            row.add_widget(txt)
            popup_layout.add_widget(row)
            
        row6 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl5 = Label(text="04. FF:", size_hint_x=0.45, font_size=dp(16), halign='left', valign='middle')
        lbl5.bind(size=lbl5.setter('text_size'))
        self.input_ff_water = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.35, font_size=dp(15))
        get_ff_btn = Button(text="Get", size_hint_x=0.2, font_size=dp(14), background_color=(0, 0.7, 1, 1))
        get_ff_btn.bind(on_press=self.fetch_ff_data)
        row6.add_widget(lbl5)
        row6.add_widget(self.input_ff_water)
        row6.add_widget(get_ff_btn)
        popup_layout.add_widget(row6)
        
        row7 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl6 = Label(text="05. Cal WT:", size_hint_x=0.45, font_size=dp(16), halign='left', valign='middle')
        lbl6.bind(size=lbl6.setter('text_size'))
        self.input_cal_wt = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.55, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row7.add_widget(lbl6)
        row7.add_widget(self.input_cal_wt)
        popup_layout.add_widget(row7)
        
        popup_layout.add_widget(Label()) 

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.1, 0.6, 0.6, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_water_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(16))
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.water_popup = Popup(title="02. Water Temp Calculator", content=popup_layout, size_hint=(0.95, 0.9), auto_dismiss=False)
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
        
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl1 = Label(text="01. Req Water Wt:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl1.bind(size=lbl1.setter('text_size')) 
        self.input_req_water = TextInput(hint_text="Enter Weight", multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row1.add_widget(lbl1)
        row1.add_widget(self.input_req_water)
        popup_layout.add_widget(row1)
        
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl2 = Label(text="02. WT:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl2.bind(size=lbl2.setter('text_size'))
        self.input_ice_wt = TextInput(hint_text="Enter WT", multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row2.add_widget(lbl2)
        row2.add_widget(self.input_ice_wt)
        popup_layout.add_widget(row2)
        
        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl3 = Label(text="03. Cal WT:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl3.bind(size=lbl3.setter('text_size'))
        self.input_ice_cal_wt = TextInput(hint_text="Value", multiline=False, input_filter='float', size_hint_x=0.35, font_size=dp(15))
        get_wt_btn = Button(text="Get", size_hint_x=0.2, font_size=dp(14), background_color=(0, 0.7, 1, 1))
        get_wt_btn.bind(on_press=self.fetch_wt_data)
        row3.add_widget(lbl3)
        row3.add_widget(self.input_ice_cal_wt)
        row3.add_widget(get_wt_btn)
        popup_layout.add_widget(row3)
        
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl4 = Label(text="04. Calc Ice Wt:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl4.bind(size=lbl4.setter('text_size'))
        self.output_calc_ice = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.55, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row4.add_widget(lbl4)
        row4.add_widget(self.output_calc_ice)
        popup_layout.add_widget(row4)
        
        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl5 = Label(text="05. Calc Water Wt:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl5.bind(size=lbl5.setter('text_size'))
        self.output_calc_water = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.55, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(lbl5)
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


    # --- POPUP DESIGN FOR BOX 04: RECIPE CALCULATOR ---
    def open_recipe_popup(self, instance):
        base_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # New unified Top Control Bar (Title Left, Checkbox Right)
        ctrl_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(5))
        
        self.recipe_title_label = Label(
            text="Active Recipe: New Formulation", 
            font_size=dp(15), 
            bold=True, 
            color=(1, 0.8, 0.2, 1), 
            size_hint_x=0.65, 
            halign='left', 
            valign='middle'
        )
        self.recipe_title_label.bind(size=self.recipe_title_label.setter('text_size'))
        ctrl_bar.add_widget(self.recipe_title_label)
        
        # Explicit label naming changed to "Auto cal."
        autocal_lbl = Label(text="Auto cal.", font_size=dp(13), size_hint_x=0.25, halign='right', valign='middle')
        autocal_lbl.bind(size=autocal_lbl.setter('text_size'))
        ctrl_bar.add_widget(autocal_lbl)
        
        self.realtime_checkbox = CheckBox(size_hint_x=0.1, active=False) # Disabled on startup
        self.realtime_checkbox.bind(active=self.on_checkbox_toggle)
        ctrl_bar.add_widget(self.realtime_checkbox)
        
        base_layout.add_widget(ctrl_bar)
        
        scroll_window = ScrollView(size_hint=(1, 0.8))
        self.form_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))
        
        # --- Top Totals Bar ---
        totals_grid = GridLayout(cols=6, size_hint_y=None, height=dp(40), spacing=dp(5))
        totals_grid.add_widget(Label(text="Total Wt:", font_size=dp(13), bold=True))
        
        self.recipe_total_weight = TextInput(hint_text="0.00", multiline=False, input_filter='float', font_size=dp(13))
        self.recipe_total_weight.bind(text=self.on_manual_field_change)
        totals_grid.add_widget(self.recipe_total_weight)
        
        totals_grid.add_widget(Label(text="Total Flour:", font_size=dp(13), bold=True))
        self.recipe_total_flour = TextInput(hint_text="0.00", readonly=True, multiline=False, font_size=dp(13), background_color=(0.9, 0.9, 0.9, 1))
        totals_grid.add_widget(self.recipe_total_flour)
        
        totals_grid.add_widget(Label(text="Total Water:", font_size=dp(13), bold=True))
        self.recipe_total_water = TextInput(hint_text="0.00", readonly=True, multiline=False, font_size=dp(13), background_color=(0.9, 0.9, 0.9, 1))
        totals_grid.add_widget(self.recipe_total_water)
        self.form_layout.add_widget(totals_grid)
        
        def create_header_row(title_text):
            header = GridLayout(cols=4, size_hint_y=None, height=dp(30), spacing=dp(5))
            lbl_main = Label(text=title_text, bold=True, font_size=dp(16), color=(0, 0.7, 1, 1), halign='left', valign='middle', size_hint_x=0.4)
            lbl_main.bind(size=lbl_main.setter('text_size'))
            header.add_widget(lbl_main)
            header.add_widget(Label(text="Bakers %", bold=True, font_size=dp(12), size_hint_x=0.2))
            header.add_widget(Label(text="True %", bold=True, font_size=dp(12), size_hint_x=0.2))
            header.add_widget(Label(text="Weight", bold=True, font_size=dp(12), size_hint_x=0.2))
            return header

        # --- SECTION A: SPONGE SYSTEM ---
        self.form_layout.add_widget(create_header_row("Sponge Section"))
        
        sponge_ingredients = ["Flour", "Water", "Yeast"]
        self.sponge_inputs = {}
        for ing in sponge_ingredients:
            row = GridLayout(cols=4, size_hint_y=None, height=dp(36), spacing=dp(5))
            lbl = Label(text=ing, font_size=dp(14), halign='left', valign='middle', size_hint_x=0.4)
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            
            b_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            t_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            wt_val = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            
            b_pct.bind(text=self.on_manual_field_change)
            t_pct.bind(text=self.on_manual_field_change)
            wt_val.bind(text=self.on_manual_field_change)
            
            self.sponge_inputs[ing] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            row.add_widget(b_pct)
            row.add_widget(t_pct)
            row.add_widget(wt_val)
            self.form_layout.add_widget(row)
            
        self.btn_add_sponge = Button(text="+ Add Ingredient (Sponge)", font_size=dp(13), size_hint_y=None, height=dp(32), background_color=(0.2, 0.6, 0.4, 1))
        self.btn_add_sponge.bind(on_press=lambda inst: self.show_add_ingredient_dialog("sponge"))
        self.form_layout.add_widget(self.btn_add_sponge)
        
        # --- SECTION B: DOUGH SYSTEM ---
        self.form_layout.add_widget(create_header_row("Dough Section"))
        
        dough_ingredients = ["Flour", "Water", "Sugar", "Shortening", "MSNF"]
        self.dough_inputs = {}
        for ing in dough_ingredients:
            row = GridLayout(cols=4, size_hint_y=None, height=dp(36), spacing=dp(5))
            lbl = Label(text=ing, font_size=dp(14), halign='left', valign='middle', size_hint_x=0.4)
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            
            b_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            t_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            wt_val = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
            
            b_pct.bind(text=self.on_manual_field_change)
            t_pct.bind(text=self.on_manual_field_change)
            wt_val.bind(text=self.on_manual_field_change)
            
            self.dough_inputs[ing] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            row.add_widget(b_pct)
            row.add_widget(t_pct)
            row.add_widget(wt_val)
            self.form_layout.add_widget(row)
            
        self.btn_add_dough = Button(text="+ Add Ingredient (Dough)", font_size=dp(13), size_hint_y=None, height=dp(32), background_color=(0.2, 0.6, 0.4, 1))
        self.btn_add_dough.bind(on_press=lambda inst: self.show_add_ingredient_dialog("dough"))
        self.form_layout.add_widget(self.btn_add_dough)
        
        # --- Total Formulation Summary Bar ---
        total_summary_row = GridLayout(cols=4, size_hint_y=None, height=dp(38), spacing=dp(5))
        lbl_sum = Label(text="Total", bold=True, font_size=dp(14), halign='left', valign='middle', size_hint_x=0.4)
        lbl_sum.bind(size=lbl_sum.setter('text_size'))
        total_summary_row.add_widget(lbl_sum)
        
        self.total_bakers_summary = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=dp(13), background_color=(0.85, 0.92, 0.98, 1))
        self.total_true_summary = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=dp(13), background_color=(0.85, 0.92, 0.98, 1))
        self.total_weight_summary = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=dp(13), background_color=(0.85, 0.92, 0.98, 1))
        
        total_summary_row.add_widget(self.total_bakers_summary)
        total_summary_row.add_widget(self.total_true_summary)
        total_summary_row.add_widget(self.total_weight_summary)
        self.form_layout.add_widget(total_summary_row)
        
        scroll_window.add_widget(self.form_layout)
        base_layout.add_widget(scroll_window)
        
        # --- Action Control Bar ---
        action_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(48))
        
        save_btn = Button(text="Save Recipe", background_color=(0.15, 0.65, 0.35, 1), font_size=dp(14), bold=True)
        save_btn.bind(on_press=self.trigger_save_workflow)
        
        load_btn = Button(text="Load Recipe", background_color=(0.15, 0.45, 0.65, 1), font_size=dp(14), bold=True)
        load_btn.bind(on_press=self.trigger_load_list_popup)
        
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(14))
        
        action_layout.add_widget(save_btn)
        action_layout.add_widget(load_btn)
        action_layout.add_widget(close_btn)
        base_layout.add_widget(action_layout)
        
        self.recipe_popup = Popup(title="04. Professional Baker Bakers % / True % Engine", content=base_layout, size_hint=(0.98, 0.95), auto_dismiss=False)
        close_btn.bind(on_press=self.recipe_popup.dismiss)
        self.recipe_popup.open()

    def on_checkbox_toggle(self, checkbox, value):
        if value:
            # Real-time calculation activated -> immediately execute calculations
            self.calculate_recipe_matrix()

    # --- REAL-TIME CALCULATION DISPATCHER ---
    def on_manual_field_change(self, instance, value):
        if self._calculating:
            return
        
        # Run calculation cycle instantly if Auto cal. checkbox is ticked
        if not self.realtime_checkbox.active:
            return
        
        context_section = None
        context_ingredient = None
        context_field_type = None
        
        if instance == self.recipe_total_weight:
            context_field_type = "total_weight"
        else:
            for s_name, inputs in [("Sponge", self.sponge_inputs), ("Dough", self.dough_inputs)]:
                for ing, fields in inputs.items():
                    for f_key, f_inst in fields.items():
                        if f_inst == instance:
                            context_section = s_name
                            context_ingredient = ing
                            context_field_type = f_key
                            break

        self.calculate_recipe_matrix(trigger_field=context_field_type, trigger_ing=context_ingredient, trigger_sec=context_section)

    # --- MAIN CALCULATION & VALIDATION ENGINE ---
    def calculate_recipe_matrix(self, trigger_field=None, trigger_ing=None, trigger_sec=None):
        if self._calculating:
            return
        
        self._calculating = True
        
        try:
            # 1. Parse Top level editable weight
            try: total_dough_weight = float(self.recipe_total_weight.text or 0.0)
            except ValueError: total_dough_weight = 0.0

            # 2. Extract active status metrics
            sponge_has_data = any(f["bakers"].text or f["true"].text or f["weight"].text for f in self.sponge_inputs.values())
            dough_has_data = any(f["bakers"].text or f["true"].text or f["weight"].text for f in self.dough_inputs.values())

            # 3. Dynamic Back-Calculation Logic from manual weight entries
            if trigger_field == "weight" and total_dough_weight > 0:
                target_inputs = self.sponge_inputs if trigger_sec == "Sponge" else self.dough_inputs
                try:
                    m_weight = float(target_inputs[trigger_ing]["weight"].text or 0.0)
                    calculated_true = (m_weight / total_dough_weight) * 100
                    target_inputs[trigger_ing]["true"].text = str(round(calculated_true, 2))
                    trigger_field = "true" 
                except ValueError: pass

            # 4. Handle Flour Rule Balancing Constraints
            sf_bakers = float(self.sponge_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.sponge_inputs else 0.0
            df_bakers = float(self.dough_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.dough_inputs else 0.0

            if not sponge_has_data and dough_has_data and "Flour" in self.dough_inputs:
                if trigger_field != "bakers" or trigger_ing != "Flour" or trigger_sec != "Dough":
                    self.dough_inputs["Flour"]["bakers"].text = "100.00"
                    df_bakers = 100.0

            # 5. Calculate Baker Total Percentages Base Summation
            total_bakers_sum = 0.0
            for name, fields in self.sponge_inputs.items():
                if name != "Water": # Skip water inside sponge configuration sum criteria
                    try: total_bakers_sum += float(fields["bakers"].text or 0.0)
                    except ValueError: pass
            for name, fields in self.dough_inputs.items():
                try: total_bakers_sum += float(fields["bakers"].text or 0.0)
                except ValueError: pass

            if total_bakers_sum == 0:
                total_bakers_sum = 100.0 

            # 6. Compute True Percentages and Weights Columns
            running_true_sum = 0.0
            running_flour_weight = 0.0
            running_water_weight = 0.0
            total_accumulated_weight_all_ingredients = 0.0  

            # Process Sponge elements
            for name, fields in self.sponge_inputs.items():
                try: b_val = float(fields["bakers"].text or 0.0)
                except ValueError: b_val = 0.0

                if name == "Water":
                    flour_bakers = float(self.sponge_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.sponge_inputs else 0.0
                    t_val = (b_val * flour_bakers) / total_bakers_sum
                else:
                    t_val = (b_val * 100.0) / total_bakers_sum

                if trigger_field != "true" or trigger_ing != name or trigger_sec != "Sponge":
                    fields["true"].text = str(round(t_val, 2)) if t_val > 0 else ""
                else:
                    try: t_val = float(fields["true"].text or 0.0)
                    except ValueError: t_val = 0.0

                if trigger_field == "total_weight" or trigger_field == "bakers" or trigger_field == "true" or trigger_field is None:
                    if total_dough_weight > 0:
                        w_val = (total_dough_weight * t_val) / 100.0
                        fields["weight"].text = str(round(w_val, 2)) if w_val > 0 else ""
                
                try: current_w = float(fields["weight"].text or 0.0)
                except ValueError: current_w = 0.0

                if name.lower() == "flour": running_flour_weight += current_w
                elif name.lower() == "water": running_water_weight += current_w

                running_true_sum += t_val
                total_accumulated_weight_all_ingredients += current_w

            # Process Dough elements
            for name, fields in self.dough_inputs.items():
                try: b_val = float(fields["bakers"].text or 0.0)
                except ValueError: b_val = 0.0

                t_val = (b_val * 100.0) / total_bakers_sum

                if trigger_field != "true" or trigger_ing != name or trigger_sec != "Dough":
                    fields["true"].text = str(round(t_val, 2)) if t_val > 0 else ""
                else:
                    try: t_val = float(fields["true"].text or 0.0)
                    except ValueError: t_val = 0.0

                if trigger_field == "total_weight" or trigger_field == "bakers" or trigger_field == "true" or trigger_field is None:
                    if total_dough_weight > 0:
                        w_val = (total_dough_weight * t_val) / 100.0
                        fields["weight"].text = str(round(w_val, 2)) if w_val > 0 else ""
                
                try: current_w = float(fields["weight"].text or 0.0)
                except ValueError: current_w = 0.0

                if name.lower() == "flour": running_flour_weight += current_w
                elif name.lower() == "water": running_water_weight += current_w

                running_true_sum += t_val
                total_accumulated_weight_all_ingredients += current_w

            # 7. Update Metrics Display fields
            self.recipe_total_flour.text = str(round(running_flour_weight, 2)) if running_flour_weight > 0 else "0.00"
            self.recipe_total_water.text = str(round(running_water_weight, 2)) if running_water_weight > 0 else "0.00"
            
            if trigger_field != "total_weight" and total_accumulated_weight_all_ingredients > 0 and total_dough_weight == 0:
                self.recipe_total_weight.text = str(round(total_accumulated_weight_all_ingredients, 2))

            self.total_bakers_summary.text = str(round(total_bakers_sum, 2))
            self.total_true_summary.text = str(round(running_true_sum, 2))
            self.total_weight_summary.text = str(round(total_accumulated_weight_all_ingredients, 2))

            # 8. Contrast-Safe Validation Highlights Engine
            error_bg = [0.6, 0.1, 0.1, 1]  
            normal_bg = [1, 1, 1, 1]

            if running_true_sum > 0 and not (99.0 <= round(running_true_sum, 2) <= 100.01):
                self.total_true_summary.background_color = error_bg
                self.total_true_summary.color = [1, 1, 1, 1]
            else:
                self.total_true_summary.background_color = [0.85, 0.92, 0.98, 1]
                self.total_true_summary.color = [0, 0, 0, 1]

            if sponge_has_data and dough_has_data:
                combined_flour_bakers = sf_bakers + df_bakers
                if round(combined_flour_bakers, 2) != 100.0:
                    if "Flour" in self.sponge_inputs: self.sponge_inputs["Flour"]["bakers"].background_color = error_bg
                    if "Flour" in self.dough_inputs: self.dough_inputs["Flour"]["bakers"].background_color = error_bg
                else:
                    if "Flour" in self.sponge_inputs: self.sponge_inputs["Flour"]["bakers"].background_color = normal_bg
                    if "Flour" in self.dough_inputs: self.dough_inputs["Flour"]["bakers"].background_color = normal_bg
            else:
                if "Flour" in self.sponge_inputs: self.sponge_inputs["Flour"]["bakers"].background_color = normal_bg
                if "Flour" in self.dough_inputs: self.dough_inputs["Flour"]["bakers"].background_color = normal_bg

        finally:
            self._calculating = False

    # --- DYNAMIC INGREDIENT PROMPT SYSTEM ---
    def show_add_ingredient_dialog(self, section_type):
        dialog_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        dialog_layout.add_widget(Label(text="Enter New Ingredient Name:", font_size=dp(15), bold=True))
        ing_name_input = TextInput(hint_text="e.g. Salt, Milk, etc.", multiline=False, font_size=dp(14))
        dialog_layout.add_widget(ing_name_input)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        add_btn = Button(text="Add", background_color=(0.2, 0.7, 0.2, 1))
        close_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(close_btn)
        dialog_layout.add_widget(btn_layout)
        
        prompt_popup = Popup(title=f"Add to {section_type.title()}", content=dialog_layout, size_hint=(0.85, 0.35))
        
        def execute_addition(instance):
            name = ing_name_input.text.strip()
            if name:
                self.inject_new_ingredient_row(name, section_type)
                prompt_popup.dismiss()
                
        add_btn.bind(on_press=execute_addition)
        close_btn.bind(on_press=prompt_popup.dismiss)
        prompt_popup.open()

    def inject_new_ingredient_row(self, name, section_type):
        new_row = GridLayout(cols=4, size_hint_y=None, height=dp(36), spacing=dp(5))
        lbl = Label(text=name, font_size=dp(14), halign='left', valign='middle', size_hint_x=0.4)
        lbl.bind(size=lbl.setter('text_size'))
        new_row.add_widget(lbl)
        
        b_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
        t_pct = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
        wt_val = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=dp(13))
        
        b_pct.bind(text=self.on_manual_field_change)
        t_pct.bind(text=self.on_manual_field_change)
        wt_val.bind(text=self.on_manual_field_change)
        
        new_row.add_widget(b_pct)
        new_row.add_widget(t_pct)
        new_row.add_widget(wt_val)
        
        if section_type == "sponge":
            self.sponge_inputs[name] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            target_index = self.form_layout.children.index(self.btn_add_sponge)
            self.form_layout.add_widget(new_row, index=target_index + 1)
        else:
            self.dough_inputs[name] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            target_index = self.form_layout.children.index(self.btn_add_dough)
            self.form_layout.add_widget(new_row, index=target_index + 1)

    # --- SAVE RECIPE WORKFLOW ENGINE ---
    def trigger_save_workflow(self, instance):
        filled_count = 0
        valid_rows = []

        for name, fields in self.sponge_inputs.items():
            bp = fields["bakers"].text.strip()
            tp = fields["true"].text.strip()
            wt = fields["weight"].text.strip()
            if bp or tp or wt:
                filled_count += 1
                valid_rows.append(("Sponge", name, bp or "0.00", tp or "0.00", wt or "0.00"))

        for name, fields in self.dough_inputs.items():
            bp = fields["bakers"].text.strip()
            tp = fields["true"].text.strip()
            wt = fields["weight"].text.strip()
            if bp or tp or wt:
                filled_count += 1
                valid_rows.append(("Dough", name, bp or "0.00", tp or "0.00", wt or "0.00"))

        if filled_count <= 2:
            warn_box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
            warn_box.add_widget(Label(text="Not enough recipe details filled to save.", font_size=dp(14), bold=True))
            ok_btn = Button(text="OK", size_hint_y=None, height=dp(40), background_color=(0.8, 0.2, 0.2, 1))
            warn_box.add_widget(ok_btn)
            
            warn_popup = Popup(title="Warning", content=warn_box, size_hint=(0.7, 0.25))
            ok_btn.bind(on_press=warn_popup.dismiss)
            warn_popup.open()
            return

        save_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        table_header = GridLayout(cols=5, size_hint_y=None, height=dp(30), spacing=dp(2))
        cols_config = [
            ("Sec", 0.15), ("Ingredient", 0.37), ("Bakers %", 0.16), ("True %", 0.16), ("Weight", 0.16)
        ]
        for title, hint_x in cols_config:
            lbl = Label(text=title, bold=True, font_size=dp(12), size_hint_x=hint_x, halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            table_header.add_widget(lbl)
        save_layout.add_widget(table_header)

        scroll_view = ScrollView(size_hint=(1, 0.6))
        grid_table = GridLayout(cols=5, spacing=dp(2), size_hint_y=None)
        grid_table.bind(minimum_height=grid_table.setter('height'))

        for sec, ing_name, b_pct, t_pct, w_val in valid_rows:
            row_data = [(sec, 0.15), (ing_name, 0.37), (b_pct, 0.16), (t_pct, 0.16), (w_val, 0.16)]
            for text_val, hint_x in row_data:
                cell_lbl = Label(text=text_val, font_size=dp(12), size_hint_x=hint_x, size_hint_y=None, height=dp(28), halign='center', valign='middle')
                cell_lbl.bind(size=cell_lbl.setter('text_size'))
                grid_table.add_widget(cell_lbl)

        scroll_view.add_widget(grid_table)
        save_layout.add_widget(scroll_view)

        input_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        input_container.add_widget(Label(text="Recipe Name:", font_size=dp(14), bold=True, size_hint_x=0.3))
        recipe_name_field = TextInput(hint_text="Enter file identity name", multiline=False, size_hint_x=0.7, font_size=dp(14))
        input_container.add_widget(recipe_name_field)
        save_layout.add_widget(input_container)

        btn_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        confirm_save_btn = Button(text="Save", background_color=(0.15, 0.65, 0.35, 1), font_size=dp(14), bold=True)
        cancel_save_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(14))
        
        btn_container.add_widget(confirm_save_btn)
        btn_container.add_widget(cancel_save_btn)
        save_layout.add_widget(btn_container)

        save_popup = Popup(title="Review Recipe Summary Layout", content=save_layout, size_hint=(0.95, 0.75), auto_dismiss=False)
        cancel_save_btn.bind(on_press=save_popup.dismiss)

        def save_to_database(inst):
            final_name = recipe_name_field.text.strip()
            if not final_name:
                recipe_name_field.hint_text = "Name required!"
                return
            
            self.saved_recipes_db[final_name] = {
                "dataset": valid_rows,
                "top_totals": {
                    "weight": self.recipe_total_weight.text,
                    "flour": self.recipe_total_flour.text,
                    "water": self.recipe_total_water.text
                },
                "bottom_totals": {
                    "bakers": self.total_bakers_summary.text,
                    "true": self.total_true_summary.text,
                    "weight": self.total_weight_summary.text
                }
            }
            self.recipe_title_label.text = f"Active Recipe: {final_name}"
            save_popup.dismiss()

        confirm_save_btn.bind(on_press=save_to_database)
        save_popup.open()

    # --- LOAD RECIPE LIST ENGINE ---
    def trigger_load_list_popup(self, instance):
        list_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        
        if not self.saved_recipes_db:
            no_rec_lbl = Label(text="No saved records found in system storage.", font_size=dp(15), halign='center', valign='middle')
            no_rec_lbl.bind(size=no_rec_lbl.setter('text_size'))
            list_layout.add_widget(no_rec_lbl)
            
            close_lbl_btn = Button(text="Close", size_hint_y=None, height=dp(45), background_color=(0.8, 0.2, 0.2, 1))
            list_layout.add_widget(close_lbl_btn)
            load_list_popup = Popup(title="Database Library Index", content=list_layout, size_hint=(0.85, 0.35))
            close_lbl_btn.bind(on_press=load_list_popup.dismiss)
            load_list_popup.open()
            return

        title_lbl = Label(text="Select Recipe Profile:", bold=True, size_hint_y=None, height=dp(25), halign='center', valign='middle')
        title_lbl.bind(size=title_lbl.setter('text_size'))
        list_layout.add_widget(title_lbl)
        
        scroll_records = ScrollView()
        records_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        records_box.bind(minimum_height=records_box.setter('height'))

        load_list_popup = Popup(title="Database Library Index", content=list_layout, size_hint=(0.9, 0.85))

        for item_key in self.saved_recipes_db.keys():
            row_item_btn = Button(text=str(item_key), size_hint_y=None, height=dp(42), background_color=(0.2, 0.4, 0.6, 1))
            row_item_btn.bind(on_press=lambda inst, key=item_key: self.open_recipe_preview(key, load_list_popup))
            records_box.add_widget(row_item_btn)

        scroll_records.add_widget(records_box)
        list_layout.add_widget(scroll_records)

        cancel_list_btn = Button(text="Cancel", size_hint_y=None, height=dp(45), background_color=(0.8, 0.2, 0.2, 1))
        cancel_list_btn.bind(on_press=load_list_popup.dismiss)
        list_layout.add_widget(cancel_list_btn)
        
        load_list_popup.open()

    # --- SUB-WINDOW RECIPE PROFILE PREVIEW ---
    def open_recipe_preview(self, recipe_key, primary_popup):
        record_profile = self.saved_recipes_db[recipe_key]
        
        preview_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        preview_layout.add_widget(Label(text=f"Profile View: {recipe_key}", bold=True, size_hint_y=None, height=dp(25), color=(0, 0.7, 1, 1)))

        preview_table = GridLayout(cols=4, size_hint_y=None, height=dp(30), spacing=dp(2))
        view_config = [("Ingredient", 0.4), ("Bakers %", 0.2), ("True %", 0.2), ("Weight", 0.2)]
        for h_text, size_x in view_config:
            lbl = Label(text=h_text, bold=True, font_size=dp(12), size_hint_x=size_x, halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            preview_table.add_widget(lbl)
        preview_layout.add_widget(preview_table)

        scroll_preview = ScrollView(size_hint=(1, 0.65))
        grid_preview = GridLayout(cols=4, spacing=dp(2), size_hint_y=None)
        grid_preview.bind(minimum_height=grid_preview.setter('height'))

        for sec, name, bp, tp, wt in record_profile["dataset"]:
            row_items = [(name, 0.4), (bp, 0.2), (tp, 0.2), (wt, 0.2)]
            for val, size_x in row_items:
                c_lbl = Label(text=val, font_size=dp(12), size_hint_x=size_x, size_hint_y=None, height=dp(28), halign='center', valign='middle')
                c_lbl.bind(size=c_lbl.setter('text_size'))
                grid_preview.add_widget(c_lbl)

        scroll_preview.add_widget(grid_preview)
        preview_layout.add_widget(scroll_preview)

        btn_preview_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(10))
        confirm_load_btn = Button(text="Load", background_color=(0.15, 0.45, 0.65, 1), font_size=dp(14), bold=True)
        cancel_preview_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(14))

        btn_preview_container.add_widget(confirm_load_btn)
        btn_preview_container.add_widget(cancel_preview_btn)
        preview_layout.add_widget(btn_preview_container)

        preview_popup = Popup(title="Recipe Component Preview Window", content=preview_layout, size_hint=(0.95, 0.8), auto_dismiss=False)
        cancel_preview_btn.bind(on_press=preview_popup.dismiss)

        def inject_recipe_to_main_screen(inst):
            self._calculating = True
            try:
                for _, fields in self.sponge_inputs.items():
                    fields["bakers"].text = ""
                    fields["true"].text = ""
                    fields["weight"].text = ""
                for _, fields in self.dough_inputs.items():
                    fields["bakers"].text = ""
                    fields["true"].text = ""
                    fields["weight"].text = ""

                for sec, name, bp, tp, wt in record_profile["dataset"]:
                    target_dict = self.sponge_inputs if sec == "Sponge" else self.dough_inputs
                    if name not in target_dict:
                        self.inject_new_ingredient_row(name, sec.lower())
                    
                    target_dict[name]["bakers"].text = bp if float(bp or 0) > 0 else ""
                    target_dict[name]["true"].text = tp if float(tp or 0) > 0 else ""
                    target_dict[name]["weight"].text = wt if float(wt or 0) > 0 else ""

                self.recipe_total_weight.text = record_profile["top_totals"]["weight"]
                self.recipe_total_flour.text = record_profile["top_totals"]["flour"]
                self.recipe_total_water.text = record_profile["top_totals"]["water"]

                self.total_bakers_summary.text = record_profile["bottom_totals"]["bakers"]
                self.total_true_summary.text = record_profile["bottom_totals"]["true"]
                self.total_weight_summary.text = record_profile["bottom_totals"]["weight"]
                
                self.recipe_title_label.text = "Active Recipe: {recipe_key}"
            finally:
                self._calculating = False

            self.calculate_recipe_matrix()
            preview_popup.dismiss()
            primary_popup.dismiss()

        confirm_load_btn.bind(on_press=inject_recipe_to_main_screen)
        preview_popup.open()

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
