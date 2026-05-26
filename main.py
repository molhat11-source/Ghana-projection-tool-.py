"""
Ghana Coordinate Projection and Transformation Tool
====================================================
GE Assignment 1 — Geomatic Engineering, KNUST
Author: Quansah Larrissa Naana
Index:  7228523
Date:   2026

GUI Application built with Python Kivy.
"""

import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window

Window.clearcolor = (0.1, 0.1, 0.18, 1)

# ─── ELLIPSOID PARAMETERS ─────────────────────────────────────────────────────

class Ellipsoid:
    def __init__(self, a, inv_f, name=""):
        self.name = name
        self.a    = a
        self.f    = 1.0 / inv_f
        self.b    = a * (1.0 - self.f)
        self.e2   = 2.0 * self.f - self.f ** 2
        self.e    = math.sqrt(self.e2)
        self.ep2  = self.e2 / (1.0 - self.e2)

WAR_OFFICE = Ellipsoid(6_378_249.145, 293.465,       "War Office (Clarke 1880 RGS)")
WGS84      = Ellipsoid(6_378_137.0,   298.257223563, "WGS 84")

# ─── GHANA TM CONSTANTS ───────────────────────────────────────────────────────
LAT0_DEG   =  0.0
LON0_DEG   = -1.0
K0         =  0.99975
FE_M       =  900_000.0
FN_M       =  0.0
GHANA_FOOT =  0.3047996
FE_FT      =  FE_M / GHANA_FOOT
FN_FT      =  0.0
DX, DY, DZ = -199.0, 32.0, 322.0

# ─── GEODETIC FUNCTIONS ───────────────────────────────────────────────────────

def meridional_arc(ell, lat):
    e2, a = ell.e2, ell.a
    A0 = 1 - e2/4 - 3*e2**2/64 - 5*e2**3/256
    A2 = 3/8 * (e2 + e2**2/4 + 15*e2**3/128)
    A4 = 15/256 * (e2**2 + 3*e2**3/4)
    A6 = 35*e2**3/3072
    return a*(A0*lat - A2*math.sin(2*lat) + A4*math.sin(4*lat) - A6*math.sin(6*lat))

def tm_forward(ell, lat_d, lon_d, lat0, lon0, k0, fe, fn):
    a, e2 = ell.a, ell.e2
    p, l   = math.radians(lat_d), math.radians(lon_d)
    p0, l0 = math.radians(lat0),  math.radians(lon0)
    sp, cp, tp = math.sin(p), math.cos(p), math.tan(p)
    N  = a / math.sqrt(1 - e2*sp**2)
    T  = tp**2; C = (e2/(1-e2))*cp**2; A_ = cp*(l-l0)
    M  = meridional_arc(ell, p); M0 = meridional_arc(ell, p0)
    ep2 = e2/(1-e2)
    E  = fe + k0*N*(A_ + (1-T+C)*A_**3/6 + (5-18*T+T**2+72*C-58*ep2)*A_**5/120)
    Nv = fn + k0*((M-M0) + N*tp*(A_**2/2 + (5-T+9*C+4*C**2)*A_**4/24 + (61-58*T+T**2+600*C-330*ep2)*A_**6/720))
    return E, Nv

def geo_xyz(ell, lat, lon, h=0):
    a, e2 = ell.a, ell.e2
    p, l  = math.radians(lat), math.radians(lon)
    N = a / math.sqrt(1 - e2*math.sin(p)**2)
    return (N+h)*math.cos(p)*math.cos(l), (N+h)*math.cos(p)*math.sin(l), (N*(1-e2)+h)*math.sin(p)

def xyz_geo(ell, X, Y, Z):
    a, e2 = ell.a, ell.e2
    lam = math.atan2(Y, X); pr = math.sqrt(X**2+Y**2)
    phi = math.atan2(Z, pr*(1-e2))
    for _ in range(10):
        N = a/math.sqrt(1-e2*math.sin(phi)**2)
        phi = math.atan2(Z + e2*N*math.sin(phi), pr)
    return math.degrees(phi), math.degrees(lam)

