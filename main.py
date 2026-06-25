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
import json
import os

# Global variables to pass results between popup engines dynamically
last_calculated_ff = 0.0
last_calculated_wt = 0.0

# =============================================================================
# SHARED STYLE CONSTANTS  – single source of truth for all GUI sizing
# =============================================================================
ROW_H        = dp(44)   # standard input-row height across all popups
BTN_H        = dp(48)   # standard action-button bar height
FIELD_FS     = dp(15)   # font size for all TextInput fields
LABEL_FS     = dp(15)   # font size for row labels
BTN_FS       = dp(15)   # font size for all buttons
HEADER_FS    = dp(16)   # section header label font size
TITLE_FS     = dp(16)   # popup title-bar label font size
SMALL_FS     = dp(13)   # small labels / grid cells
SECTION_H    = dp(34)   # section header row height
GRID_ROW_H   = dp(40)   # recipe grid ingredient row height
SUMMARY_H    = dp(42)   # summary / totals row height
PAD          = dp(14)   # standard popup padding
SPACING      = dp(10)   # standard spacing between rows
POPUP_TITLE_SIZE = dp(17)   # consistent title font across all popups
POPUP_SEP_H      = dp(2)    # thin separator line under title
POPUP_TOP_PAD    = dp(8)    # extra breathing room below title bar


