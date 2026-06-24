import json
import os
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

# File name used for permanent local recipe storage
DB_FILE_PATH = "recipes_db.json"

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
        self.load_recipes_from_disk()  # Permanent Storage Load
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

    # --- PERMANENT STORAGE MANAGEMENT ---
    def load_recipes_from_disk(self):
        if os.path.exists(DB_FILE_PATH):
            try:
                with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
                    self.saved_recipes_db = json.load(f)
            except Exception:
                self.saved_recipes_db = {}
        else:
            self.saved_recipes_db = {}

    def save_recipes_to_disk(self):
        try:
            with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.saved_recipes_db, f, indent=4)
        except Exception as e:
            print(f"Error saving recipes to local file: {e}")
        
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
            
        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl4 = Label(text="04. FF:", size_hint_x=0.45, font_size=dp(16), halign='left', valign='middle')
        lbl4.bind(size=lbl4.setter('text_size'))
        self.input_w_ff = TextInput(text=str(last_calculated_ff), multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row4.add_widget(lbl4)
        row4.add_widget(self.input_w_ff)
        popup_layout.add_widget(row4)

        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl5 = Label(text="05. Cal WT:", size_hint_x=0.45, font_size=dp(16), halign='left', valign='middle')
        lbl5.bind(size=lbl5.setter('text_size'))
        self.input_w_wt = TextInput(hint_text="Result", multiline=False, readonly=True, size_hint_x=0.55, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(lbl5)
        row5.add_widget(self.input_w_wt)
        popup_layout.add_widget(row5)

        popup_layout.add_widget(Label())

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.8, 0.2, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_water_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.water_popup = Popup(title="02. Water Temp. Calculator Engine", content=popup_layout, size_hint=(0.95, 0.85), auto_dismiss=False)
        close_btn.bind(on_press=self.water_popup.dismiss)
        self.water_popup.open()

    def process_water_calculation(self, instance):
        global last_calculated_wt
        try:
            ddt_val = float(self.w_inputs["01. DDT:"].text) if self.w_inputs["01. DDT:"].text else 0.0
            rt_val = float(self.w_inputs["02. RT:"].text) if self.w_inputs["02. RT:"].text else 0.0
            ft_val = float(self.w_inputs["03. FT:"].text) if self.w_inputs["03. FT:"].text else 0.0
            ff_val = float(self.input_w_ff.text) if self.input_w_ff.text else 0.0
            
            wt_result = (3 * ddt_val) - rt_val - ft_val - ff_val
            last_calculated_wt = wt_result
            self.input_w_wt.text = str(round(wt_result, 2))
        except ValueError:
            self.input_w_wt.text = "Error"

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
        self.input_ice_wt = TextInput(text=str(last_calculated_wt), multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row2.add_widget(lbl2)
        row2.add_widget(self.input_ice_wt)
        popup_layout.add_widget(row2)

        row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl3 = Label(text="03. Source Ice Temp:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl3.bind(size=lbl3.setter('text_size'))
        self.input_src_ice_temp = TextInput(text="-12", multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row3.add_widget(lbl3)
        row3.add_widget(self.input_src_ice_temp)
        popup_layout.add_widget(row3)

        row4 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl4 = Label(text="04. Source H2O Temp:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl4.bind(size=lbl4.setter('text_size'))
        self.input_src_h2o_temp = TextInput(text="22", multiline=False, input_filter='float', size_hint_x=0.55, font_size=dp(15))
        row4.add_widget(lbl4)
        row4.add_widget(self.input_src_h2o_temp)
        popup_layout.add_widget(row4)

        row5 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        lbl5 = Label(text="05. Target Ice Wt:", size_hint_x=0.45, font_size=dp(15), halign='left', valign='middle')
        lbl5.bind(size=lbl5.setter('text_size'))
        self.ice_sub_result = TextInput(hint_text="Ice Result", multiline=False, readonly=True, size_hint_x=0.25, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        self.water_sub_result = TextInput(hint_text="Water Result", multiline=False, readonly=True, size_hint_x=0.30, font_size=dp(15), background_color=(0.9, 0.9, 0.9, 1))
        row5.add_widget(lbl5)
        row5.add_widget(self.ice_sub_result)
        row5.add_widget(self.water_sub_result)
        popup_layout.add_widget(row5)

        popup_layout.add_widget(Label())

        action_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None, height=dp(50))
        calc_btn = Button(text="Calculate", background_color=(0.2, 0.8, 0.2, 1), font_size=dp(16))
        calc_btn.bind(on_press=self.process_ice_calculation)
        close_btn = Button(text="Close", background_color=(0.8, 0.2, 0.2, 1), font_size=16)
        
        action_layout.add_widget(calc_btn)
        action_layout.add_widget(close_btn)
        popup_layout.add_widget(action_layout)
        
        self.ice_popup = Popup(title="03. Ice Substitution Engine", content=popup_layout, size_hint=(0.95, 0.85), auto_dismiss=False)
        close_btn.bind(on_press=self.ice_popup.dismiss)
        self.ice_popup.open()

    def process_ice_calculation(self, instance):
        try:
            req_wat = float(self.input_req_water.text) if self.input_req_water.text else 0.0
            wt_val = float(self.input_ice_wt.text) if self.input_ice_wt.text else 0.0
            src_ice = float(self.input_src_ice_temp.text) if self.input_src_ice_temp.text else 0.0
            src_h2o = float(self.input_src_h2o_temp.text) if self.input_src_h2o_temp.text else 0.0
            
            numerator = req_wat * (src_h2o - wt_val)
            denominator = 80 + src_h2o - (0.5 * src_ice)
            
            if denominator == 0:
                self.ice_sub_result.text = "Error"
                self.water_sub_result.text = "Error"
                return

            ice_weight = numerator / denominator
            if ice_weight < 0:
                ice_weight = 0.0
            if ice_weight > req_wat:
                ice_weight = req_wat
                
            water_weight = req_wat - ice_weight
            
            self.ice_sub_result.text = str(round(ice_weight, 2)) + "g (Ice)"
            self.water_sub_result.text = str(round(water_weight, 2)) + "g (Water)"
        except ValueError:
            self.ice_sub_result.text = "Error"
            self.water_sub_result.text = "Error"

    # --- POPUP DESIGN FOR BOX 04: PROFESSIONAL RECIPE CALCULATOR MATRIX ENGINE ---
    def open_recipe_popup(self, instance):
        base_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        ctrl_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(8))
        self.recipe_title_label = Label(text="Active Recipe: Unsaved System Instance", font_size=dp(14), bold=True, halign='left', size_hint_x=0.6)
        self.recipe_title_label.bind(size=self.recipe_title_label.setter('text_size'))
        ctrl_bar.add_widget(self.recipe_title_label)
        
        ctrl_bar.add_widget(Label(text="Live Realtime Sync:", font_size=dp(12), size_hint_x=0.3, halign='right'))
        self.realtime_checkbox = CheckBox(size_hint_x=0.1, active=False)
        self.realtime_checkbox.bind(active=self.on_checkbox_toggle)
        ctrl_bar.add_widget(self.realtime_checkbox)
        base_layout.add_widget(ctrl_bar)
        
        scroll_window = ScrollView(size_hint=(1, 0.8))
        self.form_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))
        
        totals_grid = GridLayout(cols=6, size_hint_y=None, height=dp(40), spacing=dp(5))
        totals_grid.add_widget(Label(text="Total Wt:", font_size=dp(13), bold=True))
        self.recipe_total_weight = TextInput(hint_text="0.00", multiline=False, input_filter='float', font_size=dp(13))
        self.recipe_total_weight.bind(text=self.on_manual_field_change)
        totals_grid.add_widget(self.recipe_total_weight)
        
        totals_grid.add_widget(Label(text="Total Flour:", font_size=dp(13), bold=True))
        self.recipe_total_flour = TextInput(hint_text="0.00", multiline=False, readonly=True, font_size=dp(13), background_color=(0.9, 0.9, 0.9, 1))
        totals_grid.add_widget(self.recipe_total_flour)
        
        totals_grid.add_widget(Label(text="Total Water:", font_size=dp(13), bold=True))
        self.recipe_total_water = TextInput(hint_text="0.00", multiline=False, readonly=True, font_size=dp(13), background_color=(0.9, 0.9, 0.9, 1))
        totals_grid.add_widget(self.recipe_total_water)
        self.form_layout.add_widget(totals_grid)
        
        self.sponge_inputs = {}
        self.dough_inputs = {}
        
        self.build_section_block("A. SPONGE SECTION (PRE-FERMENT)", ["Flour", "Water", "Yeast"], self.sponge_inputs)
        self.build_section_block("B. FINAL DOUGH INGREDIENTS MATRIX", ["Flour", "Water", "Salt", "Yeast", "Sugar", "Butter"], self.dough_inputs)
        
        summary_grid = GridLayout(cols=4, size_hint_y=None, height=dp(40), spacing=dp(5))
        summary_grid.add_widget(Label(text="Matrix Totals Summary:", font_size=dp(12), bold=True))
        self.total_bakers_summary = TextInput(hint_text="0.0%", readonly=True, font_size=dp(12), background_color=(0.9, 0.9, 0.9, 1))
        self.total_true_summary = TextInput(hint_text="0.0%", readonly=True, font_size=dp(12), background_color=(0.9, 0.9, 0.9, 1))
        self.total_weight_summary = TextInput(hint_text="0.00", readonly=True, font_size=dp(12), background_color=(0.9, 0.9, 0.9, 1))
        summary_grid.add_widget(self.total_bakers_summary)
        summary_grid.add_widget(self.total_true_summary)
        summary_grid.add_widget(self.total_weight_summary)
        self.form_layout.add_widget(summary_grid)
        
        scroll_window.add_widget(self.form_layout)
        base_layout.add_widget(scroll_window)
        
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
        
        self.recipe_popup = Popup(title="04. Professional Multi-Section Recipe Formulation Engine Matrix", content=base_layout, size_hint=(0.98, 0.98), auto_dismiss=False)
        close_btn.bind(on_press=self.recipe_popup.dismiss)
        self.recipe_popup.open()

    def build_section_block(self, title, ingredient_list, target_dict):
        self.form_layout.add_widget(Label(text=title, font_size=dp(14), bold=True, size_hint_y=None, height=dp(25), color=(0, 0.7, 1, 1), halign='left'))
        
        header = GridLayout(cols=4, size_hint_y=None, height=dp(30), spacing=dp(5))
        header.add_widget(Label(text="Ingredient Item", font_size=dp(12), bold=True))
        header.add_widget(Label(text="Baker's %", font_size=dp(12), bold=True))
        header.add_widget(Label(text="True %", font_size=dp(12), bold=True))
        header.add_widget(Label(text="Weight (g)", font_size=dp(12), bold=True))
        self.form_layout.add_widget(header)
        
        for name in ingredient_list:
            row = GridLayout(cols=4, size_hint_y=None, height=dp(38), spacing=dp(5))
            row.add_widget(Label(text=name, font_size=dp(13)))
            
            bakers_in = TextInput(hint_text="0.0", multiline=False, input_filter='float', font_size=dp(13))
            true_in = TextInput(hint_text="0.0", multiline=False, input_filter='float', font_size=dp(13))
            weight_in = TextInput(hint_text="0.0", multiline=False, input_filter='float', font_size=dp(13))
            
            bakers_in.bind(text=self.on_manual_field_change)
            true_in.bind(text=self.on_manual_field_change)
            weight_in.bind(text=self.on_manual_field_change)
            
            target_dict[name] = {"bakers": bakers_in, "true": true_in, "weight": weight_in}
            
            row.add_widget(bakers_in)
            row.add_widget(true_in)
            row.add_widget(weight_in)
            self.form_layout.add_widget(row)

    def on_checkbox_toggle(self, checkbox, value):
        if value:
            self.calculate_recipe_matrix()

    def on_manual_field_change(self, instance, text):
        if self.realtime_checkbox.active:
            self.calculate_recipe_matrix()

    def calculate_recipe_matrix(self):
        if self._calculating:
            return
        self._calculating = True
        try:
            total_flour_bakers_sum = 0.0
            sf_bakers = float(self.sponge_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.sponge_inputs else 0.0
            df_bakers = float(self.dough_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.dough_inputs else 0.0
            total_flour_bakers_sum = sf_bakers + df_bakers
            
            if total_flour_bakers_sum == 0:
                total_flour_bakers_sum = 100.0
                
            total_bakers_sum = 0.0
            sponge_has_data = False
            dough_has_data = False
            
            for name, fields in self.sponge_inputs.items():
                try:
                    bp = float(fields["bakers"].text or 0.0)
                    wt = float(fields["weight"].text or 0.0)
                    tp = float(fields["true"].text or 0.0)
                    if bp > 0 or wt > 0 or tp > 0:
                        sponge_has_data = True
                except ValueError: pass
                
            for name, fields in self.dough_inputs.items():
                try:
                    bp = float(fields["bakers"].text or 0.0)
                    wt = float(fields["weight"].text or 0.0)
                    tp = float(fields["true"].text or 0.0)
                    if bp > 0 or wt > 0 or tp > 0:
                        dough_has_data = True
                except ValueError: pass

            for name, fields in self.sponge_inputs.items():
                try: total_bakers_sum += float(fields["bakers"].text or 0.0)
                except ValueError: pass
            for name, fields in self.dough_inputs.items():
                try: total_bakers_sum += float(fields["bakers"].text or 0.0)
                except ValueError: pass
                
            if total_bakers_sum == 0:
                total_bakers_sum = 100.0

            running_true_sum = 0.0
            running_flour_weight = 0.0
            running_water_weight = 0.0
            total_accumulated_weight_all_ingredients = 0.0

            for name, fields in self.sponge_inputs.items():
                try: b_val = float(fields["bakers"].text or 0.0)
                except ValueError: b_val = 0.0
                
                if name == "Water":
                    flour_bakers = float(self.sponge_inputs["Flour"]["bakers"].text or 0.0) if "Flour" in self.sponge_inputs else 0.0
                    t_val = (b_val * flour_bakers) / total_bakers_sum
                else:
                    t_val = (b_val * 100.0) / total_bakers_sum
                    
                running_true_sum += t_val
                if fields["true"].focus is False:
                    fields["true"].text = str(round(t_val, 2)) if t_val > 0 else ""
                    
                try: macro_wt = float(self.recipe_total_weight.text or 0.0)
                except ValueError: macro_wt = 0.0
                
                w_val = (t_val / 100.0) * macro_wt
                total_accumulated_weight_all_ingredients += w_val
                if fields["weight"].focus is False:
                    fields["weight"].text = str(round(w_val, 2)) if w_val > 0 else ""
                    
                if name == "Flour": running_flour_weight += w_val
                if name == "Water": running_water_weight += w_val

            for name, fields in self.dough_inputs.items():
                try: b_val = float(fields["bakers"].text or 0.0)
                except ValueError: b_val = 0.0
                
                t_val = (b_val * 100.0) / total_bakers_sum
                running_true_sum += t_val
                if fields["true"].focus is False:
                    fields["true"].text = str(round(t_val, 2)) if t_val > 0 else ""
                    
                try: macro_wt = float(self.recipe_total_weight.text or 0.0)
                except ValueError: macro_wt = 0.0
                
                w_val = (t_val / 100.0) * macro_wt
                total_accumulated_weight_all_ingredients += w_val
                if fields["weight"].focus is False:
                    fields["weight"].text = str(round(w_val, 2)) if w_val > 0 else ""
                    
                if name == "Flour": running_flour_weight += w_val
                if name == "Water": running_water_weight += w_val

            self.recipe_total_flour.text = str(round(running_flour_weight, 2))
            self.recipe_total_water.text = str(round(running_water_weight, 2))
            
            if len(self.recipe_total_weight.text) == 0:
                self.recipe_total_weight.text = str(round(total_accumulated_weight_all_ingredients, 2))
                
            self.total_bakers_summary.text = str(round(total_bakers_sum, 2))
            self.total_true_summary.text = str(round(running_true_sum, 2))
            self.total_weight_summary.text = str(round(total_accumulated_weight_all_ingredients, 2))
            
            error_bg = [0.6, 0.1, 0.1, 1]
            if running_true_sum > 0 and not (99.0 <= round(running_true_sum, 2) <= 100.01):
                self.total_true_summary.background_color = error_bg
                self.total_true_summary.color = [1, 1, 1, 1]
            else:
                self.total_true_summary.background_color = [0.85, 0.92, 0.98, 1]
                self.total_true_summary.color = [0, 0, 0, 1]
        finally:
            self._calculating = False

    # --- SAVE PROFILE WORKFLOW ENGINE ---
    def trigger_save_workflow(self, instance):
        valid_rows = []
        filled_count = 0
        
        for name, target in [("Sponge", self.sponge_inputs), ("Dough", self.dough_inputs)]:
            for ing_name, fields in target.items():
                bp = fields["bakers"].text
                tp = fields["true"].text
                wt = fields["weight"].text
                if bp or tp or wt:
                    filled_count += 1
                    valid_rows.append((name, ing_name, bp or "0.00", tp or "0.00", wt or "0.00"))
                    
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
        cols_config = [("Sec", 0.15), ("Item", 0.25), ("Bak%", 0.2), ("Tru%", 0.2), ("Wt(g)", 0.2)]
        for h_text, h_sz in cols_config:
            table_header.add_widget(Label(text=h_text, font_size=dp(11), bold=True))
        save_layout.add_widget(table_header)
        
        preview_scroll = ScrollView(size_hint=(1, 0.5))
        preview_grid = GridLayout(cols=5, size_hint_y=None, spacing=dp(2))
        preview_grid.bind(minimum_height=preview_grid.setter('height'))
        
        for sec, item, b, t, w in valid_rows:
            preview_grid.add_widget(Label(text=sec, font_size=dp(11)))
            preview_grid.add_widget(Label(text=item, font_size=dp(11)))
            preview_grid.add_widget(Label(text=str(b), font_size=dp(11)))
            preview_grid.add_widget(Label(text=str(t), font_size=dp(11)))
            preview_grid.add_widget(Label(text=str(w), font_size=dp(11)))
        preview_scroll.add_widget(preview_grid)
        save_layout.add_widget(preview_scroll)
        
        input_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        input_row.add_widget(Label(text="Recipe Key Name:", size_hint_x=0.35, font_size=dp(14)))
        recipe_name_input = TextInput(hint_text="e.g., Artisan Sourdough V1", multiline=False, font_size=dp(14))
        input_row.add_widget(recipe_name_input)
        save_layout.add_widget(input_row)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        confirm_btn = Button(text="Commit Save", background_color=(0.15, 0.65, 0.35, 1), font_size=dp(14), bold=True)
        cancel_btn = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(14))
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        save_layout.add_widget(btn_layout)
        
        save_popup = Popup(title="Confirm Serialization Structure", content=save_layout, size_hint=(0.96, 0.9), auto_dismiss=False)
        cancel_btn.bind(on_press=save_popup.dismiss)
        
        def commit_to_database_instance(btn_obj):
            name_key = recipe_name_input.text.strip()
            if not name_key:
                recipe_name_input.hint_text = "REQUIRED FIELD NAME!"
                return
                
            payload = {
                "top_totals": {
                    "weight": self.recipe_total_weight.text,
                    "flour": self.recipe_total_flour.text,
                    "water": self.recipe_total_water.text
                },
                "bottom_totals": {
                    "bakers": self.total_bakers_summary.text,
                    "true": self.total_true_summary.text,
                    "weight": self.total_weight_summary.text
                },
                "matrix_data": valid_rows
            }
            
            self.saved_recipes_db[name_key] = payload
            self.save_recipes_to_disk()  # Permanent Storage Write
            self.recipe_title_label.text = f"Active Recipe: {name_key}"
            save_popup.dismiss()
            
        confirm_btn.bind(on_press=commit_to_database_instance)
        save_popup.open()

    # --- LOAD MANAGEMENT SYSTEM (RECIPE LIST POPUP) ---
    def trigger_load_list_popup(self, instance):
        self.load_recipes_from_disk()  # Always read fresh data from disk before displaying list
        
        main_box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        if not self.saved_recipes_db:
            main_box.add_widget(Label(text="No serialized recipes stored in local cache.", font_size=dp(14)))
            close_btn = Button(text="Close", size_hint_y=None, height=dp(45), background_color=(0.8, 0.2, 0.2, 1))
            main_box.add_widget(close_btn)
            list_popup = Popup(title="Database Browser", content=main_box, size_hint=(0.9, 0.6))
            close_btn.bind(on_press=list_popup.dismiss)
            list_popup.open()
            return

        scroll = ScrollView(size_hint=(1, 0.85))
        list_grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        list_grid.bind(minimum_height=list_grid.setter('height'))
        
        list_popup = Popup(title="Select Recipe Profile from Local DB", content=main_box, size_hint=(0.95, 0.95))
        
        # Build individual recipe row list items containing Load and Delete triggers
        for key in sorted(self.saved_recipes_db.keys()):
            row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(5))
            
            recipe_btn = Button(text=f"Profile: {key}", halign='left', valign='middle', font_size=dp(13), size_hint_x=0.75)
            recipe_btn.bind(size=recipe_btn.setter('text_size'))
            # Nested function layout safely preserves active row element references
            recipe_btn.bind(on_press=lambda b, k=key: self.open_recipe_preview(k, list_popup))
            row_layout.add_widget(recipe_btn)
            
            del_btn = Button(text="Delete", background_color=(0.8, 0.2, 0.2, 1), size_hint_x=0.25, font_size=dp(13))
            del_btn.bind(on_press=lambda b, k=key: self.delete_recipe_workflow(k, list_popup))
            row_layout.add_widget(del_btn)
            
            list_grid.add_widget(row_layout)
            
        scroll.add_widget(list_grid)
        main_box.add_widget(scroll)
        
        close_btn = Button(text="Back to Matrix Panel", size_hint_y=None, height=dp(45))
        close_btn.bind(on_press=list_popup.dismiss)
        main_box.add_widget(close_btn)
        
        list_popup.open()

    # --- DELETE RECIPE WORKFLOW ENGINE ---
    def delete_recipe_workflow(self, recipe_key, parent_popup_to_close):
        confirm_box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        confirm_box.add_widget(Label(text=f"Permanently delete recipe:\n'{recipe_key}'?", font_size=dp(14), halign='center'))
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        yes_btn = Button(text="Yes, Delete", background_color=(0.8, 0.2, 0.2, 1))
        no_btn = Button(text="Cancel")
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        confirm_box.add_widget(btn_layout)
        
        del_popup = Popup(title="Confirm Deletion", content=confirm_box, size_hint=(0.8, 0.35))
        no_btn.bind(on_press=del_popup.dismiss)
        
        def execute_delete(instance):
            if recipe_key in self.saved_recipes_db:
                del self.saved_recipes_db[recipe_key]
                self.save_recipes_to_disk()  # Sync permanent record file immediately
                if self.recipe_title_label.text == f"Active Recipe: {recipe_key}":
                    self.recipe_title_label.text = "Active Recipe: Unsaved System Instance"
            del_popup.dismiss()
            parent_popup_to_close.dismiss()
            self.trigger_load_list_popup(None) # Refresh list view dynamically
            
        yes_btn.bind(on_press=execute_delete)
        del_popup.open()

    # --- SUB-WINDOW RECIPE PROFILE PREVIEW ---
    def open_recipe_preview(self, recipe_key, primary_popup):
        record_profile = self.saved_recipes_db[recipe_key]
        preview_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        preview_layout.add_widget(Label(text=f"Profile View: {recipe_key}", bold=True, size_hint_y=None, height=dp(25), color=(0, 0.7, 1, 1)))
        
        totals_display_grid = GridLayout(cols=3, size_hint_y=None, height=dp(35), spacing=dp(5))
        totals_display_grid.add_widget(Label(text=f"Wt: {record_profile['top_totals']['weight']}", font_size=dp(12)))
        totals_display_grid.add_widget(Label(text=f"Flour: {record_profile['top_totals']['flour']}", font_size=dp(12)))
        totals_display_grid.add_widget(Label(text=f"Water: {record_profile['top_totals']['water']}", font_size=dp(12)))
        preview_layout.add_widget(totals_display_grid)
        
        preview_scroll = ScrollView(size_hint=(1, 0.55))
        data_grid = GridLayout(cols=5, size_hint_y=None, spacing=dp(3))
        data_grid.bind(minimum_height=data_grid.setter('height'))
        
        cols_config = [("Sec", 0.15), ("Item", 0.25), ("Bak%", 0.2), ("Tru%", 0.2), ("Wt(g)", 0.2)]
        for h_text, _ in cols_config:
            data_grid.add_widget(Label(text=h_text, font_size=dp(11), bold=True))
            
        for row in record_profile["matrix_data"]:
            for cell in row:
                data_grid.add_widget(Label(text=str(cell), font_size=dp(11)))
                
        preview_scroll.add_widget(data_grid)
        preview_layout.add_widget(preview_scroll)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        confirm_load_btn = Button(text="Inject Formulation into Grid", background_color=(0.15, 0.45, 0.65, 1), font_size=dp(13), bold=True)
        view_del_btn = Button(text="Delete Recipe", background_color=(0.8, 0.2, 0.2, 1), font_size=dp(13))
        cancel_btn = Button(text="Back", font_size=dp(13))
        
        btn_layout.add_widget(confirm_load_btn)
        btn_layout.add_widget(view_del_btn)
        btn_layout.add_widget(cancel_btn)
        preview_layout.add_widget(btn_layout)
        
        preview_popup = Popup(title="Formula Inspection Sandbox Profile", content=preview_layout, size_hint=(0.96, 0.92), auto_dismiss=False)
        cancel_btn.bind(on_press=preview_popup.dismiss)
        
        # Connect the view page delete button to our core delete workflow
        view_del_btn.bind(on_press=lambda b: [preview_popup.dismiss(), self.delete_recipe_workflow(recipe_key, primary_popup)])

        def inject_recipe_to_main_screen(btn_instance):
            self._calculating = True
            try:
                for target_dict in [self.sponge_inputs, self.dough_inputs]:
                    for name in target_dict:
                        target_dict[name]["bakers"].text = ""
                        target_dict[name]["true"].text = ""
                        target_dict[name]["weight"].text = ""
                        
                for section, name, bp, tp, wt in record_profile["matrix_data"]:
                    target_dict = self.sponge_inputs if section == "Sponge" else self.dough_inputs
                    if name not in target_dict:
                        continue
                    target_dict[name]["bakers"].text = bp if float(bp or 0) > 0 else ""
                    target_dict[name]["true"].text = tp if float(tp or 0) > 0 else ""
                    target_dict[name]["weight"].text = wt if float(wt or 0) > 0 else ""

                self.recipe_total_weight.text = record_profile["top_totals"]["weight"]
                self.recipe_total_flour.text = record_profile["top_totals"]["flour"]
                self.recipe_total_water.text = record_profile["top_totals"]["water"]

                self.total_bakers_summary.text = record_profile["bottom_totals"]["bakers"]
                self.total_true_summary.text = record_profile["bottom_totals"]["true"]
                self.total_weight_summary.text = record_profile["bottom_totals"]["weight"]
                
                self.recipe_title_label.text = f"Active Recipe: {recipe_key}"
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
