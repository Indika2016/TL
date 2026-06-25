import asyncio
import json
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
from kivy.core.window import Window
from kivy.metrics import dp

# Force responsive window adjustments for desktop/browser environments
Window.keyboard_behavior = 'managed'

# Shared persistent states
last_calculated_ff = 0.0
last_calculated_wt = 0.0
saved_recipes_db = {}

def load_recipes_from_disk():
    global saved_recipes_db
    try:
        with open("recipes_db.json", "r") as f:
            saved_recipes_db = json.load(f)
    except:
        saved_recipes_db = {
            "Classic Sourdough": {
                "rows": [
                    {"name": "Bread Flour", "bakers": "100", "true": "56.18", "weight": "1000"},
                    {"name": "Water", "bakers": "75", "true": "42.13", "weight": "750"},
                    {"name": "Salt", "bakers": "2", "true": "1.12", "weight": "20"},
                    {"name": "Sourdough Starter", "bakers": "10", "true": "5.62", "weight": "100"}
                ],
                "top_totals": {"weight": "1870.00", "flour": "1000.00", "water": "750.00"},
                "bottom_totals": {"bakers": "187.00", "true": "105.05", "weight": "1870.00"}
            }
        }

def save_recipes_to_disk():
    try:
        with open("recipes_db.json", "w") as f:
            json.dump(saved_recipes_db, f, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")

# --- SCREEN 1: LOGIN ---
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=dp(24))
        login_box = BoxLayout(orientation='vertical', spacing=dp(14), size_hint=(0.85, None))
        login_box.bind(minimum_height=login_box.setter('height'))
        
        login_box.add_widget(Label(text="BAKERY SCIENCE", font_size=dp(26), bold=True, color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(45)))
        
        self.username = TextInput(hint_text="Username", multiline=False, font_size=dp(16), size_hint_y=None, height=dp(45), write_tab=False)
        self.password = TextInput(hint_text="Password", password=True, multiline=False, font_size=dp(16), size_hint_y=None, height=dp(45), write_tab=False)
        
        login_box.add_widget(self.username)
        login_box.add_widget(self.password)
        
        btn_login = Button(text="LOGIN", background_color=(0, 0.6, 1, 1), color=(1, 1, 1, 1), font_size=dp(16), bold=True, size_hint_y=None, height=dp(50))
        btn_login.bind(on_press=self.validate_login)
        login_box.add_widget(btn_login)
        
        root_anchor.add_widget(login_box)
        self.add_widget(root_anchor)

    def validate_login(self, instance):
        if self.username.text.strip() != "" and self.password.text.strip() != "":
            self.manager.current = 'dashboard'