# =============================================================================
# SCREEN 1: LOGIN
# =============================================================================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root_anchor = AnchorLayout(anchor_x='center', anchor_y='center', padding=dp(24))
        login_box = BoxLayout(orientation='vertical', spacing=dp(14), size_hint=(0.85, None))
        login_box.bind(minimum_height=login_box.setter('height'))

        login_box.add_widget(Label(
            text="WELCOME", font_size=dp(28), bold=True,
            color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(52)
        ))

        self.username = TextInput(
            hint_text="Username", multiline=False,
            font_size=dp(16), size_hint_y=None, height=dp(46),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        login_box.add_widget(self.username)

        self.password = TextInput(
            hint_text="Password", password=True, multiline=False,
            font_size=dp(16), size_hint_y=None, height=dp(46),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        login_box.add_widget(self.password)

        btn = Button(
            text="LOGIN", font_size=dp(18), bold=True,
            background_color=(0, 0.7, 1, 1), size_hint_y=None, height=dp(50)
        )
        btn.bind(on_press=self.check_login)
        login_box.add_widget(btn)

        self.error_msg = Label(
            text="", color=(1, 0, 0, 1),
            font_size=dp(14), size_hint_y=None, height=dp(30)
        )
        login_box.add_widget(self.error_msg)

        root_anchor.add_widget(login_box)
        self.add_widget(root_anchor)

    def check_login(self, instance):
        if self.username.text == "admin" and self.password.text == "123":
            self.manager.current = 'dashboard'
        else:
            self.error_msg.text = "Try again! (admin / 123)"


# =============================================================================
# SCREEN 2: DASHBOARD
# =============================================================================
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.recipes_db_file = "recipes_db.json"
        try:
            if os.path.exists(self.recipes_db_file):
                with open(self.recipes_db_file, "r", encoding="utf-8") as f:
                    self.saved_recipes_db = json.load(f)
            else:
                self.saved_recipes_db = {}
        except (json.JSONDecodeError, OSError, ValueError):
            self.saved_recipes_db = {}
        self._calculating = False

        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        main_layout.add_widget(Label(
            text="Select Calculator", font_size=dp(24), bold=True, size_hint_y=0.15
        ))

        grid = GridLayout(cols=2, rows=2, spacing=dp(16), size_hint_y=0.7)

        btn1 = Button(text="01.\nFF Calculator",         halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.5, 0.8, 1))
        btn2 = Button(text="02.\nWater Temp.\nCalculator", halign='center', valign='middle', font_size=dp(18), background_color=(0.1, 0.6, 0.6, 1))
        btn3 = Button(text="03.\nIce Temp.\nCalculator",  halign='center', valign='middle', font_size=dp(18), background_color=(0.2, 0.5, 0.7, 1))
        btn4 = Button(text="04.\nRecipe\nCalculator",     halign='center', valign='middle', font_size=dp(18), background_color=(0.3, 0.4, 0.6, 1))

        for b in [btn1, btn2, btn3, btn4]:
            b.bind(size=b.setter('text_size'))

        btn1.bind(on_press=self.open_ff_popup)
        btn2.bind(on_press=self.open_water_temp_popup)
        btn3.bind(on_press=self.open_ice_temp_popup)
        btn4.bind(on_press=self.open_recipe_popup)

        for b in [btn1, btn2, btn3, btn4]:
            grid.add_widget(b)

        main_layout.add_widget(grid)

        logout_btn = Button(
            text="Logout", size_hint_y=0.15,
            font_size=dp(16), bold=True, background_color=(0.8, 0.2, 0.2, 1)
        )
        logout_btn.bind(on_press=self.logout)
        main_layout.add_widget(logout_btn)

        self.add_widget(main_layout)

    # -------------------------------------------------------------------------
    # HELPER: build a uniform labelled input row
    # -------------------------------------------------------------------------
    def _make_row(self, label_text, widget, label_hint_x=0.4):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_H, spacing=SPACING)
        lbl = Label(
            text=label_text, font_size=LABEL_FS,
            size_hint_x=label_hint_x, halign='left', valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        row.add_widget(lbl)
        row.add_widget(widget)
        return row

    # -------------------------------------------------------------------------
    # HELPER: build a uniform action button bar
    # -------------------------------------------------------------------------
    def _make_action_bar(self, *buttons):
        bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=BTN_H, spacing=SPACING)
        for b in buttons:
            bar.add_widget(b)
        return bar

    # =========================================================================
    # POPUP 01: FF CALCULATOR
    # =========================================================================
    def open_ff_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        fields = [("01. WT:", "Enter WT"), ("02. FT:", "Enter FT"), ("03. ADT:", "Enter ADT")]
        self.ff_inputs = {}
        for label_text, hint in fields:
            inp = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=FIELD_FS)
            self.ff_inputs[label_text] = inp
            layout.add_widget(self._make_row(label_text, inp))

        self.input_ff = TextInput(
            hint_text="Result", multiline=False, readonly=True,
            font_size=FIELD_FS, background_color=(0.9, 0.9, 0.9, 1)
        )
        layout.add_widget(self._make_row("04. FF:", self.input_ff))

        layout.add_widget(Label(size_hint_y=1))   # flexible spacer

        calc_btn  = Button(text="Calculate", font_size=BTN_FS, bold=True, background_color=(0.2, 0.8, 0.2, 1))
        close_btn = Button(text="Close",     font_size=BTN_FS, bold=True, background_color=(0.8, 0.2, 0.2, 1))
        calc_btn.bind(on_press=self.process_ff_calculation)
        layout.add_widget(self._make_action_bar(calc_btn, close_btn))

        self.ff_popup = Popup(
            title="01. FF Calculator Engine",
            content=layout, size_hint=(0.92, 0.72), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )
        close_btn.bind(on_press=self.ff_popup.dismiss)
        self.ff_popup.open()

    def process_ff_calculation(self, instance):
        global last_calculated_ff
        try:
            wt  = float(self.ff_inputs["01. WT:"].text  or 0)
            ft  = float(self.ff_inputs["02. FT:"].text  or 0)
            adt = float(self.ff_inputs["03. ADT:"].text or 0)
            result = (3 * adt) - ft - wt - ft
            last_calculated_ff = result
            self.input_ff.text = str(round(result, 2))
        except ValueError:
            self.input_ff.text = "Error"

    # =========================================================================
    # POPUP 02: WATER TEMP CALCULATOR
    # =========================================================================
    def open_water_temp_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        water_fields = [("01. DDT:", "Enter DDT"), ("02. RT:", "Enter RT"), ("03. FT:", "Enter FT")]
        self.w_inputs = {}
        for label, hint in water_fields:
            inp = TextInput(hint_text=hint, multiline=False, input_filter='float', font_size=FIELD_FS)
            self.w_inputs[label] = inp
            layout.add_widget(self._make_row(label, inp))

        # FF row – input + Get button
        ff_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_H, spacing=SPACING)
        ff_lbl = Label(text="04. FF:", font_size=LABEL_FS, size_hint_x=0.4, halign='left', valign='middle')
        ff_lbl.bind(size=ff_lbl.setter('text_size'))
        self.input_ff_water = TextInput(hint_text="Value", multiline=False, input_filter='float', font_size=FIELD_FS)
        get_ff_btn = Button(text="Get", font_size=BTN_FS, bold=True, size_hint_x=0.25, background_color=(0, 0.7, 1, 1))
        get_ff_btn.bind(on_press=self.fetch_ff_data)
        ff_row.add_widget(ff_lbl)
        ff_row.add_widget(self.input_ff_water)
        ff_row.add_widget(get_ff_btn)
        layout.add_widget(ff_row)

        self.input_cal_wt = TextInput(
            hint_text="Result", multiline=False, readonly=True,
            font_size=FIELD_FS, background_color=(0.9, 0.9, 0.9, 1)
        )
        layout.add_widget(self._make_row("05. Cal WT:", self.input_cal_wt))

        layout.add_widget(Label(size_hint_y=1))

        calc_btn  = Button(text="Calculate", font_size=BTN_FS, bold=True, background_color=(0.1, 0.6, 0.6, 1))
        close_btn = Button(text="Close",     font_size=BTN_FS, bold=True, background_color=(0.8, 0.2, 0.2, 1))
        calc_btn.bind(on_press=self.process_water_calculation)
        layout.add_widget(self._make_action_bar(calc_btn, close_btn))

        self.water_popup = Popup(
            title="02. Water Temp Calculator",
            content=layout, size_hint=(0.92, 0.78), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )
        close_btn.bind(on_press=self.water_popup.dismiss)
        self.water_popup.open()

    def fetch_ff_data(self, instance):
        global last_calculated_ff
        self.input_ff_water.text = str(round(last_calculated_ff, 2))

    def process_water_calculation(self, instance):
        global last_calculated_wt
        try:
            ddt = float(self.w_inputs["01. DDT:"].text or 0)
            rt  = float(self.w_inputs["02. RT:"].text  or 0)
            ft  = float(self.w_inputs["03. FT:"].text  or 0)
            ff  = float(self.input_ff_water.text       or 0)
            result = (3 * ddt) - rt - ft - ff
            last_calculated_wt = result
            self.input_cal_wt.text = str(round(result, 2))
        except ValueError:
            self.input_cal_wt.text = "Error"

    # =========================================================================
    # POPUP 03: ICE TEMP CALCULATOR
    # =========================================================================
    def open_ice_temp_popup(self, instance):
        layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        self.input_req_water = TextInput(hint_text="Enter Weight", multiline=False, input_filter='float', font_size=FIELD_FS)
        self.input_ice_wt    = TextInput(hint_text="Enter WT",     multiline=False, input_filter='float', font_size=FIELD_FS)
        layout.add_widget(self._make_row("01. Req Water Wt:", self.input_req_water))
        layout.add_widget(self._make_row("02. WT:",           self.input_ice_wt))

        # Cal WT row – input + Get button
        cal_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_H, spacing=SPACING)
        cal_lbl = Label(text="03. Cal WT:", font_size=LABEL_FS, size_hint_x=0.4, halign='left', valign='middle')
        cal_lbl.bind(size=cal_lbl.setter('text_size'))
        self.input_ice_cal_wt = TextInput(hint_text="Value", multiline=False, input_filter='float', font_size=FIELD_FS)
        get_wt_btn = Button(text="Get", font_size=BTN_FS, bold=True, size_hint_x=0.25, background_color=(0, 0.7, 1, 1))
        get_wt_btn.bind(on_press=self.fetch_wt_data)
        cal_row.add_widget(cal_lbl)
        cal_row.add_widget(self.input_ice_cal_wt)
        cal_row.add_widget(get_wt_btn)
        layout.add_widget(cal_row)

        self.output_calc_ice   = TextInput(hint_text="Result", multiline=False, readonly=True, font_size=FIELD_FS, background_color=(0.9, 0.9, 0.9, 1))
        self.output_calc_water = TextInput(hint_text="Result", multiline=False, readonly=True, font_size=FIELD_FS, background_color=(0.9, 0.9, 0.9, 1))
        layout.add_widget(self._make_row("04. Calc Ice Wt:",   self.output_calc_ice))
        layout.add_widget(self._make_row("05. Calc Water Wt:", self.output_calc_water))

        layout.add_widget(Label(size_hint_y=1))

        calc_btn  = Button(text="Calculate", font_size=BTN_FS, bold=True, background_color=(0.2, 0.5, 0.7, 1))
        close_btn = Button(text="Close",     font_size=BTN_FS, bold=True, background_color=(0.8, 0.2, 0.2, 1))
        calc_btn.bind(on_press=self.process_ice_calculation)
        layout.add_widget(self._make_action_bar(calc_btn, close_btn))

        self.ice_popup = Popup(
            title="03. Ice Temp Calculator Engine",
            content=layout, size_hint=(0.92, 0.82), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )
        close_btn.bind(on_press=self.ice_popup.dismiss)
        self.ice_popup.open()

    def fetch_wt_data(self, instance):
        global last_calculated_wt
        self.input_ice_cal_wt.text = str(round(last_calculated_wt, 2))

    def process_ice_calculation(self, instance):
        try:
            req_water = float(self.input_req_water.text    or 0)
            wt        = float(self.input_ice_wt.text       or 0)
            cal_wt    = float(self.input_ice_cal_wt.text   or 0)
            if (wt + 80) == 0:
                self.output_calc_ice.text   = "Error: Div/0"
                self.output_calc_water.text = "Error"
                return
            ice_wt   = req_water * (wt - cal_wt) / (wt + 80)
            water_wt = req_water - ice_wt
            self.output_calc_ice.text   = str(round(ice_wt,   2))
            self.output_calc_water.text = str(round(water_wt, 2))
        except ValueError:
            self.output_calc_ice.text   = "Error"
            self.output_calc_water.text = "Error"

    # =========================================================================
    # POPUP 04: RECIPE CALCULATOR
    # =========================================================================
    def open_recipe_popup(self, instance):
        base_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        # --- Top control bar: active recipe label  +  Auto cal. checkbox -----
        ctrl_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38), spacing=SPACING)

        self.recipe_title_label = Label(
            text="Active Recipe: New Formulation",
            font_size=TITLE_FS, bold=True, color=(1, 0.8, 0.2, 1),
            size_hint_x=0.7, halign='left', valign='middle'
        )
        self.recipe_title_label.bind(size=self.recipe_title_label.setter('text_size'))
        ctrl_bar.add_widget(self.recipe_title_label)

        autocal_lbl = Label(
            text="Auto cal.", font_size=SMALL_FS,
            size_hint_x=0.22, halign='right', valign='middle'
        )
        autocal_lbl.bind(size=autocal_lbl.setter('text_size'))
        ctrl_bar.add_widget(autocal_lbl)

        self.realtime_checkbox = CheckBox(size_hint_x=0.08, active=False)
        self.realtime_checkbox.bind(active=self.on_checkbox_toggle)
        ctrl_bar.add_widget(self.realtime_checkbox)

        base_layout.add_widget(ctrl_bar)

        # --- Scrollable form area --------------------------------------------
        scroll_window = ScrollView(size_hint=(1, 1))
        self.form_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))

        # Top totals bar
        totals_grid = GridLayout(cols=6, size_hint_y=None, height=SUMMARY_H, spacing=dp(6))
        for lbl_text in ["Total Wt:", "Total Flour:", "Total Water:"]:
            totals_grid.add_widget(Label(
                text=lbl_text, font_size=SMALL_FS, bold=True,
                halign='center', valign='middle'
            ))
            if lbl_text == "Total Wt:":
                self.recipe_total_weight = TextInput(
                    hint_text="0.00", multiline=False, input_filter='float', font_size=SMALL_FS
                )
                self.recipe_total_weight.bind(text=self.on_manual_field_change)
                totals_grid.add_widget(self.recipe_total_weight)
            elif lbl_text == "Total Flour:":
                self.recipe_total_flour = TextInput(
                    hint_text="0.00", readonly=True, multiline=False,
                    font_size=SMALL_FS, background_color=(0.9, 0.9, 0.9, 1)
                )
                totals_grid.add_widget(self.recipe_total_flour)
            else:
                self.recipe_total_water = TextInput(
                    hint_text="0.00", readonly=True, multiline=False,
                    font_size=SMALL_FS, background_color=(0.9, 0.9, 0.9, 1)
                )
                totals_grid.add_widget(self.recipe_total_water)
        self.form_layout.add_widget(totals_grid)

        # Helper: column header row
        def make_section_header(title_text):
            header = GridLayout(cols=4, size_hint_y=None, height=SECTION_H, spacing=dp(4))
            lbl_main = Label(
                text=title_text, bold=True, font_size=HEADER_FS,
                color=(0, 0.7, 1, 1), halign='left', valign='middle', size_hint_x=0.4
            )
            lbl_main.bind(size=lbl_main.setter('text_size'))
            header.add_widget(lbl_main)
            for col_name in ["Bakers %", "True %", "Weight"]:
                header.add_widget(Label(
                    text=col_name, bold=True, font_size=SMALL_FS,
                    size_hint_x=0.2, halign='center', valign='middle'
                ))
            return header

        # Helper: ingredient input row
        def make_ingredient_row(name, section_dict, bind_fn):
            row = GridLayout(cols=4, size_hint_y=None, height=GRID_ROW_H, spacing=dp(4))
            lbl = Label(
                text=name, font_size=SMALL_FS,
                halign='left', valign='middle', size_hint_x=0.4
            )
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            b_pct  = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)
            t_pct  = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)
            wt_val = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)
            for w in [b_pct, t_pct, wt_val]:
                w.bind(text=bind_fn)
            row.add_widget(b_pct)
            row.add_widget(t_pct)
            row.add_widget(wt_val)
            section_dict[name] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            return row

        # --- SPONGE SECTION --------------------------------------------------
        self.form_layout.add_widget(make_section_header("Sponge Section"))
        self.sponge_inputs = {}
        for ing in ["Flour", "Water", "Yeast"]:
            self.form_layout.add_widget(make_ingredient_row(ing, self.sponge_inputs, self.on_manual_field_change))

        self.btn_add_sponge = Button(
            text="+ Add Ingredient (Sponge)", font_size=SMALL_FS, bold=True,
            size_hint_y=None, height=GRID_ROW_H, background_color=(0.2, 0.6, 0.4, 1)
        )
        self.btn_add_sponge.bind(on_press=lambda i: self.show_add_ingredient_dialog("sponge"))
        self.form_layout.add_widget(self.btn_add_sponge)

        # --- DOUGH SECTION ---------------------------------------------------
        self.form_layout.add_widget(make_section_header("Dough Section"))
        self.dough_inputs = {}
        for ing in ["Flour", "Water", "Sugar", "Shortening", "MSNF"]:
            self.form_layout.add_widget(make_ingredient_row(ing, self.dough_inputs, self.on_manual_field_change))

        self.btn_add_dough = Button(
            text="+ Add Ingredient (Dough)", font_size=SMALL_FS, bold=True,
            size_hint_y=None, height=GRID_ROW_H, background_color=(0.2, 0.6, 0.4, 1)
        )
        self.btn_add_dough.bind(on_press=lambda i: self.show_add_ingredient_dialog("dough"))
        self.form_layout.add_widget(self.btn_add_dough)

        # --- Totals summary row ----------------------------------------------
        summary_row = GridLayout(cols=4, size_hint_y=None, height=SUMMARY_H, spacing=dp(4))
        lbl_sum = Label(
            text="Total", bold=True, font_size=SMALL_FS,
            halign='left', valign='middle', size_hint_x=0.4
        )
        lbl_sum.bind(size=lbl_sum.setter('text_size'))
        summary_row.add_widget(lbl_sum)
        self.total_bakers_summary = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=SMALL_FS, background_color=(0.85, 0.92, 0.98, 1))
        self.total_true_summary   = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=SMALL_FS, background_color=(0.85, 0.92, 0.98, 1))
        self.total_weight_summary = TextInput(text="0.00", readonly=True, multiline=False, size_hint_x=0.2, font_size=SMALL_FS, background_color=(0.85, 0.92, 0.98, 1))
        summary_row.add_widget(self.total_bakers_summary)
        summary_row.add_widget(self.total_true_summary)
        summary_row.add_widget(self.total_weight_summary)
        self.form_layout.add_widget(summary_row)

        scroll_window.add_widget(self.form_layout)
        base_layout.add_widget(scroll_window)

        # --- Bottom action bar -----------------------------------------------
        save_btn  = Button(text="Save Recipe", font_size=BTN_FS, bold=True, background_color=(0.15, 0.65, 0.35, 1))
        load_btn  = Button(text="Load Recipe", font_size=BTN_FS, bold=True, background_color=(0.15, 0.45, 0.65, 1))
        calc_btn  = Button(text="Calculate",   font_size=BTN_FS, bold=True, background_color=(0.55, 0.2,  0.75, 1))
        close_btn = Button(text="Close",       font_size=BTN_FS, bold=True, background_color=(0.8,  0.2,  0.2,  1))

        save_btn.bind(on_press=self.trigger_save_workflow)
        load_btn.bind(on_press=self.trigger_load_list_popup)
        calc_btn.bind(on_press=lambda inst: self.calculate_recipe_matrix())

        base_layout.add_widget(self._make_action_bar(save_btn, load_btn, calc_btn, close_btn))

        self.recipe_popup = Popup(
            title="Recipe Calculator",
            content=base_layout, size_hint=(0.98, 0.95), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )
        close_btn.bind(on_press=self.recipe_popup.dismiss)
        self.recipe_popup.open()

    # =========================================================================
    # AUTO-CALCULATE CHECKBOX TOGGLE
    # =========================================================================
    def on_checkbox_toggle(self, checkbox, value):
        if value:
            self.calculate_recipe_matrix()

    # =========================================================================
    # REAL-TIME CALCULATION DISPATCHER
    # =========================================================================
    def on_manual_field_change(self, instance, value):
        if self._calculating:
            return
        if not self.realtime_checkbox.active:
            return

        context_section    = None
        context_ingredient = None
        context_field_type = None

        if instance == self.recipe_total_weight:
            context_field_type = "total_weight"
        else:
            for s_name, inputs in [("Sponge", self.sponge_inputs), ("Dough", self.dough_inputs)]:
                for ing, fields in inputs.items():
                    for f_key, f_inst in fields.items():
                        if f_inst == instance:
                            context_section    = s_name
                            context_ingredient = ing
                            context_field_type = f_key
                            break

        self.calculate_recipe_matrix(
            trigger_field=context_field_type,
            trigger_ing=context_ingredient,
            trigger_sec=context_section
        )

    # =========================================================================
    # MAIN CALCULATION & VALIDATION ENGINE  (bidirectional, 3-scenario)
    # =========================================================================
    def calculate_recipe_matrix(self, trigger_field=None, trigger_ing=None, trigger_sec=None):
        if self._calculating:
            return
        self._calculating = True

        try:
            def _f(text, default=0.0):
                try:
                    v = float(text)
                    return v if v == v else default
                except (ValueError, TypeError):
                    return default

            # STEP 1 – global Total Dough Weight
            total_dough_weight = _f(self.recipe_total_weight.text)

            # STEP 2 – section occupancy
            sponge_has_data = any(
                f["bakers"].text or f["true"].text or f["weight"].text
                for f in self.sponge_inputs.values()
            )
            dough_has_data = any(
                f["bakers"].text or f["true"].text or f["weight"].text
                for f in self.dough_inputs.values()
            )

            # STEP 3 – SCENARIO 01: True % → Bakers % back-calculation
            if trigger_field == "true" and trigger_ing and trigger_sec:
                target_inputs = self.sponge_inputs if trigger_sec == "Sponge" else self.dough_inputs
                ing_true_val  = _f(target_inputs[trigger_ing]["true"].text)
                flour_true_pct = 0.0
                for sec_inputs in [self.sponge_inputs, self.dough_inputs]:
                    if "Flour" in sec_inputs:
                        c = _f(sec_inputs["Flour"]["true"].text)
                        if c > 0:
                            flour_true_pct = c
                            break
                if flour_true_pct > 0 and ing_true_val > 0:
                    new_b = str(round((ing_true_val / flour_true_pct) * 100.0, 2))
                    if target_inputs[trigger_ing]["bakers"].text != new_b:
                        target_inputs[trigger_ing]["bakers"].text = new_b

            # STEP 4 – SCENARIO 02: True % + Weight → Total Dough Weight
            if trigger_field in ("weight", "true") and trigger_ing and trigger_sec:
                target_inputs = self.sponge_inputs if trigger_sec == "Sponge" else self.dough_inputs
                row_true   = _f(target_inputs[trigger_ing]["true"].text)
                row_weight = _f(target_inputs[trigger_ing]["weight"].text)
                if row_true > 0 and row_weight > 0:
                    derived_total = (row_weight / row_true) * 100.0
                    new_tw = str(round(derived_total, 2))
                    if total_dough_weight == 0 or self.recipe_total_weight.text != new_tw:
                        self.recipe_total_weight.text = new_tw
                        total_dough_weight = derived_total

            # STEP 5 – Flour rule: single-section dough auto-sets Flour = 100 %
            sf_bakers = _f(self.sponge_inputs["Flour"]["bakers"].text) if "Flour" in self.sponge_inputs else 0.0
            df_bakers = _f(self.dough_inputs["Flour"]["bakers"].text)  if "Flour" in self.dough_inputs  else 0.0

            if not sponge_has_data and dough_has_data and "Flour" in self.dough_inputs:
                if not (trigger_field == "bakers" and trigger_ing == "Flour" and trigger_sec == "Dough"):
                    if df_bakers == 0.0:
                        self.dough_inputs["Flour"]["bakers"].text = "100.00"
                        df_bakers = 100.0

            # STEP 6 – Total Bakers % summation (Sponge Water excluded)
            total_bakers_sum = 0.0
            for name, fields in self.sponge_inputs.items():
                if name != "Water":
                    total_bakers_sum += _f(fields["bakers"].text)
            for name, fields in self.dough_inputs.items():
                total_bakers_sum += _f(fields["bakers"].text)
            if total_bakers_sum == 0:
                total_bakers_sum = 100.0

            # STEP 7 – SCENARIO 03: full matrix breakdown
            running_true_sum = 0.0
            running_flour_wt = 0.0
            running_water_wt = 0.0
            total_accum_wt   = 0.0

            for sec_name, sec_inputs in [("Sponge", self.sponge_inputs), ("Dough", self.dough_inputs)]:
                for name, fields in sec_inputs.items():
                    b_val = _f(fields["bakers"].text)
                    t_val = _f(fields["true"].text)
                    w_val = _f(fields["weight"].text)

                    user_owns_bakers = (trigger_field == "bakers" and trigger_ing == name and trigger_sec == sec_name)
                    user_owns_true   = (trigger_field == "true"   and trigger_ing == name and trigger_sec == sec_name)
                    user_owns_weight = (trigger_field == "weight" and trigger_ing == name and trigger_sec == sec_name)

                    # --- Derive True % from Bakers % ---
                    if b_val > 0 and not user_owns_true:
                        if name == "Water" and sec_name == "Sponge":
                            # LOGIC 02: Water True % = Sponge Flour Bakers % * Sponge Water Bakers % / Total Bakers %
                            sponge_flour_b = _f(self.sponge_inputs["Flour"]["bakers"].text) if "Flour" in self.sponge_inputs else 0.0
                            computed_true = (sponge_flour_b * b_val) / total_bakers_sum if total_bakers_sum > 0 else 0.0

                        elif name == "Water" and sec_name == "Dough":
                            # Dough Water True % = (Dough Water Bakers % / Total Bakers % * 100) - Sponge Water True %
                            sponge_water_true = _f(self.sponge_inputs["Water"]["true"].text) if "Water" in self.sponge_inputs else 0.0
                            raw_true = (b_val / total_bakers_sum) * 100.0 if total_bakers_sum > 0 else 0.0
                            computed_true = max(raw_true - sponge_water_true, 0.0)

                        else:
                            computed_true = (b_val * 100.0) / total_bakers_sum

                        new_t = str(round(computed_true, 2)) if computed_true > 0 else ""
                        if fields["true"].text != new_t:
                            fields["true"].text = new_t
                        t_val = computed_true

                    # --- LOGIC 03 Path A: Weight = True % * Total Dough Weight / 100 ---
                    if t_val > 0 and total_dough_weight > 0 and not user_owns_weight:
                        computed_weight = (total_dough_weight * t_val) / 100.0
                        new_w = str(round(computed_weight, 2)) if computed_weight > 0 else ""
                        if fields["weight"].text != new_w:
                            fields["weight"].text = new_w
                        w_val = computed_weight

                    # --- Derive True % from Weight alone ---
                    elif w_val > 0 and b_val == 0 and total_dough_weight > 0 and not user_owns_true:
                        computed_true = (w_val / total_dough_weight) * 100.0
                        new_t = str(round(computed_true, 2)) if computed_true > 0 else ""
                        if fields["true"].text != new_t:
                            fields["true"].text = new_t
                        t_val = computed_true

                    t_val = _f(fields["true"].text)
                    w_val = _f(fields["weight"].text)

                    if name.lower() == "flour": running_flour_wt += w_val
                    if name.lower() == "water": running_water_wt += w_val
                    running_true_sum += t_val
                    total_accum_wt   += w_val

            # STEP 8 – update summary display fields
            self.recipe_total_flour.text = str(round(running_flour_wt, 2)) if running_flour_wt > 0 else "0.00"
            self.recipe_total_water.text = str(round(running_water_wt, 2)) if running_water_wt > 0 else "0.00"

            if trigger_field != "total_weight" and total_accum_wt > 0 and total_dough_weight == 0:
                new_tw = str(round(total_accum_wt, 2))
                if self.recipe_total_weight.text != new_tw:
                    self.recipe_total_weight.text = new_tw

            self.total_bakers_summary.text = str(round(total_bakers_sum, 2))
            self.total_true_summary.text   = str(round(running_true_sum, 2))
            self.total_weight_summary.text = str(round(total_accum_wt,   2))

            # STEP 9 – validation highlights
            error_bg   = [0.6, 0.1, 0.1, 1]
            normal_bg  = [1,   1,   1,   1]
            summary_bg = [0.85, 0.92, 0.98, 1]

            if running_true_sum > 0 and not (99.0 <= round(running_true_sum, 2) <= 100.01):
                self.total_true_summary.background_color = error_bg
                self.total_true_summary.color = [1, 1, 1, 1]
            else:
                self.total_true_summary.background_color = summary_bg
                self.total_true_summary.color = [0, 0, 0, 1]

            # LOGIC 01: Sponge Flour Bakers % + Dough Flour Bakers % must = 100
            if sponge_has_data and dough_has_data:
                sf_bakers = _f(self.sponge_inputs["Flour"]["bakers"].text) if "Flour" in self.sponge_inputs else 0.0
                df_bakers = _f(self.dough_inputs["Flour"]["bakers"].text)  if "Flour" in self.dough_inputs  else 0.0
                flour_ok  = abs((sf_bakers + df_bakers) - 100.0) <= 0.05
                flour_bg  = normal_bg if flour_ok else error_bg
                if "Flour" in self.sponge_inputs:
                    self.sponge_inputs["Flour"]["bakers"].background_color = flour_bg
                if "Flour" in self.dough_inputs:
                    self.dough_inputs["Flour"]["bakers"].background_color = flour_bg
            else:
                if "Flour" in self.sponge_inputs:
                    self.sponge_inputs["Flour"]["bakers"].background_color = normal_bg
                if "Flour" in self.dough_inputs:
                    self.dough_inputs["Flour"]["bakers"].background_color = normal_bg

        finally:
            self._calculating = False

    # =========================================================================
    # ADD INGREDIENT DIALOG
    # =========================================================================
    def show_add_ingredient_dialog(self, section_type):
        dialog_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)
        dialog_layout.add_widget(Label(
            text="Enter New Ingredient Name:",
            font_size=LABEL_FS, bold=True, size_hint_y=None, height=ROW_H
        ))
        ing_name_input = TextInput(
            hint_text="e.g. Salt, Milk, etc.",
            multiline=False, font_size=FIELD_FS,
            size_hint_y=None, height=ROW_H
        )
        dialog_layout.add_widget(ing_name_input)

        add_btn    = Button(text="Add",    font_size=BTN_FS, bold=True, background_color=(0.2, 0.7, 0.2, 1))
        cancel_btn = Button(text="Cancel", font_size=BTN_FS, bold=True, background_color=(0.8, 0.2, 0.2, 1))
        dialog_layout.add_widget(self._make_action_bar(add_btn, cancel_btn))

        prompt_popup = Popup(
            title=f"Add to {section_type.title()}",
            content=dialog_layout, size_hint=(0.85, 0.42), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )

        def execute_addition(instance):
            name = ing_name_input.text.strip()
            if name:
                self.inject_new_ingredient_row(name, section_type)
                prompt_popup.dismiss()

        add_btn.bind(on_press=execute_addition)
        cancel_btn.bind(on_press=prompt_popup.dismiss)
        prompt_popup.open()

    def inject_new_ingredient_row(self, name, section_type):
        new_row = GridLayout(cols=4, size_hint_y=None, height=GRID_ROW_H, spacing=dp(4))
        lbl = Label(text=name, font_size=SMALL_FS, halign='left', valign='middle', size_hint_x=0.4)
        lbl.bind(size=lbl.setter('text_size'))
        new_row.add_widget(lbl)

        b_pct  = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)
        t_pct  = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)
        wt_val = TextInput(hint_text="0.00", multiline=False, input_filter='float', size_hint_x=0.2, font_size=SMALL_FS)

        for w in [b_pct, t_pct, wt_val]:
            w.bind(text=self.on_manual_field_change)

        new_row.add_widget(b_pct)
        new_row.add_widget(t_pct)
        new_row.add_widget(wt_val)

        if section_type == "sponge":
            self.sponge_inputs[name] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            idx = self.form_layout.children.index(self.btn_add_sponge)
            self.form_layout.add_widget(new_row, index=idx + 1)
        else:
            self.dough_inputs[name] = {"bakers": b_pct, "true": t_pct, "weight": wt_val}
            idx = self.form_layout.children.index(self.btn_add_dough)
            self.form_layout.add_widget(new_row, index=idx + 1)

    # =========================================================================
    # SAVE RECIPE WORKFLOW
    # =========================================================================
    def trigger_save_workflow(self, instance):
        filled_count = 0
        valid_rows   = []

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
            warn_box = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)
            warn_box.add_widget(Label(
                text="Not enough recipe details filled to save.",
                font_size=LABEL_FS, bold=True, halign='center', valign='middle'
            ))
            ok_btn = Button(text="OK", font_size=BTN_FS, bold=True, size_hint_y=None, height=BTN_H, background_color=(0.8, 0.2, 0.2, 1))
            warn_box.add_widget(ok_btn)
            warn_popup = Popup(title="Warning", content=warn_box, size_hint=(0.75, 0.32),
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H)
            ok_btn.bind(on_press=warn_popup.dismiss)
            warn_popup.open()
            return

        save_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        # Table header
        table_header = GridLayout(cols=5, size_hint_y=None, height=SECTION_H, spacing=dp(2))
        for col_text, sx in [("Sec", 0.15), ("Ingredient", 0.37), ("Bakers %", 0.16), ("True %", 0.16), ("Weight", 0.16)]:
            lbl = Label(text=col_text, bold=True, font_size=SMALL_FS, size_hint_x=sx, halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            table_header.add_widget(lbl)
        save_layout.add_widget(table_header)

        scroll_view = ScrollView(size_hint=(1, 1))
        grid_table  = GridLayout(cols=5, spacing=dp(2), size_hint_y=None)
        grid_table.bind(minimum_height=grid_table.setter('height'))
        for sec, ing_name, b_pct, t_pct, w_val in valid_rows:
            for text_val, sx in [(sec, 0.15), (ing_name, 0.37), (b_pct, 0.16), (t_pct, 0.16), (w_val, 0.16)]:
                c = Label(text=text_val, font_size=SMALL_FS, size_hint_x=sx, size_hint_y=None, height=GRID_ROW_H, halign='center', valign='middle')
                c.bind(size=c.setter('text_size'))
                grid_table.add_widget(c)
        scroll_view.add_widget(grid_table)
        save_layout.add_widget(scroll_view)

        # Name input
        name_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=ROW_H, spacing=SPACING)
        name_row.add_widget(Label(text="Recipe Name:", font_size=LABEL_FS, bold=True, size_hint_x=0.32))
        recipe_name_field = TextInput(hint_text="Enter recipe name", multiline=False, font_size=FIELD_FS)
        name_row.add_widget(recipe_name_field)
        save_layout.add_widget(name_row)

        save_btn   = Button(text="Save",   font_size=BTN_FS, bold=True, background_color=(0.15, 0.65, 0.35, 1))
        cancel_btn = Button(text="Cancel", font_size=BTN_FS, bold=True, background_color=(0.8,  0.2,  0.2,  1))
        save_layout.add_widget(self._make_action_bar(save_btn, cancel_btn))

        save_popup = Popup(title="Review Recipe Summary", content=save_layout, size_hint=(0.95, 0.88), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H)
        cancel_btn.bind(on_press=save_popup.dismiss)

        def save_to_database(inst):
            final_name = recipe_name_field.text.strip()
            if not final_name:
                recipe_name_field.hint_text = "Name required!"
                return
            self.saved_recipes_db[final_name] = {
                "dataset": valid_rows,
                "top_totals": {
                    "weight": self.recipe_total_weight.text,
                    "flour":  self.recipe_total_flour.text,
                    "water":  self.recipe_total_water.text
                },
                "bottom_totals": {
                    "bakers": self.total_bakers_summary.text,
                    "true":   self.total_true_summary.text,
                    "weight": self.total_weight_summary.text
                }
            }
            try:
                with open(self.recipes_db_file, "w", encoding="utf-8") as f:
                    json.dump(self.saved_recipes_db, f, indent=4)
            except OSError:
                pass
            self.recipe_title_label.text = f"Active Recipe: {final_name}"
            save_popup.dismiss()

        save_btn.bind(on_press=save_to_database)
        save_popup.open()

    # =========================================================================
    # LOAD RECIPE LIST
    # =========================================================================
    def trigger_load_list_popup(self, instance):
        list_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)

        if not self.saved_recipes_db:
            no_lbl = Label(
                text="No saved records found in system storage.",
                font_size=LABEL_FS, halign='center', valign='middle'
            )
            no_lbl.bind(size=no_lbl.setter('text_size'))
            list_layout.add_widget(no_lbl)
            close_btn = Button(text="Close", font_size=BTN_FS, bold=True, size_hint_y=None, height=BTN_H, background_color=(0.8, 0.2, 0.2, 1))
            list_layout.add_widget(close_btn)
            ep = Popup(title="Database Library Index", content=list_layout, size_hint=(0.85, 0.35),
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H)
            close_btn.bind(on_press=ep.dismiss)
            ep.open()
            return

        title_lbl = Label(
            text="Select Recipe Profile:", bold=True,
            font_size=LABEL_FS, size_hint_y=None, height=ROW_H,
            halign='center', valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        list_layout.add_widget(title_lbl)

        scroll_records = ScrollView()
        records_box    = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        records_box.bind(minimum_height=records_box.setter('height'))

        load_list_popup = Popup(title="Database Library Index", content=list_layout, size_hint=(0.9, 0.88),
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H)

        for item_key in self.saved_recipes_db.keys():
            row_btn = Button(
                text=str(item_key), font_size=LABEL_FS, bold=True,
                size_hint_y=None, height=BTN_H, background_color=(0.2, 0.4, 0.6, 1)
            )
            row_btn.bind(on_press=lambda inst, key=item_key: self.open_recipe_preview(key, load_list_popup))
            records_box.add_widget(row_btn)

        scroll_records.add_widget(records_box)
        list_layout.add_widget(scroll_records)

        cancel_btn = Button(text="Cancel", font_size=BTN_FS, bold=True, size_hint_y=None, height=BTN_H, background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn.bind(on_press=load_list_popup.dismiss)
        list_layout.add_widget(cancel_btn)

        load_list_popup.open()

    # =========================================================================
    # RECIPE PREVIEW POPUP
    # =========================================================================
    def open_recipe_preview(self, recipe_key, primary_popup):
        record_profile = self.saved_recipes_db[recipe_key]

        preview_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)
        title_lbl = Label(
            text=f"Profile View: {recipe_key}", bold=True,
            font_size=LABEL_FS, size_hint_y=None, height=ROW_H, color=(0, 0.7, 1, 1)
        )
        preview_layout.add_widget(title_lbl)

        # Column headers
        preview_table = GridLayout(cols=4, size_hint_y=None, height=SECTION_H, spacing=dp(2))
        for h_text, sx in [("Ingredient", 0.4), ("Bakers %", 0.2), ("True %", 0.2), ("Weight", 0.2)]:
            lbl = Label(text=h_text, bold=True, font_size=SMALL_FS, size_hint_x=sx, halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            preview_table.add_widget(lbl)
        preview_layout.add_widget(preview_table)

        scroll_preview = ScrollView(size_hint=(1, 1))
        grid_preview   = GridLayout(cols=4, spacing=dp(2), size_hint_y=None)
        grid_preview.bind(minimum_height=grid_preview.setter('height'))
        for sec, name, bp, tp, wt in record_profile["dataset"]:
            for val, sx in [(name, 0.4), (bp, 0.2), (tp, 0.2), (wt, 0.2)]:
                c = Label(text=val, font_size=SMALL_FS, size_hint_x=sx, size_hint_y=None, height=GRID_ROW_H, halign='center', valign='middle')
                c.bind(size=c.setter('text_size'))
                grid_preview.add_widget(c)
        scroll_preview.add_widget(grid_preview)
        preview_layout.add_widget(scroll_preview)

        load_btn   = Button(text="Load",   font_size=BTN_FS, bold=True, background_color=(0.15, 0.45, 0.65, 1))
        delete_btn = Button(text="Delete", font_size=BTN_FS, bold=True, background_color=(0.75, 0.1,  0.1,  1))
        cancel_btn = Button(text="Cancel", font_size=BTN_FS, bold=True, background_color=(0.45, 0.45, 0.45, 1))
        preview_layout.add_widget(self._make_action_bar(load_btn, delete_btn, cancel_btn))

        preview_popup = Popup(
            title="Recipe Preview", content=preview_layout,
            size_hint=(0.95, 0.88), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H
        )
        cancel_btn.bind(on_press=preview_popup.dismiss)

        # --- Delete with confirmation -----------------------------------------
        def confirm_delete_recipe(inst):
            confirm_layout = BoxLayout(orientation='vertical', padding=[PAD, PAD + POPUP_TOP_PAD, PAD, PAD], spacing=SPACING)
            msg = Label(
                text=f"Delete '{recipe_key}'?\nThis cannot be undone.",
                font_size=LABEL_FS, bold=True, halign='center', valign='middle'
            )
            msg.bind(size=msg.setter('text_size'))
            confirm_layout.add_widget(msg)
            yes_btn = Button(text="Yes, Delete", font_size=BTN_FS, bold=True, background_color=(0.75, 0.1, 0.1, 1))
            no_btn  = Button(text="Cancel",      font_size=BTN_FS, bold=True, background_color=(0.45, 0.45, 0.45, 1))
            confirm_layout.add_widget(self._make_action_bar(yes_btn, no_btn))
            del_popup = Popup(title="Confirm Delete", content=confirm_layout, size_hint=(0.78, 0.35), auto_dismiss=False,
            title_size=POPUP_TITLE_SIZE, separator_height=POPUP_SEP_H)

            def execute_delete(inst):
                if recipe_key in self.saved_recipes_db:
                    del self.saved_recipes_db[recipe_key]
                    try:
                        with open(self.recipes_db_file, "w", encoding="utf-8") as f:
                            json.dump(self.saved_recipes_db, f, indent=4)
                    except OSError:
                        pass
                del_popup.dismiss()
                preview_popup.dismiss()
                primary_popup.dismiss()

            yes_btn.bind(on_press=execute_delete)
            no_btn.bind(on_press=del_popup.dismiss)
            del_popup.open()

        delete_btn.bind(on_press=confirm_delete_recipe)

        # --- Load recipe into main grid --------------------------------------
        def inject_recipe_to_main_screen(inst):
            self._calculating = True
            try:
                for _, fields in self.sponge_inputs.items():
                    fields["bakers"].text = fields["true"].text = fields["weight"].text = ""
                for _, fields in self.dough_inputs.items():
                    fields["bakers"].text = fields["true"].text = fields["weight"].text = ""

                for sec, name, bp, tp, wt in record_profile["dataset"]:
                    target = self.sponge_inputs if sec == "Sponge" else self.dough_inputs
                    if name not in target:
                        self.inject_new_ingredient_row(name, sec.lower())
                    target[name]["bakers"].text = bp if float(bp or 0) > 0 else ""
                    target[name]["true"].text   = tp if float(tp or 0) > 0 else ""
                    target[name]["weight"].text = wt if float(wt or 0) > 0 else ""

                self.recipe_total_weight.text    = record_profile["top_totals"]["weight"]
                self.recipe_total_flour.text     = record_profile["top_totals"]["flour"]
                self.recipe_total_water.text     = record_profile["top_totals"]["water"]
                self.total_bakers_summary.text   = record_profile["bottom_totals"]["bakers"]
                self.total_true_summary.text     = record_profile["bottom_totals"]["true"]
                self.total_weight_summary.text   = record_profile["bottom_totals"]["weight"]
                self.recipe_title_label.text     = f"Active Recipe: {recipe_key}"
            finally:
                self._calculating = False

            self.calculate_recipe_matrix()
            preview_popup.dismiss()
            primary_popup.dismiss()

        load_btn.bind(on_press=inject_recipe_to_main_screen)
        preview_popup.open()

    def logout(self, instance):
        self.manager.current = 'login'


# =============================================================================
# APP MANAGER
# =============================================================================
class MyMainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    MyMainApp().run()
