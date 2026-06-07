import random
import os
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.audio import SoundLoader
from kivy.metrics import dp, sp
from kivy.animation import Animation

Window.softinput_mode = 'below_target'
Window.clearcolor = get_color_from_hex('#B3E5FC')

HINT_IMAGE_PATH = 'hint_icon.png' if os.path.exists('hint_icon.png') else ('hint_icon.jpg' if os.path.exists('hint_icon.jpg') else None)

# --- UI COMPONENTS ---
class StyledButton(Button):
    def __init__(self, bg_color='#1976D2', radius=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.btn_color = bg_color
        self.radius = radius or [dp(15)]
        with self.canvas.before:
            self.color_instruction = Color(rgba=get_color_from_hex(self.btn_color))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def change_color(self, hex_color):
        self.btn_color = hex_color
        self.color_instruction.rgba = get_color_from_hex(hex_color)

class StyledCard(BoxLayout):
    def __init__(self, bg_color='#FFFFFF', radius=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius or [dp(15)]
        with self.canvas.before:
            self.bg_color_inst = Color(rgba=get_color_from_hex(self.bg_color))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class HistoryItem(StyledCard):
    def __init__(self, sender, word, status="correct", error_msg="", category_tag="", **kwargs):
        if status == "correct":
            bg = '#E8F5E9' if sender == "YOU" else '#E3F2FD'
            status_symbol = "[color=#4CAF50][b][OK][/b][/color]"
        elif status == "warning":
            bg = '#FFF8E1'
            status_symbol = "[color=#FF9800][b][!][/b][/color]"
        else:
            bg = '#FFEBEE'
            status_symbol = "[color=#F44336][b][X][/b][/color]"

        super().__init__(bg_color=bg, radius=[dp(10)], orientation='vertical', padding=[dp(8), dp(6), dp(8), dp(6)], spacing=dp(4), size_hint_y=None, **kwargs)
        self.height = dp(68) if error_msg else dp(48)

        meta_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(16), spacing=dp(6))
        badge_bg = '#4CAF50' if sender == "YOU" else '#1976D2'
        
        badge_card = StyledCard(bg_color=badge_bg, radius=[dp(4)], size_hint=(None, None), size=(dp(34), dp(14)))
        badge_lbl = Label(text=sender, font_size='9sp', bold=True, color=(1,1,1,1))
        badge_card.add_widget(badge_lbl)
        meta_row.add_widget(badge_card)
        
        if category_tag:
            tag_card = StyledCard(bg_color='#78909C', radius=[dp(4)], size_hint=(None, None), size=(dp(38), dp(14)))
            tag_lbl = Label(text=category_tag, font_size='8sp', bold=True, color=(1,1,1,1))
            tag_card.add_widget(tag_lbl)
            meta_row.add_widget(tag_card)
            
        self.add_widget(meta_row)

        content_row = BoxLayout(orientation='horizontal', spacing=dp(4), size_hint_y=1)
        flag_lbl = Label(text="►", font_size='10sp', color=(0.5, 0.5, 0.5, 1), size_hint_x=None, width=dp(12), halign='left')
        content_row.add_widget(flag_lbl)

        word_lbl = Label(text=f"[b]{word.title()}[/b]", markup=True, font_size='13sp', color=(0,0,0,1), halign='left', valign='middle')
        word_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        content_row.add_widget(word_lbl)

        status_lbl = Label(text=status_symbol, markup=True, font_size='14sp', bold=True, size_hint_x=None, width=dp(20), halign='right')
        content_row.add_widget(status_lbl)
        self.add_widget(content_row)

        if error_msg:
            err_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(14))
            err_lbl = Label(text=error_msg, font_size='10sp', color=get_color_from_hex('#C62828'), halign='left', valign='top')
            err_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
            err_row.add_widget(err_lbl)
            self.add_widget(err_row)