# --- SCREEN 2: DASHBOARD ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_recipes_from_disk()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(12))
        
        # Header Row
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        header.add_widget(Label(text="Dashboard", font_size=dp(22), bold=True, halign='left', valign='middle', size_hint_x=0.7))
        btn_logout = Button(text="Logout", size_hint_x=0.3, background_color=(0.9, 0.3, 0.3, 1), font_size=dp(14))
        btn_logout.bind(on_press=self.logout)
        header.add_widget(btn_logout)
        main_layout.add_widget(header)
        
        # Grid Menu Modules
        menu_grid = GridLayout(cols=1, spacing=dp(12), size_hint_y=1)
        
        b1 = Button(text="01. Friction Factor (FF)", font_size=dp(16), bold=True, background_color=(0.1, 0.5, 0.8, 1))
        b1.bind(on_press=self.open_ff_calculator)
        
        b2 = Button(text="02. Water Temp. Calculator", font_size=dp(16), bold=True, background_color=(0.1, 0.5, 0.8, 1))
        b2.bind(on_press=self.open_water_calculator)
        
        b3 = Button(text="03. Ice Substitution", font_size=dp(16), bold=True, background_color=(0.1, 0.5, 0.8, 1))
        b3.bind(on_press=self.open_ice_calculator)
        
        # CHANGED: Box 04 Page Renamed to Recipe Calculation Matrix
        b4 = Button(text="04. Recipe Calculation Matrix", font_size=dp(16), bold=True, background_color=(0.1, 0.6, 0.5, 1))
        b4.bind(on_press=self.open_recipe_matrix)
        
        menu_grid.add_widget(b1)
        menu_grid.add_widget(menu_grid.add_widget(b2) or b3)
        menu_grid.add_widget(b4)
        
        main_layout.add_widget(menu_grid)
        self.add_widget(main_layout)

    # --- POPUP LAYOUT GENERATORS AND LOGIC ---
    def open_ff_calculator(self, instance):
        layout = GridLayout(cols=2, spacing=dp(10), padding=dp(15))
        layout.add_widget(Label(text="01. Room Temp (RT):", font_size=dp(14)))
        rt_in = TextInput(text="24", input_filter='float', multiline=False)
        layout.add_widget(rt_in)
        
        layout.add_widget(Label(text="02. Flour Temp (FT):", font_size=dp(14)))
        ft_in = TextInput(text="22", input_filter='float', multiline=False)
        layout.add_widget(ft_in)
        
        layout.add_widget(Label(text="03. Water Temp (WT):", font_size=dp(14)))
        wt_in = TextInput(text="18", input_filter='float', multiline=False)
        layout.add_widget(wt_in)
        
        layout.add_widget(Label(text="04. Actual DDT:", font_size=dp(14)))
        ddt_in = TextInput(text="26", input_filter='float', multiline=False)
        layout.add_widget(ddt_in)
        
        result_lbl = Label(text="Calculated FF: --", bold=True, color=(0, 1, 0.5, 1), font_size=dp(15))
        layout.add_widget(result_lbl)
        
        def calc_ff(obj):
            try:
                ff = (float(ddt_in.text) * 3) - (float(rt_in.text) + float(ft_in.text) + float(wt_in.text))
                global last_calculated_ff
                last_calculated_ff = max(0.0, ff)
                result_lbl.text = f"Calculated FF: {last_calculated_ff:.2f}°C"
            except:
                result_lbl.text = "Invalid Inputs"
                
        btn_calc = Button(text="Calculate", background_color=(0, 0.7, 0.4, 1))
        btn_calc.bind(on_press=calc_ff)
        layout.add_widget(btn_calc)
        
        Popup(title="Friction Factor Engine", content=layout, size_hint=(0.9, 0.65)).open()

    def open_water_calculator(self, instance):
        layout = GridLayout(cols=2, spacing=dp(10), padding=dp(15))
        layout.add_widget(Label(text="01. Desired DDT:", font_size=dp(14)))
        ddt_in = TextInput(text="25", input_filter='float', multiline=False)
        layout.add_widget(ddt_in)
        
        layout.add_widget(Label(text="02. Room Temp (RT):", font_size=dp(14)))
        rt_in = TextInput(text="24", input_filter='float', multiline=False)
        layout.add_widget(rt_in)
        
        layout.add_widget(Label(text="03. Flour Temp (FT):", font_size=dp(14)))
        ft_in = TextInput(text="22", input_filter='float', multiline=False)
        layout.add_widget(ft_in)
        
        layout.add_widget(Label(text="04. Sp.T (Optional):", font_size=dp(14)))
        spt_in = TextInput(hint_text="Blank if none", input_filter='float', multiline=False)
        layout.add_widget(spt_in)
        
        layout.add_widget(Label(text="05. FF:", font_size=dp(14)))
        ff_in = TextInput(text=str(last_calculated_ff), input_filter='float', multiline=False)
        layout.add_widget(ff_in)
        
        result_lbl = Label(text="Cal WT: --", bold=True, color=(0, 1, 0.5, 1), font_size=dp(15))
        layout.add_widget(result_lbl)
        
        def calc_wt(obj):
            try:
                ddt, rt, ft, ff = float(ddt_in.text), float(rt_in.text), float(ft_in.text), float(ff_in.text)
                if spt_in.text.strip() == "":
                    wt = (3 * ddt) - rt - ft - ff
                else:
                    wt = (4 * ddt) - (rt + ft + float(spt_in.text) + ff)
                global last_calculated_wt
                last_calculated_wt = wt
                result_lbl.text = f"Cal WT: {last_calculated_wt:.2f}°C"
            except:
                result_lbl.text = "Invalid Inputs"
                
        btn_calc = Button(text="Calculate", background_color=(0, 0.7, 0.4, 1))
        btn_calc.bind(on_press=calc_wt)
        layout.add_widget(btn_calc)
        
        Popup(title="Water Temp Calculator Engine", content=layout, size_hint=(0.9, 0.75)).open()

    def open_ice_calculator(self, instance):
        layout = GridLayout(cols=2, spacing=dp(10), padding=dp(15))
        layout.add_widget(Label(text="Total Water Wt:", font_size=dp(14)))
        tot_w = TextInput(text="500", input_filter='float', multiline=False)
        layout.add_widget(tot_w)
        
        layout.add_widget(Label(text="Tap Water Temp:", font_size=dp(14)))
        tap_t = TextInput(text="22", input_filter='float', multiline=False)
        layout.add_widget(tap_t)
        
        layout.add_widget(Label(text="Target Water Temp:", font_size=dp(14)))
        tgt_t = TextInput(text=str(max(0.0, last_calculated_wt)) if last_calculated_wt != 0 else "12", input_filter='float', multiline=False)
        layout.add_widget(tgt_t)
        
        result_lbl = GridLayout(cols=1, size_hint_y=None, height=dp(50))
        lbl_ice = Label(text="Ice Weight: --", bold=True, color=(0, 0.8, 1, 1), font_size=dp(14))
        lbl_water = Label(text="Water Weight: --", bold=True, color=(1, 1, 1, 1), font_size=dp(14))
        result_lbl.add_widget(lbl_ice)
        result_lbl.add_widget(lbl_water)
        layout.add_widget(result_lbl)
        
        def calc_ice(obj):
            try:
                w_tot = float(tot_w.text)
                t_tap = float(tap_t.text)
                t_tgt = float(tgt_t.text)
                ice = (w_tot * (t_tap - t_tgt)) / (80 + t_tap)
                if ice < 0: ice = 0
                lbl_ice.text = f"Ice Weight: {ice:.1f} g"
                lbl_water.text = f"Water Weight: {(w_tot - ice):.1f} g"
            except:
                lbl_ice.text = "Error in parsing parameters"
                
        btn_calc = Button(text="Calculate Ice", background_color=(0, 0.7, 0.4, 1))
        btn_calc.bind(on_press=calc_ice)
        layout.add_widget(btn_calc)
        
        Popup(title="Ice Substitution Engine", content=layout, size_hint=(0.9, 0.65)).open()

    def open_recipe_matrix(self, instance):
        # CHANGED: Master layout designated as Recipe Calculation Matrix page layout
        primary_popup = Popup(title="Recipe Calculation Matrix Dashboard", size_hint=(0.95, 0.95))
        outer_container = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        
        self.recipe_title_label = Label(text="Active Recipe: Scratchpad Matrix", font_size=dp(16), bold=True, size_hint_y=None, height=dp(30), color=(0, 0.8, 1, 1))
        outer_container.add_widget(self.recipe_title_label)
        
        # Matrix Header
        matrix_header = GridLayout(cols=4, size_hint_y=None, height=dp(35), spacing=dp(4))
        matrix_header.add_widget(Label(text="Ingredient Name", bold=True, font_size=dp(12)))
        matrix_header.add_widget(Label(text="Baker's %", bold=True, font_size=dp(12)))
        matrix_header.add_widget(Label(text="True %", bold=True, font_size=dp(12)))
        matrix_header.add_widget(Label(text="Weight (g)", bold=True, font_size=dp(12)))
        outer_container.add_widget(matrix_header)
        
        # Interactive Grid Rows Setup
        scroll_window = ScrollView(size_hint=(1, 0.55))
        self.matrix_grid = GridLayout(cols=4, spacing=dp(4), size_hint_y=None)
        self.matrix_grid.bind(minimum_height=self.matrix_grid.setter('height'))
        
        self.target_dict = {}
        ingredient_presets = ["Bread Flour", "Whole Wheat Flour", "Water", "Salt", "Yeast", "Inclusions"]
        
        for name in ingredient_presets:
            lbl = Label(text=name, font_size=dp(12), halign='center', short_content=True)
            bp_input = TextInput(text="100" if "Bread Flour" in name else "", input_filter='float', multiline=False, font_size=dp(13))
            tp_input = TextInput(input_filter='float', multiline=False, font_size=dp(13))
            wt_input = TextInput(input_filter='float', multiline=False, font_size=dp(13))
            
            bp_input.bind(text=lambda instance, val, n=name: self.on_matrix_cell_change(n, 'bakers', val))
            tp_input.bind(text=lambda instance, val, n=name: self.on_matrix_cell_change(n, 'true', val))
            wt_input.bind(text=lambda instance, val, n=name: self.on_matrix_cell_change(n, 'weight', val))
            
            self.matrix_grid.add_widget(lbl)
            self.matrix_grid.add_widget(bp_input)
            self.matrix_grid.add_widget(tp_input)
            self.matrix_grid.add_widget(wt_input)
            
            self.target_dict[name] = {"label": lbl, "bakers": bp_input, "true": tp_input, "weight": wt_input}
            
        scroll_window.add_widget(self.matrix_grid)
        outer_container.add_widget(scroll_window)
        
        # Real-time computation footer labels
        summary_panel = GridLayout(cols=4, size_hint_y=None, height=dp(40), spacing=dp(4))
        summary_panel.add_widget(Label(text="Totals Summary:", bold=True, font_size=dp(11)))
        self.total_bakers_summary = Label(text="0.0%", font_size=dp(12), bold=True)
        self.total_true_summary = Label(text="0.0%", font_size=dp(12), bold=True)
        self.total_weight_summary = Label(text="0g", font_size=dp(12), bold=True)
        summary_panel.add_widget(self.total_bakers_summary)
        summary_panel.add_widget(self.total_true_summary)
        summary_panel.add_widget(self.total_weight_summary)
        outer_container.add_widget(summary_panel)
        
        # Interactive Action Matrix Row
        action_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(6))
        btn_save_rec = Button(text="Save Matrix", background_color=(0, 0.6, 0.9, 1), font_size=dp(13))
        btn_save_rec.bind(on_press=lambda idx: self.trigger_save_recipe_popup())
        
        btn_load_rec = Button(text="Open Database", background_color=(0.1, 0.7, 0.3, 1), font_size=dp(13))
        btn_load_rec.bind(on_press=lambda idx: self.trigger_load_list_popup(primary_popup))
        
        btn_close_matrix = Button(text="Exit", background_color=(0.8, 0.3, 0.3, 1), font_size=dp(13))
        btn_close_matrix.bind(on_press=primary_popup.dismiss)
        
        action_row.add_widget(btn_save_rec)
        action_row.add_widget(btn_load_rec)
        action_row.add_widget(btn_close_matrix)
        outer_container.add_widget(action_row)
        
        primary_popup.content = outer_container
        primary_popup.open()
        self.calculate_recipe_matrix()

    _calculating = False
    def on_matrix_cell_change(self, ingredient_name, cell_type, values):
        if self._calculating: return
        self.calculate_recipe_matrix(trigger_source=(ingredient_name, cell_type))

    def calculate_recipe_matrix(self, trigger_source=None):
        self._calculating = True
        try:
            total_flour_weight = 0.0
            total_bakers_pct = 0.0
            total_true_pct = 0.0
            total_dough_weight = 0.0
            
            # Find running scaling keys based on entered elements
            for name, fields in self.target_dict.items():
                w_val = float(fields["weight"].text or 0)
                b_val = float(fields["bakers"].text or 0)
                if "Flour" in name and w_val > 0:
                    total_flour_weight += w_val
                if b_val > 0:
                    total_bakers_pct += b_val
                    
            if trigger_source and total_flour_weight == 0:
                src_name, src_type = trigger_source
                src_val = float(self.target_dict[src_name][src_type].text or 0)
                if src_type == "weight" and src_val > 0:
                    src_bp = float(self.target_dict[src_name]["bakers"].text or 0)
                    if src_bp > 0:
                        total_flour_weight = (src_val / src_bp) * 100
                        
            if total_flour_weight > 0:
                for name, fields in self.target_dict.items():
                    b_val = float(fields["bakers"].text or 0)
                    if b_val > 0 and (trigger_source is None or trigger_source[1] != 'weight'):
                        calc_w = (b_val / 100) * total_flour_weight
                        fields["weight"].text = f"{calc_w:.2f}"
                        
            # Sum dynamic columns securely
            calc_total_wt = 0.0
            for name, fields in self.target_dict.items():
                calc_total_wt += float(fields["weight"].text or 0)
                
            if calc_total_wt > 0:
                self.total_weight_summary.text = f"{calc_total_wt:.1f}g"
                for name, fields in self.target_dict.items():
                    w_val = float(fields["weight"].text or 0)
                    calculated_true = (w_val / calc_total_wt) * 100
                    fields["true"].text = f"{calculated_true:.1f}" if calculated_true > 0 else ""
                    
                    if fields["bakers"].text == "" and total_flour_weight > 0 and w_val > 0:
                        fields["bakers"].text = f"{((w_val / total_flour_weight) * 100):.1f}"
            else:
                self.total_weight_summary.text = "0.0g"
        finally:
            self._calculating = False

    def trigger_save_recipe_popup(self):
        box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        box.add_widget(Label(text="Enter Unique Recipe Key ID:", font_size=dp(14)))
        name_in = TextInput(hint_text="e.g., Artisan Sourdough Batch A", multiline=False)
        box.add_widget(name_in)
        
        save_popup = Popup(title="Commit Matrix State to Disk", content=box, size_hint=(0.85, 0.4))
        
        def commit_save_workflow(obj):
            r_name = name_in.text.strip()
            if not r_name: return
            
            serialized_rows = []
            for name, fields in self.target_dict.items():
                serialized_rows.append({
                    "name": name,
                    "bakers": fields["bakers"].text,
                    "true": fields["true"].text,
                    "weight": fields["weight"].text
                })
                
            saved_recipes_db[r_name] = {
                "rows": serialized_rows,
                "top_totals": {"weight": self.total_weight_summary.text, "flour": "1000", "water": "700"},
                "bottom_totals": {"bakers": self.total_bakers_summary.text, "true": self.total_true_summary.text, "weight": self.total_weight_summary.text}
            }
            save_recipes_to_disk()
            save_popup.dismiss()
            
        btn = Button(text="Save Recipe", background_color=(0, 0.6, 1, 1))
        btn.bind(on_press=commit_save_workflow)
        box.add_widget(btn)
        save_popup.open()

    def trigger_load_list_popup(self, primary_popup):
        list_container = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        scroll = ScrollView()
        scroll_grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        scroll_grid.bind(minimum_height=scroll_grid.setter('height'))
        
        list_popup = Popup(title="Local Recipe Library Database", content=list_container, size_hint=(0.9, 0.85))
        
        def delete_recipe_workflow(recipe_key, row_widget):
            if recipe_key in saved_recipes_db:
                del saved_recipes_db[recipe_key]
                save_recipes_to_disk()
                scroll_grid.remove_widget(row_widget)
                if self.recipe_title_label.text == f"Active Recipe: {recipe_key}":
                    self.recipe_title_label.text = "Active Recipe: Scratchpad Matrix"
                    
        for r_key in list(saved_recipes_db.keys()):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(6))
            
            btn_load = Button(text=r_key, halign='left', size_hint_x=0.75, background_color=(0.2, 0.3, 0.4, 1))
            btn_load.bind(on_press=lambda idx, k=r_key: self.inject_recipe_to_matrix_canvas(k, list_popup, primary_popup))
            
            btn_del = Button(text="X", size_hint_x=0.25, background_color=(0.9, 0.2, 0.2, 1), font_size=dp(14), bold=True)
            btn_del.bind(on_press=lambda idx, k=r_key, r=row: delete_recipe_workflow(k, r))
            
            row.add_widget(btn_load)
            row.add_widget(btn_del)
            scroll_grid.add_widget(row)
            
        scroll.add_widget(scroll_grid)
        list_container.add_widget(scroll)
        
        btn_close = Button(text="Back", size_hint_y=None, height=dp(45), background_color=(0.5, 0.5, 0.5, 1))
        btn_close.bind(on_press=list_popup.dismiss)
        list_container.add_widget(btn_close)
        list_popup.open()

    def inject_recipe_to_matrix_canvas(self, recipe_key, list_popup, primary_popup):
        self._calculating = True
        try:
            record_profile = saved_recipes_db[recipe_key]
            for row_item in record_profile["rows"]:
                name = row_item["name"]
                if name in self.target_dict:
                    self.target_dict[name]["bakers"].text = row_item["bakers"]
                    self.target_dict[name]["true"].text = row_item["true"]
                    self.target_dict[name]["weight"].text = row_item["weight"]
                    
            self.total_weight_summary.text = record_profile["bottom_totals"]["weight"]
            self.recipe_title_label.text = f"Active Recipe: {recipe_key}"
        finally:
            self._calculating = False
            
        self.calculate_recipe_matrix()
        list_popup.dismiss()

    def logout(self, instance):
        self.manager.current = 'login'

# --- MAIN APP EXECUTION ---
class MyMainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    # Standard web-optimized execution loop framework wrapper
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyMainApp().async_run())