def wgs_accra(lat, lon):
    X, Y, Z = geo_xyz(WGS84, lat, lon)
    return xyz_geo(WAR_OFFICE, X+DX, Y+DY, Z+DZ)

# ─── CONVERSIONS ──────────────────────────────────────────────────────────────

def gng_to_gmg(E, N): return E*GHANA_FOOT, N*GHANA_FOOT
def gmg_to_gng(E, N): return E/GHANA_FOOT, N/GHANA_FOOT
def wgs_to_gmg(lat, lon):
    la, lo = wgs_accra(lat, lon)
    return tm_forward(WAR_OFFICE, la, lo, LAT0_DEG, LON0_DEG, K0, FE_M, FN_M)
def wgs_to_gng(lat, lon):
    E, N = wgs_to_gmg(lat, lon); return gmg_to_gng(E, N)

# ─── CONVERSION DEFINITIONS ───────────────────────────────────────────────────

CONVERSIONS = {
    "GNG → GMG  (feet to metres)": {
        "labels": ["Easting (ft)", "Northing (ft)"],
        "out_labels": ["Easting (m)", "Northing (m)"],
        "func": gng_to_gmg,
    },
    "GMG → GNG  (metres to feet)": {
        "labels": ["Easting (m)", "Northing (m)"],
        "out_labels": ["Easting (ft)", "Northing (ft)"],
        "func": gmg_to_gng,
    },
    "WGS 84 → GNG": {
        "labels": ["Latitude (°, +N)", "Longitude (°, +E)"],
        "out_labels": ["Easting (ft)", "Northing (ft)"],
        "func": wgs_to_gng,
    },
    "WGS 84 → GMG": {
        "labels": ["Latitude (°, +N)", "Longitude (°, +E)"],
        "out_labels": ["Easting (m)", "Northing (m)"],
        "func": wgs_to_gmg,
    },
}

CONV_KEYS = list(CONVERSIONS.keys())

# ─── UI HELPERS ───────────────────────────────────────────────────────────────

def make_label(text, font_size=15, color=(0.88, 0.89, 0.85, 1), bold=False, halign="left"):
    lbl = Label(text=text, font_size=font_size, color=color,
                bold=bold, halign=halign, valign="middle",
                size_hint_y=None, height=36)
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    return lbl

def make_input(hint=""):
    ti = TextInput(hint_text=hint, font_size=16,
                   background_color=(0.05, 0.11, 0.17, 1),
                   foreground_color=(0.89, 0.69, 0.29, 1),
                   hint_text_color=(0.4, 0.44, 0.52, 1),
                   cursor_color=(0.89, 0.69, 0.29, 1),
                   multiline=False,
                   size_hint_y=None, height=44,
                   padding=[12, 10])
    return ti

# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────

class GhanaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=16, spacing=10, **kwargs)

        # ── Title ──
        with self.canvas.before:
            Color(0.06, 0.19, 0.38, 1)
            self.title_rect = Rectangle(size=(Window.width, 70), pos=(0, Window.height - 70))

        title_box = BoxLayout(orientation='vertical', size_hint_y=None, height=70)
        title_box.add_widget(make_label("Ghana Coordinate Projection Tool",
                                        font_size=17, bold=True,
                                        color=(0.89, 0.69, 0.29, 1), halign="center"))
        title_box.add_widget(make_label("Geomatic Engineering · KNUST · GE Assignment 1",
                                        font_size=11, color=(0.54, 0.58, 0.68, 1), halign="center"))
        self.add_widget(title_box)

        # ── Conversion selector ──
        self.add_widget(make_label("Select Conversion:", font_size=13,
                                   color=(0.89, 0.69, 0.29, 1), bold=True))
        self.spinner = Spinner(
            text=CONV_KEYS[0],
            values=CONV_KEYS,
            font_size=14,
            size_hint_y=None, height=46,
            background_color=(0.06, 0.19, 0.38, 1),
            color=(1, 1, 1, 1),
        )
        self.spinner.bind(text=self.on_conversion_change)
        self.add_widget(self.spinner)

        # ── Input 1 ──
        self.lbl1 = make_label("Easting (ft):", font_size=13, color=(0.54, 0.58, 0.68, 1))
        self.add_widget(self.lbl1)
        self.input1 = make_input("Enter value…")
        self.add_widget(self.input1)

        # ── Input 2 ──
        self.lbl2 = make_label("Northing (ft):", font_size=13, color=(0.54, 0.58, 0.68, 1))
        self.add_widget(self.lbl2)
        self.input2 = make_input("Enter value…")
        self.add_widget(self.input2)

        # ── Convert button ──
        self.btn = Button(
            text="▶   Convert",
            font_size=16,
            bold=True,
            background_color=(0.89, 0.69, 0.29, 1),
            color=(0.08, 0.08, 0.12, 1),
            size_hint_y=None, height=52,
        )
        self.btn.bind(on_press=self.do_convert)
        self.add_widget(self.btn)

        # ── Clear button ──
        clr_btn = Button(
            text="Clear",
            font_size=13,
            background_color=(0.15, 0.15, 0.22, 1),
            color=(0.54, 0.58, 0.68, 1),
            size_hint_y=None, height=38,
        )
        clr_btn.bind(on_press=self.do_clear)
        self.add_widget(clr_btn)

        # ── Results box ──
        self.add_widget(make_label("Result:", font_size=13,
                                   color=(0.89, 0.69, 0.29, 1), bold=True))

        result_box = GridLayout(cols=2, size_hint_y=None, height=90, spacing=8)

        self.out_lbl1 = make_label("Easting (m)", font_size=12, color=(0.54, 0.58, 0.68, 1))
        self.out_lbl2 = make_label("Northing (m)", font_size=12, color=(0.54, 0.58, 0.68, 1))
        self.out_val1 = make_label("—", font_size=20, bold=True, color=(0.3, 0.87, 0.5, 1))
        self.out_val2 = make_label("—", font_size=20, bold=True, color=(0.3, 0.87, 0.5, 1))

        result_box.add_widget(self.out_lbl1)
        result_box.add_widget(self.out_lbl2)
        result_box.add_widget(self.out_val1)
        result_box.add_widget(self.out_val2)
        self.add_widget(result_box)

        # ── Error label ──
        self.err_lbl = make_label("", font_size=12, color=(0.97, 0.32, 0.29, 1))
        self.add_widget(self.err_lbl)

        # ── Footer ──
        self.add_widget(make_label(
            "War Office (Clarke 1880) · Transverse Mercator · EPSG:1029",
            font_size=10, color=(0.35, 0.38, 0.46, 1), halign="center"))

    def on_conversion_change(self, spinner, text):
        conv = CONVERSIONS[text]
        self.lbl1.text = conv["labels"][0] + ":"
        self.lbl2.text = conv["labels"][1] + ":"
        self.out_lbl1.text = conv["out_labels"][0]
        self.out_lbl2.text = conv["out_labels"][1]
        self.out_val1.text = "—"
        self.out_val2.text = "—"
        self.err_lbl.text  = ""
        self.input1.text   = ""
        self.input2.text   = ""

    def do_convert(self, instance):
        self.err_lbl.text = ""
        conv = CONVERSIONS[self.spinner.text]
        try:
            v1 = float(self.input1.text)
            v2 = float(self.input2.text)
        except ValueError:
            self.err_lbl.text = "⚠  Please enter valid numbers in both fields."
            return
        try:
            r1, r2 = conv["func"](v1, v2)
            self.out_val1.text = f"{r1:,.3f}"
            self.out_val2.text = f"{r2:,.3f}"
        except Exception as e:
            self.err_lbl.text = f"⚠  Error: {str(e)}"

    def do_clear(self, instance):
        self.input1.text  = ""
        self.input2.text  = ""
        self.out_val1.text = "—"
        self.out_val2.text = "—"
        self.err_lbl.text  = ""


# ─── APP ──────────────────────────────────────────────────────────────────────

class GhanaProjectionApp(App):
    def build(self):
        self.title = "Ghana Projection Tool"
        scroll = ScrollView()
        scroll.add_widget(GhanaLayout(size_hint_y=None, height=700))
        return scroll


if __name__ == "__main__":
    GhanaProjectionApp().run()