# --- SCREENS ---
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        with layout.canvas.before:
            if os.path.exists('background.png'):
                self.bg_rect = Rectangle(source='background.png', pos=layout.pos, size=layout.size)
            else:
                Color(rgba=get_color_from_hex('#B3E5FC'))
                self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        rules_card = StyledCard(orientation='vertical', padding=dp(16), spacing=dp(12), bg_color='#FFFFFF', size_hint=(0.85, 0.45), pos_hint={'center_x': 0.5, 'top': 0.88})
        
        title_box = BoxLayout(orientation='horizontal', size_hint_y=0.18, spacing=dp(8))
        title_lbl = Label(text="[b][color=#1976D2]■ HOW TO PLAY :-[/color][/b]", markup=True, font_size='22sp', halign='left', valign='middle')
        title_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        title_box.add_widget(title_lbl)
        rules_card.add_widget(title_box)

        lbl1 = Label(text="● 1. Name a place starting with the last letter of the previous item. Mixed mode starts with 3 Lives.", color=get_color_from_hex('#0D47A1'), font_size='13sp', halign='left', valign='middle')
        lbl1.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl1)
        
        lbl2 = Label(text="● 2. Mixed Category Bonus Points: Countries = 10, States/Continents = 15, Capitals = 25! Wrong answers drain clock time.", color=get_color_from_hex('#0D47A1'), font_size='13sp', halign='left', valign='middle')
        lbl2.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl2)
        
        lbl3 = Label(text="● 3. Switch game systems below. Country Only mode removes the life system entirely!", color=get_color_from_hex('#0D47A1'), font_size='13sp', halign='left', valign='middle')
        lbl3.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl3)
        layout.add_widget(rules_card)

        play_btn = StyledButton(text="PLAY", bold=True, font_size='30sp', bg_color='#4CAF50', size_hint=(None, None), size=(dp(120), dp(120)), pos_hint={'center_x': 0.5, 'center_y': 0.36}, radius=[dp(60)])
        play_btn.bind(on_release=self.go_to_game)
        layout.add_widget(play_btn)
        
        # THE ZERO-RISK STATS BUTTON (NOW POINTING TO THE RAW API DATA)
        stats_btn = StyledButton(
            text="📊 Live Game Stats", 
            bold=True, 
            font_size='13sp', 
            bg_color='#0D47A1', 
            size_hint=(None, None), 
            size=(dp(160), dp(38)), 
            pos_hint={'center_x': 0.5, 'center_y': 0.23}, 
            radius=[dp(12)]
        )
        
        # This link skips the dashboard and shows the direct {"value": X} string
        stats_btn.bind(on_release=lambda x: webbrowser.open("https://api.counterapi.dev/v1/singhakshit_word_game_production/total_downloads"))
        layout.add_widget(stats_btn)

        mode_box = BoxLayout(orientation='horizontal', size_hint=(0.85, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.14}, spacing=dp(12))
        self.btn_country_only = StyledButton(text="Countries Only", bold=True, font_size='13sp', bg_color='#1976D2', radius=[dp(10)])
        self.btn_country_only.bind(on_release=lambda x: App.get_running_app().select_game_mode("country"))
        self.btn_all_combined = StyledButton(text="All-In-One Mixed", bold=True, font_size='13sp', bg_color='#78909C', radius=[dp(10)])
        self.btn_all_combined.bind(on_release=lambda x: App.get_running_app().select_game_mode("all"))
        
        mode_box.add_widget(self.btn_country_only)
        mode_box.add_widget(self.btn_all_combined)
        layout.add_widget(mode_box)
        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def go_to_game(self, *args):
        app = App.get_running_app()
        if hasattr(app, 'hint_sound') and app.hint_sound:
            app.hint_sound.play()
        self.manager.current = 'game'
        app.restart_game()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            if os.path.exists('background.png'):
                self.bg_rect = Rectangle(source='background.png', pos=self.layout.pos, size=self.layout.size)
            else:
                Color(rgba=get_color_from_hex('#B3E5FC'))
                self.bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.update_bg, size=self.update_bg)
        
        stats_grid = GridLayout(cols=4, spacing=dp(10), size_hint=(0.95, 0.1), pos_hint={'center_x': 0.5, 'top': 0.88})

        self.score_lbl = self.create_stat(stats_grid, "SCORE", "0", "#2196F3")
        self.timer_lbl = self.create_stat(stats_grid, "TIME LEFT", "30s", "#4CAF50")
        self.best_lbl = self.create_stat(stats_grid, "BEST", "0", "#9C27B0")
        self.lives_lbl = self.create_stat(stats_grid, "LIVES", "3 / 3", "#E91E63")
        self.layout.add_widget(stats_grid)

        content_area = BoxLayout(orientation='horizontal', size_hint=(0.95, 0.58), pos_hint={'center_x': 0.5, 'top': 0.76}, spacing=dp(15))
        
        self.card_wrapper = FloatLayout(size_hint_x=0.58)
        self.game_card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(12), size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        self.game_card.add_widget(Label(text="LAST LETTER", color=(0.5,0.5,0.5,1), size_hint_y=0.1))
        
        self.letter_box = StyledCard(bg_color='#E3F2FD', radius=[dp(10)], size_hint_y=0.3)
        self.last_letter_lbl = Label(text="?", font_size='80sp', bold=True, color=get_color_from_hex('#1976D2'), markup=True)
        self.letter_box.add_widget(self.last_letter_lbl)
        self.game_card.add_widget(self.letter_box)

        self.instruction = Label(text="Enter an item!", color=(0,0,0,1), markup=True, font_size='13sp', halign='center', valign='middle', size_hint_y=0.1)
        self.instruction.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        self.game_card.add_widget(self.instruction)

        hint_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10), padding=[0, dp(4)])
        hint_info_lbl = Label(text="Need a country? (Costs 50 pts)", font_size='11sp', color=(0.4, 0.4, 0.4, 1), halign='left', valign='middle')
        hint_info_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        hint_row.add_widget(hint_info_lbl)

        hint_btn_text = f"[ref=hint][img={HINT_IMAGE_PATH}][/ref]" if HINT_IMAGE_PATH else "[b]HINT[/b]"
        self.hint_btn = StyledButton(text=hint_btn_text, markup=True, font_size='12sp', color=(0,0,0,1), bg_color='#FFC107', size_hint=(None, None), size=(dp(54), dp(36)), radius=[dp(10)])
        self.hint_btn.bind(on_release=lambda x: App.get_running_app().trigger_country_hint())
        hint_row.add_widget(self.hint_btn)
        self.game_card.add_widget(hint_row)
        
        self.user_input = TextInput(hint_text="Type response here...", multiline=False, size_hint_y=None, height=dp(55), padding=[dp(10), dp(15)])
        self.user_input.bind(on_text_validate=lambda x: App.get_running_app().handle_turn())
        self.game_card.add_widget(self.user_input)

        self.submit_btn = StyledButton(text="SUBMIT", bold=True, bg_color='#9CEF43', size_hint_y=None, height=dp(50))
        self.submit_btn.bind(on_release=lambda x: App.get_running_app().handle_turn())
        self.game_card.add_widget(self.submit_btn)
        
        self.card_wrapper.add_widget(self.game_card)
        content_area.add_widget(self.card_wrapper)

        history_card = StyledCard(orientation='vertical', padding=dp(10), size_hint_x=0.42)
        history_card.add_widget(Label(text="RESPONSE HISTORY", bold=True, color=get_color_from_hex('#1976D2'), size_hint_y=0.08, font_size='12sp'))
        
        self.history_scroll = ScrollView(do_scroll_x=False)
        self.history_scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=[dp(2), dp(2)])
        self.history_scroll_layout.bind(minimum_height=self.history_scroll_layout.setter('height'))
        
        self.history_scroll.add_widget(self.history_scroll_layout)
        history_card.add_widget(self.history_scroll) 
        content_area.add_widget(history_card)
        self.layout.add_widget(content_area)

        bottom_btns = BoxLayout(size_hint=(0.95, 0.08), pos_hint={'center_x': 0.5, 'y': 0.04}, spacing=dp(20))
        restart_btn = StyledButton(text="RESTART", bg_color='#1976D2', bold=True)
        restart_btn.bind(on_release=lambda x: App.get_running_app().restart_game())
        exit_btn = StyledButton(text="EXIT", bg_color='#F44336', bold=True)
        exit_btn.bind(on_release=self.go_to_start)
        bottom_btns.add_widget(restart_btn)
        bottom_btns.add_widget(exit_btn)
        self.layout.add_widget(bottom_btns)
        self.add_widget(self.layout)

    def create_stat(self, parent, title, val, color):
        card = StyledCard(orientation='vertical', padding=dp(5))
        card.add_widget(Label(text=title, font_size='10sp', color=(0.4,0.4,0.4,1)))
        v = Label(text=val, font_size='14sp', bold=True, color=get_color_from_hex(color))
        card.add_widget(v)
        parent.add_widget(card)
        return v

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def go_to_start(self, *args):
        self.manager.current = 'start'
        app = App.get_running_app()
        if app.timer_event: Clock.unschedule(app.timer_event)
        if app.bot_timer_event: Clock.unschedule(app.bot_timer_event)


# --- MAIN APP ---
class AtlasApp(App):
    def build(self):
        self.countries = ["afghanistan", "albania", "algeria","america", "andorra", "angola","antigua & deps", "argentina", "armenia", "australia", "austria","azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados","belarus", "belgium", "belize", "benin", "bhutan","bolivia", "bosnia herzegovina", "botswana", "brazil","brunei","bulgaria", "burkina", "burundi", "cambodia", "cameroon","canada", "cape verde", "central african rep", "chad", "chile","china", "colombia", "comoros", "congo", "cong","costa rica", "croatia", "cuba", "cyprus", "czech republic","denmark", "djibouti", "dominica", "dominican republic", "east timor","ecuador", "egypt", "el salvador", "equatorial guinea", "eritrea","estonia", "ethiopia", "fiji", "finland", "france","gabon", "gambia", "georgia", "germany", "ghana","greece", "grenada", "guatemala", "guinea", "guinea-bissau","guyana", "haiti", "honduras", "hungary", "iceland","india", "indonesia", "iran", "iraq", "ireland","israel", "italy", "ivory coast", "jamaica", "japan","jordan", "kazakhstan", "kenya", "kiribati", "north korea","south korea", "kosovo", "kuwait", "kyrgyzstan", "laos","latvia", "lebanon", "lesotho", "liberia", "libya","liechtenstein", "lithuania", "luxembourg", "macedonia", "madagascar","malawi", "malaysia", "maldives", "mali", "malta","marshall islands", "mauritania", "mauritius", "mexico", "micronesia","moldova", "monaco", "mongolia", "montenegro", "morocco","mozambique", "myanmar", "namibia", "nauru", "nepal","netherlands", "new zealand", "nicaragua", "niger", "nigeria","norway", "oman", "pakistan", "palau", "panama","papua new guinea", "paraguay", "peru", "philippines", "poland","portugal", "qatar", "romania", "russia", "rwanda","st kitts & nevis", "st lucia", "saint vincent & the grenadines","samoa", "san marino", "sao tome & principe", "saudi arabia","senegal", "serbia", "seychelles", "sierra leone", "singapore","slovakia", "slovenia", "solomon islands","somalia", "south africa","south sudan", "spain", "sri lanka", "sudan", "suriname","swaziland", "sweden", "switzerland", "syria", "taiwan","tajikistan", "tanzania", "thailand", "togo", "tonga","trinidad & tobago", "tunisia", "turkey", "turkmenistan", "tuvalu","uganda", "ukraine", "united arab emirates", "united kingdom","united states", "uruguay", "uzbekistan", "vanuatu","vatican city", "venezuela", "vietnam", "yemen","zambia", "zimbabwe"]
        self.continents = ["asia", "africa", "north america", "south america", "antarctica", "europe", "australia"]
        self.capitals = ["algiers", "luanda", "porto-novo", "gaborone", "praia", "yaounde", "bangui", "moroni", "cairo", "djibouti", "asmara", "malabo", "libreville", "accra", "conakry", "bissau", "nairobi", "maseru", "monrovia", "tripoli", "antananarivo", "lilongwe", "bamako", "nouakchott", "port louis", "rabat", "maputo", "windhoek", "niamey", "abuja", "kigali", "dakar", "victoria", "freetown", "mogadishu", "pretoria", "juba", "khartoum", "dodoma", "lome", "tunis", "kampala", "lusaka", "harare", "kabul", "yerevan", "baku", "manama", "dhaka", "thimphu", "beijing", "nicosia", "tbilisi", "new delhi", "delhi", "jakarta", "tehran", "baghdad", "tokyo", "amman", "astana", "kuwait city", "bishkek", "vientiane", "beirut", "kuala lumpur", "male", "ulaanbaatar", "kathmandu", "pyongyang", "muscat", "islamabad", "manila", "doha", "riyadh", "singapore", "seoul", "damascus", "taipei", "dushanbe", "bangkok", "dili", "ankara", "ashgabat", "abu dhabi", "tashkent", "hanoi", "sanaa", "tirana", "vienna", "minsk", "brussels", "sofia", "zagreb", "prague", "copenhagen", "tallinn", "helsinki", "paris", "berlin", "athens", "budapest", "reykjavik", "dublin", "rome", "riga", "vilnius", "luxembourg", "valletta", "chisinau", "monaco", "amsterdam", "oslo", "warsaw", "lisbon", "bucharest", "moscow", "san marino", "belgrade", "bratislava", "ljubljana", "madrid", "stockholm", "bern", "kyiv", "london", "vatican city", "ottawa", "havana", "mexico city", "washington", "canberra", "wellington", "buenos aires", "brasília", "santiago", "bogota", "quito", "asuncion", "lima", "paramaribo", "montevideo", "caracas"]
        self.states = [#india
"andaman and nicobar islands", "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chandigarh", "chhattisgarh", "dadra and nagar haveli", "daman and diu", "delhi", "goa", "gujarat", "haryana", "himachal pradesh", "jammu and kashmir", "jharkhand", "karnataka", "kerala", "ladakh", "lakshadweep", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "puducherry", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
#america
"alabama","alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
#Austrailia
"queensland", "south australia",
"tasmania", "victoria", 
#canada
"alberta","british columbia", "manitoba", "new brunswick","nova scotia", "nunavut", "ontario", "quebec", "saskatchewan", "yukon",
#UK
"england", "scotland", "wales", "northern ireland",
#Germany
"bavaria", "berlin", "brandenburg", "bremen", "hamburg", "hesse", "saarland", "saxony", "thuringia",
#Brazil
"acre", "alagoas", "amapa", "amazonas", "bahia", "ceara", "distrito federal", "espirito santo", "goias", "maranhao", "mato grosso", "minas gerais", "para", "paraiba", "parana", "pernambuco", "piaui", "rio de janeiro", "rio grande do norte", "rio grande do sul", "rondonia", "roraima", "santa catarina", "sao paulo", "sergipe", "tocantins",
#mexico
"aguascalientes", "baja california", "campeche", "chiapas", "chihuahua", "coahuila", "colima", "durango", "guanajuato", "guerrero", "hidalgo", "jalisco", "mexico", "michoacan", "morelos", "nayarit", "nuevo leon", "oaxaca", "puebla", "queretaro", "sinaloa", "sonora", "tabasco", "tamaulipas", "tlaxcala", "veracruz", "yucatan", "zacatecas",
#chinese
"anhui", "beijing", "chongqing", "fujian", "gansu", "guangdong", "guangxi", "guizhou", "hainan", "hebei", "heilongjiang", "henan", "hubei", "hunan", "inner mongolia", "jiangsu", "jiangxi", "jilin", "liaoning", "ningxia", "qinghai", "shaanxi", "shandong", "shanghai", "shanxi", "sichuan", "tianjin", "tibet", "xinjiang", "yunnan", "zhejiang",
#Japan
"hokkaido","aomori",
"iwate","miyagi","akita","yamagata","fukushima","ibaraki","tochigi","gunma","saitama","chiba","tokyo","kanagawa","niigata","toyama","ishikawa","fukui","yamanashi","nagano","gifu","shizuoka","aichi","mie","shiga","kyoto","osaka","hyogo","nara","wakayama","tottori","shimane","okayama","hiroshima","yamaguchi","tokushima","kagawa","ehime","kochi","fukuoka","saga","nagasaki","kumamoto","oita","miyazaki","kagoshima","okinawa",
#pakistan
"sindh","khyber pakhtunkhwa","balochistan","islamabad",
#indonesia
"aceh","riau","jambi","sumatra","bengkulu","lampung","riau islands","dki jakarta","yogyakarta","banten","bali","west nusa tenggara","kalimantan","sulawesi","gorontalo","maluku","papua",
#france
"brittany", "corsica","normandy", "occitanie", "guadeloupe", "martinique", "guyane","mayotte","paris"
#italy
"piedmont","lombardy","veneto", "liguria", "tuscany", "umbria", "marche", "lazio", "abruzzo", "molise", "campania", "apulia", "basilicata", "calabria", "sicily", "sardinia",
#Spain
"andalusia", "aragon", "asturias", "balearic islands","canary islands", "cantabria", "castile and leon","catalonia", "extremadura", "galicia","madrid", "murcia", "navarre", "valencian community", "ceuta",
#Russia
"moscow", "saint petersburg",
#argentina
"buenos aires", "catamarca", "chaco", "chubut", "cordoba", "corrientes", "entre rios", "formosa", "jujuy", "la pampa", "la rioja", "mendoza", "misiones", "neuquen", "rio negro", "salta", "san juan", "san luis", "santa cruz", "santa fe", "tucuman",
#columbia
"amazonas", "antioquia", "arauca", "atlantico", "bolivar", "boyaca", "caldas", "caqueta", "casanare", "cauca", "cesar", "choco", "cordoba", "cundinamarca", "guainia", "guaviare", "huila", "magdalena", "meta", "narino", "norte de santander", "putumayo", "quindio", "risaralda", "san andres y providencia", "santander", "sucre", "tolima", "vaupes", "vichada",
#peru
"amazonas", "ancash", "apurimac", "arequipa", "ayacucho", "cajamarca", "callao", "cusco", "huancavelica", "huanuco", "ica", "junin", "la libertad", "lambayeque", "lima", "loreto", "moquegua", "pasco", "piura", "puno", "san martin", "tacna", "tumbes", "ucayali",
#Nigeria
"abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue", "borno", "cross river", "delta", "ebonyi", "edo", "ekiti", "enugu", "gombe", "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi", "kogi", "kwara", "lagos", "nasarawa", "niger", "ogun", "ondo", "osun", "oyo", "plateau", "rivers", "sokoto", "taraba", "yobe", "zamfara",
#south africa
"free state", "gauteng", "limpopo", "mpumalanga", "north west","cape",
#egypt
"cairo", "alexandria", "giza", "qalyubia", "sharqia", "dakahlia", "beheira", "monufia", "gharbia", "kafr el sheikh", "damietta", "port said", "ismailia", "suez", "north sinai", "south sinai", "fayoum", "beni suef", "minya", "asyut", "sohag", "qena", "luxor", "aswan", "red sea", "new valley", "matruh",
#newzealand
"northland", "auckland", "waikato", "bay of plenty", "gisborne", "hawke's bay", "taranaki", "wellington", "tasman", "nelson", "marlborough", "west coast", "canterbury", "otago", "southland",]

        self.item_types = {}
        for item in self.countries: self.item_types[item] = "C"
        for item in self.capitals: self.item_types[item] = "Cap"
        for item in self.continents: self.item_types[item] = "Cont"
        for item in self.states: self.item_types[item] = "S"

        self.point_weights = {"C": 10, "Cont": 15, "S": 15, "Cap": 25}

        self.sm = ScreenManager(transition=FadeTransition())
        self.start_screen = StartScreen(name='start')
        self.game_screen = GameScreen(name='game')
        self.sm.add_widget(self.start_screen)
        self.sm.add_widget(self.game_screen)
        return self.sm

    @property
    def gs(self):
        return self.sm.get_screen('game')

    def select_game_mode(self, mode_selection):
        self.game_mode = mode_selection
        if mode_selection == "country":
            self.start_screen.btn_country_only.change_color('#1976D2')
            self.start_screen.btn_all_combined.change_color('#78909C')
        else:
            self.start_screen.btn_country_only.change_color('#78909C')
            self.start_screen.btn_all_combined.change_color('#9C27B0')

    def on_start(self):
        Clock.schedule_once(self.deferred_game_init, 0.1)

    def deferred_game_init(self, dt):
        self.game_mode = "country"
        self.active_pool = list(self.countries) 
        self.used_countries = []
        self.bot_country = ""
        self.score = 0
        self.best_score = 0
        
        self.player_lives = 3
        self.bot_lives = 3
        self.bot_timeout_count = 0
        self.bot_is_panicking = False
        self.bot_panic_cooldown = 0
        
        self.timer_seconds = 30
        self.timer_event = None
        self.bot_timer_event = None
        self.first_turn = True

        try:
            self.success_sound = SoundLoader.load('success.wav') if os.path.exists('success.wav') else None
            self.fail_sound = SoundLoader.load('fail.wav') if os.path.exists('fail.wav') else None
            self.victory_sound = SoundLoader.load('victory.wav') if os.path.exists('victory.wav') else None
            self.hint_sound = SoundLoader.load('him.wav') if os.path.exists('him.wav') else None
            self.tick_sound = SoundLoader.load('tick.wav') if os.path.exists('tick.wav') else None
            if self.tick_sound: self.tick_sound.stop()
        except:
            self.success_sound = self.fail_sound = self.victory_sound = self.hint_sound = self.tick_sound = None

    def refresh_lives_display(self):
        if self.game_mode == "country":
            self.gs.lives_lbl.text = "N/A"
        else:
            self.gs.lives_lbl.text = f"{self.player_lives} / {self.bot_lives}"

    def add_history_item(self, sender, word, status="correct", error_msg="", category_tag=""):
        item = HistoryItem(sender=sender, word=word, status=status, error_msg=error_msg, category_tag=category_tag)
        item.opacity = 0
        self.gs.history_scroll_layout.add_widget(item)
        Animation(opacity=1, duration=0.2).start(item)
        Clock.schedule_once(lambda dt: setattr(self.gs.history_scroll, 'scroll_y', 0))

    def trigger_shake(self):
        card = self.gs.game_card
        Animation.cancel_all(card)
        shake = (
            Animation(pos_hint={'center_x': 0.47}, duration=0.04) +
            Animation(pos_hint={'center_x': 0.53}, duration=0.04) +
            Animation(pos_hint={'center_x': 0.48}, duration=0.04) +
            Animation(pos_hint={'center_x': 0.52}, duration=0.04) +
            Animation(pos_hint={'center_x': 0.5}, duration=0.04)
        )
        shake.start(card)

    def handle_turn(self, *args):
        val = self.gs.user_input.text.strip().lower()
        if not val or self.gs.user_input.disabled: return
        self.gs.user_input.text = ""

        if val in ["don't know", "skip", "quit"]:
            if self.game_mode == "country":
                self.add_history_item("YOU", "Forgot", status="error", error_msg="Game Over")
                if self.fail_sound: self.fail_sound.play()
                self.game_over("You gave up!")
            else:
                self.add_history_item("YOU", "Forgot", status="error", error_msg="Lost 1 Life")
                if self.fail_sound: self.fail_sound.play()
                self.deduct_life(player=True, reason="You skipped!")
            return

        if not self.first_turn and not val.startswith(self.bot_country[-1]):
            self.gs.instruction.text = f"Wrong! Must start with '{self.bot_country[-1].upper()}'"
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val or "?", status="error", error_msg="Wrong Starting Letter")
            self.trigger_shake()
            return 
        
        if val not in self.active_pool:
            self.gs.instruction.text = "Not recognized in database!"
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val, status="error", error_msg="Not Valid")
            self.trigger_shake()
            return

        if val in self.used_countries:
            self.gs.instruction.text = "Already played!"
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val, status="warning", error_msg="Repeated Word")
            self.trigger_shake()
            return

        # CORRECT ANSWER LOGIC
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.success_sound: self.success_sound.play()
        
        if self.bot_panic_cooldown > 0:
            self.bot_panic_cooldown -= 1
        
        display_tag = self.item_types.get(val, "C") if self.game_mode != "country" else "C"
        earned_pts = self.point_weights.get(display_tag, 10)
        self.score += earned_pts
        self.gs.score_lbl.text = str(self.score)
        
        score_pop = Animation(font_size=sp(22), duration=0.12) + Animation(font_size=sp(14), duration=0.1)
        score_pop.start(self.gs.score_lbl)

        self.used_countries.append(val)
        self.add_history_item("YOU", val, status="correct", category_tag=display_tag if self.game_mode != "country" else "")
        
        self.first_turn = False
        self.gs.user_input.disabled = True
        self.bot_is_panicking = False
        self.start_timer()
        self.gs.instruction.text = "Bot thinking..."
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
        self.bot_timer_event = Clock.schedule_once(lambda dt: self.bot_check_turn(val[-1]), random.uniform(1.0, 7.5))

    def bot_check_turn(self, char):
        possible = [c for c in self.active_pool if c.startswith(char) and c not in self.used_countries]
        
        if not possible:
            if self.game_mode == "country":
                if self.timer_event: Clock.unschedule(self.timer_event)
                if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
                try:
                    if self.tick_sound: self.tick_sound.stop()
                except: pass
                
                if self.victory_sound: self.victory_sound.play()
                self.gs.instruction.text = "[b][color=#4CAF50]VICTORY![/color][/b]\nBot has no answers left!"
                self.gs.last_letter_lbl.text = "[color=#FFC107]W[/color]"
                self.update_best_score()
                self.gs.user_input.disabled = True
                
                self.trigger_shake()
            else:
                self.gs.instruction.text = "Bot stuck! Bot loses a life. [OK]"
                self.deduct_life(player=False, reason="Bot had no answers left!")
            return

        if self.game_mode != "country" and self.bot_timeout_count < 2 and self.bot_panic_cooldown == 0 and random.random() < 0.20:
            self.bot_timeout_count += 1
            self.bot_panic_cooldown = random.randint(4, 6)
            self.bot_is_panicking = True
            self.gs.instruction.text = "Bot looks confused... Time is ticking!"
            return

        self.bot_move(possible)

    def bot_move(self, possible_options):
        if self.success_sound: self.success_sound.play()

        # SMART BOT LOGIC: Prioritize Countries, Continents, and Capitals over States
        if self.game_mode != "country":
            premium_options = [c for c in possible_options if self.item_types.get(c, "C") in ["C", "Cap", "Cont"]]
            fallback_options = [c for c in possible_options if self.item_types.get(c, "C") == "S"]

            if premium_options:
                self.bot_country = random.choice(premium_options)
            else:
                self.bot_country = random.choice(fallback_options)
        else:
            self.bot_country = random.choice(possible_options)

        self.used_countries.append(self.bot_country.lower())
        
        display_tag = self.item_types.get(self.bot_country, "C") if self.game_mode != "country" else "C"
        
        self.add_history_item("BOT", self.bot_country, status="correct", category_tag=display_tag if self.game_mode != "country" else "")
        self.gs.last_letter_lbl.text = self.bot_country[-1].upper()
        
        self.gs.instruction.text = f"Bot played: {self.bot_country.upper()}"
        self.gs.user_input.disabled = False
        self.start_timer()

    def deduct_life(self, player, reason):
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
        self.bot_is_panicking = False
        
        try:
            if self.tick_sound: self.tick_sound.stop()
        except: pass

        if self.game_mode == "country": return

        if player:
            self.player_lives -= 1
        else:
            self.bot_lives -= 1
            
        self.refresh_lives_display()
        
        if self.player_lives <= 0:
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", "MATCH OVER", status="error", error_msg="Defeat!")
            self.game_over("Defeat! You ran out of lives.")
            self.gs.last_letter_lbl.text = "[color=#FF0000]L[/color]"
        elif self.bot_lives <= 0:
            if self.victory_sound: self.victory_sound.play()
            self.add_history_item("YOU", "VICTORY!", status="correct", error_msg="Match Won!")
            self.gs.instruction.text = "[b][color=#4CAF50]VICTORY![/color][/b]\nYou completely knocked out the bot!"
            self.gs.last_letter_lbl.text = "[color=#FFC107]W[/color]"
            self.update_best_score()
            self.gs.user_input.disabled = True
            
            self.trigger_shake()
        else:
            if not player and self.fail_sound: self.fail_sound.play()
            self.gs.user_input.disabled = False
            self.first_turn = True
            self.gs.instruction.text = f"{reason}! Fresh turn, play any item."
            self.gs.last_letter_lbl.text = "?"
            self.start_timer()

    def start_timer(self):
        if self.timer_event: Clock.unschedule(self.timer_event)
        try:
            if self.tick_sound: self.tick_sound.stop()
        except: pass
        self.timer_seconds = 30
        self.gs.timer_lbl.text = "30s"
        self.gs.timer_lbl.font_size = '14sp'
        self.gs.timer_lbl.color = get_color_from_hex("#4CAF50")
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.timer_seconds -= 1
        self.gs.timer_lbl.text = f"{self.timer_seconds}s"
        
        if self.timer_seconds <= 15:
            self.gs.timer_lbl.color = get_color_from_hex("#F44336")
            try:
                if self.tick_sound: self.tick_sound.play()
            except: pass
            danger_pulse = (Animation(font_size=sp(24), duration=0.12, transition='out_quad') + Animation(font_size=sp(14), duration=0.12, transition='in_quad'))
            danger_pulse.start(self.gs.timer_lbl)

        if self.timer_seconds <= 0:
            if self.timer_event: Clock.unschedule(self.timer_event)
            
            if self.game_mode == "country":
                self.add_history_item("YOU", "TIMEOUT", status="error", error_msg="Game Over")
                if self.fail_sound: self.fail_sound.play()
                self.game_over("Time Out!")
                self.gs.last_letter_lbl.text = "[color=#FF0000]X[/color]"
            else:
                if self.bot_is_panicking:
                    self.add_history_item("BOT", "TIMEOUT", status="error", error_msg="Panic Lockout")
                    if self.fail_sound: self.fail_sound.play()
                    self.deduct_life(player=False, reason="Bot Timeout")
                else:
                    self.add_history_item("YOU", "TIMEOUT", status="error", error_msg="Out of time!")
                    if self.fail_sound: self.fail_sound.play()
                    self.deduct_life(player=True, reason="Time Out")

    def game_over(self, reason):
        try:
            if self.tick_sound: self.tick_sound.stop()
        except: pass
        self.gs.user_input.disabled = True
        self.update_best_score()
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)

        target_char = random.choice([c for c in self.active_pool]) if self.first_turn else self.bot_country[-1]
        missed_options = [c for c in self.active_pool if c.startswith(target_char) and c not in self.used_countries]
        if missed_options:
            suggestion = random.choice(missed_options).upper()
            self.gs.instruction.text = f"Match Over! Missed suggestion: {suggestion}"
        else:
            self.gs.instruction.text = f"Match Over! No answers left anywhere."

    def update_best_score(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.gs.best_lbl.text = str(self.best_score)

    def restart_game(self, *args):
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
        try:
            if self.tick_sound: self.tick_sound.stop()
        except: pass
        
        if self.game_mode == "country":
            self.active_pool = list(self.countries)
            self.gs.instruction.text = "Enter a country!"
        else:
            self.active_pool = self.countries + self.continents + self.capitals + self.states
            self.gs.instruction.text = "Enter Country, Capital,\n Continent, or State!"

        self.player_lives = 3
        self.bot_lives = 3
        self.bot_timeout_count = 0
        self.bot_panic_cooldown = 0
        self.bot_is_panicking = False
        self.refresh_lives_display()
        
        self.used_countries = []
        self.score = 0
        self.gs.score_lbl.text = "0"
        self.gs.last_letter_lbl.text = "?"
        self.gs.history_scroll_layout.clear_widgets()
        self.gs.user_input.disabled = False
        self.first_turn = True
        self.start_timer()
        
    def trigger_country_hint(self, *args):
        if self.score < 50:
            self.gs.instruction.text = "Locked! You need 50+ score points."
            if self.fail_sound: self.fail_sound.play()
            return

        if hasattr(self, 'hint_sound') and self.hint_sound:
            self.hint_sound.play()

        target_char = ""
        if not self.first_turn and self.bot_country:
            target_char = self.bot_country[-1] if self.bot_country[-1] != " " else self.bot_country[-2]

        if target_char:
            valid_hint_options = [c for c in self.active_pool if c.startswith(target_char) and c not in self.used_countries]
        else:
            valid_hint_options = [c for c in self.active_pool if c not in self.used_countries]

        if not valid_hint_options:
            self.gs.instruction.text = "No countries left for this letter hint!"
            return

        chosen_hint = random.choice(valid_hint_options).upper()
        self.score -= 50
        self.gs.score_lbl.text = str(self.score)
        self.gs.instruction.text = f"Try typing: {chosen_hint}"

        if hasattr(self.gs, 'hint_btn'):
            anim = Animation(size=(dp(60), dp(40)), duration=0.1) + Animation(size=(dp(54), dp(36)), duration=0.1)
            anim.start(self.gs.hint_btn)

if __name__ == '__main__':
    AtlasApp().run()