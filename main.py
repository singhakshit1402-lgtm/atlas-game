import random
import os
import urllib.parse
import json
from kivy.network.urlrequest import UrlRequest
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

# --- UNIVERSAL GRAPHICS TIMELINE HISTORY ITEM ---
class HistoryItem(StyledCard):
    def __init__(self, sender, word, status="correct", error_msg="", **kwargs):
        if status == "correct":
            bg = '#E8F5E9' if sender == "YOU" else '#E3F2FD'
            status_symbol = "[color=#4CAF50][b]✔[/b][/color]"
        elif status == "warning":
            bg = '#FFF8E1'
            status_symbol = "[color=#FF9800][b]! [/b][/color]"
        else:
            bg = '#FFEBEE'
            status_symbol = "[color=#F44336][b]X[/b][/color]"

        super().__init__(bg_color=bg, radius=[dp(10)], orientation='vertical', 
                         padding=[dp(8), dp(6), dp(8), dp(6)], spacing=dp(4), size_hint_y=None, **kwargs)
        
        self.height = dp(68) if error_msg else dp(48)

        meta_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(16))
        badge_bg = '#4CAF50' if sender == "YOU" else '#1976D2'
        
        badge_card = StyledCard(bg_color=badge_bg, radius=[dp(4)], size_hint=(None, None), size=(dp(34), dp(14)))
        badge_lbl = Label(text=sender, font_size='9sp', bold=True, color=(1,1,1,1))
        badge_card.add_widget(badge_lbl)
        meta_row.add_widget(badge_card)
        self.add_widget(meta_row)

        content_row = BoxLayout(orientation='horizontal', spacing=dp(4), size_hint_y=1)
        flag_lbl = Label(text="►", font_size='10sp', color=(0.5, 0.5, 0.5, 1), size_hint_x=None, width=dp(12), halign='left')
        content_row.add_widget(flag_lbl)

        word_lbl = Label(text=f"[b]{word.title()}[/b]", markup=True, font_size='13sp', color=(0,0,0,1), 
                         halign='left', valign='middle')
        word_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        content_row.add_widget(word_lbl)

        status_lbl = Label(text=status_symbol, markup=True, font_size='14sp', bold=True, size_hint_x=None, width=dp(16), halign='right')
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

        rules_card = StyledCard(
            orientation='vertical', padding=dp(16), spacing=dp(12), bg_color='#FFFFFF',
            size_hint=(0.85, 0.42), pos_hint={'center_x': 0.5, 'top': 0.85}
        )
        
        title_box = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=dp(8))
        title_lbl = Label(text="[b][color=#1976D2]■ HOW TO PLAY :-[/color][/b]", markup=True, font_size='22sp', halign='left', valign='middle')
        title_lbl.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        title_box.add_widget(title_lbl)
        rules_card.add_widget(title_box)

        lbl1 = Label(text="● 1. You have to name a Country that starts with the last letter of the previous Country.", color=get_color_from_hex('#0D47A1'), font_size='14sp', halign='left', valign='middle')
        lbl1.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl1)
        
        lbl2 = Label(text="● 2. No country can be repeated. And You get points for each correct answer given within 30 second !! For Example- new york, andhra pradesh,etc\nSo, write like this in example by giving space in between as they written in english !!! ", color=get_color_from_hex('#0D47A1'), font_size='12sp', halign='left', valign='middle')
        lbl2.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl2)
        
        lbl3 = Label(text="● 3. Change modes below to mix in Capitals, Continents, and States...!!!", color=get_color_from_hex('#0D47A1'), font_size='14sp', halign='left', valign='middle')
        lbl3.bind(size=lambda x, s: setattr(x, 'text_size', (x.width, x.height)))
        rules_card.add_widget(lbl3)
        
        layout.add_widget(rules_card)

        play_btn = StyledButton(
            text="PLAY", bold=True, font_size='30sp', bg_color='#4CAF50',
            size_hint=(None, None), size=(dp(120), dp(120)), pos_hint={'center_x': 0.5, 'center_y': 0.38}, radius=[dp(60)]
        )
        play_btn.bind(on_release=self.go_to_game)
        layout.add_widget(play_btn)

        mode_box = BoxLayout(orientation='horizontal', size_hint=(0.85, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.16}, spacing=dp(12))
        self.btn_country_only = StyledButton(text="Countries Only", bold=True, font_size='13sp', bg_color='#1976D2', radius=[dp(10)])
        self.btn_country_only.bind(on_release=lambda x: self.select_game_mode("country"))
        self.btn_all_combined = StyledButton(text="All-In-One Mixed", bold=True, font_size='13sp', bg_color='#78909C', radius=[dp(10)])
        self.btn_all_combined.bind(on_release=lambda x: self.select_game_mode("all"))
        
        mode_box.add_widget(self.btn_country_only)
        mode_box.add_widget(self.btn_all_combined)
        layout.add_widget(mode_box)
        self.add_widget(layout)

    def select_game_mode(self, mode_selection):
        app = App.get_running_app()
        app.game_mode = mode_selection
        if mode_selection == "country":
            self.btn_country_only.change_color('#1976D2')
            self.btn_all_combined.change_color('#78909C')
        else:
            self.btn_country_only.change_color('#78909C')
            self.btn_all_combined.change_color('#9C27B0')

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def go_to_game(self, *args):
        self.manager.current = 'game'
        app = App.get_running_app()
        if hasattr(app, 'restart_game'):
            app.restart_game()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        app = App.get_running_app()
        
        # Sleek Floating Download Tally Badge in the Top Right Corner
        download_badge = StyledCard(
            bg_color='#0D47A1', radius=[dp(12)], 
            orientation='horizontal', padding=[dp(10), dp(4), dp(10), dp(4)],
            size_hint=(None, None), size=(dp(100), dp(25)),
            pos_hint={'right': 0.98, 'top': 0.98}
        )
        
        app.top_download_lbl = Label(
            text="Downloads: ...", font_size='12sp', 
            bold=True, color=(1, 1, 1, 1), halign='center', valign='middle'
        )
        download_badge.add_widget(app.top_download_lbl)
        self.layout.add_widget(download_badge)

        with self.layout.canvas.before:
            if os.path.exists('background.png'):
                self.bg_rect = Rectangle(source='background.png', pos=self.layout.pos, size=self.layout.size)
            else:
                Color(rgba=get_color_from_hex('#B3E5FC'))
                self.bg_rect = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.update_bg, size=self.update_bg)
        
        stats_grid = GridLayout(cols=4, spacing=dp(10), size_hint=(0.95, 0.1), pos_hint={'center_x': 0.5, 'top': 0.88})

        app.score_lbl = app.create_stat(stats_grid, "SCORE", "0", "#2196F3")
        app.timer_lbl = app.create_stat(stats_grid, "TIME LEFT", "30s", "#4CAF50")
        app.best_lbl = app.create_stat(stats_grid, "BEST", "0", "#9C27B0")
        app.streak_lbl = app.create_stat(stats_grid, "STREAK", "0", "#E91E63")
        self.layout.add_widget(stats_grid)

        content_area = BoxLayout(orientation='horizontal', size_hint=(0.95, 0.58), pos_hint={'center_x': 0.5, 'top': 0.76}, spacing=dp(15))
        game_card = StyledCard(orientation='vertical', padding=dp(15), spacing=dp(12), size_hint_x=0.58)
        game_card.add_widget(Label(text="LAST LETTER", color=(0.5,0.5,0.5,1), size_hint_y=0.1))
        
        app.letter_box = StyledCard(bg_color='#E3F2FD', radius=[dp(10)], size_hint_y=0.3)
        app.last_letter_lbl = Label(text="?", font_size='80sp', bold=True, color=get_color_from_hex('#1976D2'), markup=True)
        app.letter_box.add_widget(app.last_letter_lbl)
        game_card.add_widget(app.letter_box)

        app.instruction = Label(text="Enter an item!", color=(0,0,0,1), font_size='14sp', size_hint_y=0.1)
        game_card.add_widget(app.instruction)

        app.user_input = TextInput(hint_text="Type response here...", multiline=False, size_hint_y=None, height=dp(55), padding=[dp(10), dp(15)])
        app.user_input.bind(on_text_validate=app.handle_turn)
        game_card.add_widget(app.user_input)

        app.submit_btn = StyledButton(text="SUBMIT", bold=True, bg_color='#9CEF43', size_hint_y=None, height=dp(50))
        app.submit_btn.bind(on_release=app.handle_turn)
        game_card.add_widget(app.submit_btn)
        content_area.add_widget(game_card)

        history_card = StyledCard(orientation='vertical', padding=dp(10), size_hint_x=0.42)
        history_card.add_widget(Label(text="RESPONSE HISTORY", bold=True, color=get_color_from_hex('#1976D2'), size_hint_y=0.08, font_size='12sp'))
        
        app.history_scroll = ScrollView(do_scroll_x=False)
        app.history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6), padding=[dp(2), dp(2)])
        app.history_layout.bind(minimum_height=app.history_layout.setter('height'))
        
        app.history_scroll.add_widget(app.history_layout)
        history_card.add_widget(app.history_scroll)
        content_area.add_widget(history_card)
        content_area.bind()
        self.layout.add_widget(content_area)

        bottom_btns = BoxLayout(size_hint=(0.95, 0.08), pos_hint={'center_x': 0.5, 'y': 0.04}, spacing=dp(20))
        restart_btn = StyledButton(text="RESTART", bg_color='#1976D2', bold=True)
        restart_btn.bind(on_release=app.restart_game)
        exit_btn = StyledButton(text="EXIT", bg_color='#F44336', bold=True)
        exit_btn.bind(on_release=self.go_to_start)
        bottom_btns.add_widget(restart_btn)
        bottom_btns.add_widget(exit_btn)
        self.layout.add_widget(bottom_btns)
        self.add_widget(self.layout)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def go_to_start(self, *args):
        self.manager.current = 'start'
        app = App.get_running_app()
        if app.timer_event: 
            Clock.unschedule(app.timer_event)
        if app.bot_timer_event: 
            Clock.unschedule(app.bot_timer_event)


# --- MAIN APP ---
class AtlasApp(App):
    def build(self):
        # Database Sets Full Lists
        self.countries = [#Countries
 "afghanistan", "albania", "algeria","america", "andorra", "angola","antigua & deps", "argentina", "armenia", "australia", "austria","azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados","belarus", "belgium", "belize", "benin", "bhutan","bolivia", "bosnia herzegovina", "botswana", "brazil","brunei","bulgaria", "burkina", "burundi", "cambodia", "cameroon","canada", "cape verde", "central african rep", "chad", "chile","china", "colombia", "comoros", "congo", "cong","costa rica", "croatia", "cuba", "cyprus", "czech republic","denmark", "djibouti", "dominica", "dominican republic", "east timor","ecuador", "egypt", "el salvador", "equatorial guinea", "eritrea","estonia", "ethiopia", "fiji", "finland", "france","gabon", "gambia", "georgia", "germany", "ghana","greece", "grenada", "guatemala", "guinea", "guinea-bissau","guyana", "haiti", "honduras", "hungary", "iceland","india", "indonesia", "iran", "iraq", "ireland","israel", "italy", "ivory coast", "jamaica", "japan","jordan", "kazakhstan", "kenya", "kiribati", "north korea","south korea", "kosovo", "kuwait", "kyrgyzstan", "laos","latvia", "lebanon", "lesotho", "liberia", "libya","liechtenstein", "lithuania", "luxembourg", "macedonia", "madagascar","malawi", "malaysia", "maldives", "mali", "malta","marshall islands", "mauritania", "mauritius", "mexico", "micronesia","moldova", "monaco", "mongolia", "montenegro", "morocco","mozambique", "myanmar", "namibia", "nauru", "nepal","netherlands", "new zealand", "nicaragua", "niger", "nigeria","norway", "oman", "pakistan", "palau", "panama","papua new guinea", "paraguay", "peru", "philippines", "poland","portugal", "qatar", "romania", "russia", "rwanda","st kitts & nevis", "st lucia", "saint vincent & the grenadines","samoa", "san marino", "sao tome & principe", "saudi arabia","senegal", "serbia", "seychelles", "sierra leone", "singapore","slovakia", "slovenia", "solomon islands","somalia", "south africa","south sudan", "spain", "sri lanka", "sudan", "suriname","swaziland", "sweden", "switzerland", "syria", "taiwan","tajikistan", "tanzania", "thailand", "togo", "tonga","trinidad & tobago", "tunisia", "turkey", "turkmenistan", "tuvalu","uganda", "ukraine", "united arab emirates", "united kingdom","united states", "uruguay", "uzbekistan", "vanuatu","vatican city", "venezuela", "vietnam", "yemen","zambia", "zimbabwe"
        ]
        
        self.continents = ["asia", "africa", "north america", "south america", "antarctica", "europe", "australia"]
        
        self.capitals = ["algiers","luanda","porto-novo","gaborone","ouagadougou","gitega","praia","yaounde","bangui","n'djamena","moroni","kinshasa","brazzaville","yamoussoukro","djibouti","cairo","malabo","asmara","mbabane","addis ababa","libreville","banjul","accra","conakry","bissau","nairobi","maseru","monrovia","tripoli","antananarivo","lilongwe","bamako","nouakchott","port louis","rabat","maputo","windhoek","niamey","abuja","kigali","sao tome","dakar","victoria","freetown","mogadishu","pretoria","juba","khartoum","dodoma","lome","tunis","kampala","lusaka","harare","kabul","yerevan","baku","manama","dhaka","thimphu","bandar seri begawan","phnom penh","beijing","nicosia","tbilisi","new delhi","delhi","jakarta","tehran","baghdad","jerusalem","tokyo","amman","astana","kuwait city","bishkek","vientiane","beirut","kuala lumpur","male","naypyidaw","ulaanbaatar","kathmandu","pyongyang","muscat","islamabad","manila","doha","riyadh","singapore","seoul","sri jayawardenepura kotte","damascus","taipei","dushanbe","bangkok","dili","ankara","ashgabat","abu dhabi","tashkent","hanoi","sanaa","tirana","andorra la vella","vienna","minsk","brussels","sarajevo","sofia","zagreb","prague","copenhagen","tallinn","helsinki","paris","berlin","athens","budapest","reykjavik","dublin","rome","pristina","riga","vaduz","vilnius","luxembourg","valletta","chisinau","monaco","podgorica","amsterdam","skopje","oslo","warsaw","lisbon","bucharest","moscow","san marino","belgrade","bratislava","ljubljana","madrid","stockholm","bern","kyiv","london","vatican city","st. john's","nassau","bridgetown","belmopan","ottawa","san jose","havana","roseau","santo domingo","san salvador","st. george's","guatemala city","port-au-prince","tegucigalpa","kingston","mexico city","managua","panama city","basseterre","castries","kingstown","washington , d.c.","canberra","suva","tarawa","majuro","palikir","yaren","wellington","ngerulmud","port moresby","apia","honiara","nuku'alofa","funafuti","port vila","buenos aires","sucre","brasília","santiago","bogota","quito","georgetown","asuncion","lima","paramaribo","montevideo","caracas",
        ]
        
        self.states = [#state 
#india
"andaman and nicobar islands", "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chandigarh", "chhattisgarh", "dadra and nagar haveli", "daman and diu", "delhi", "goa", "gujarat", "haryana", "himachal pradesh", "jammu and kashmir", "jharkhand", "karnataka", "kerala", "ladakh", "lakshadweep", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "puducherry", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
#america
"alabama","alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
#Austrailia
"australian capital territory", "new south wales", "northern territory", "queensland", "south australia",
"tasmania", "victoria", "western australia",
#canada
"alberta","british columbia", "manitoba", "new brunswick", "newfoundland and labrador", "northwest territories", "nova scotia", "nunavut", "ontario", "prince edward island", "quebec", "saskatchewan", "yukon",
#UK
"england", "scotland", "wales", "northern ireland",
#Germany
"baden-wuerttemberg", "bavaria", "berlin", "brandenburg", "bremen", "hamburg", "hesse", "lower saxony", "mecklenburg-western pomerania", "north rhine-westphalia", "rhineland-palatinate", "saarland", "saxony", "saxony-anhalt", "schleswig-holstein", "thuringia",
#Brazil
"acre", "alagoas", "amapa", "amazonas", "bahia", "ceara", "distrito federal", "espirito santo", "goias", "maranhao", "mato grosso", "mato grosso do sul", "minas gerais", "para", "paraiba", "parana", "pernambuco", "piaui", "rio de janeiro", "rio grande do norte", "rio grande do sul", "rondonia", "roraima", "santa catarina", "sao paulo", "sergipe", "tocantins",
#mexico
"aguascalientes", "baja california", "baja california sur", "campeche", "chiapas", "chihuahua", "coahuila", "colima", "ciudad de mexico", "durango", "guanajuato", "guerrero", "hidalgo", "jalisco", "mexico", "michoacan", "morelos", "nayarit", "nuevo leon", "oaxaca", "puebla", "queretaro", "quintana roo", "san luis potosi", "sinaloa", "sonora", "tabasco", "tamaulipas", "tlaxcala", "veracruz", "yucatan", "zacatecas",
#chinese
"anhui", "beijing", "chongqing", "fujian", "gansu", "guangdong", "guangxi", "guizhou", "hainan", "hebei", "heilongjiang", "henan", "hubei", "hunan", "inner mongolia", "jiangsu", "jiangxi", "jilin", "liaoning", "ningxia", "qinghai", "shaanxi", "shandong", "shanghai", "shanxi", "sichuan", "tianjin", "tibet", "xinjiang", "yunnan", "zhejiang",
#Japan
"hokkaido","aomori",
"iwate","miyagi","akita","yamagata","fukushima","ibaraki","tochigi","gunma","saitama","chiba","tokyo","kanagawa","niigata","toyama","ishikawa","fukui","yamanashi","nagano","gifu","shizuoka","aichi","mie","shiga","kyoto","osaka","hyogo","nara","wakayama","tottori","shimane","okayama","hiroshima","yamaguchi","tokushima","kagawa","ehime","kochi","fukuoka","saga","nagasaki","kumamoto","oita","miyazaki","kagoshima","okinawa",
#pakistan
"sindh","khyber pakhtunkhwa","balochistan","islamabad","gilgit-baltistan",
#indonesia
"aceh","north sumatra","west sumatra","riau","jambi","south sumatra","bengkulu","lampung","bangka belitung islands","riau islands","dki jakarta","west java","central java","east java","yogyakarta","banten","bali","west nusa tenggara","east nusa tenggara","west kalimantan","central kalimantan","south kalimantan","east kalimantan","north kalimantan","north sulawesi","central sulawesi","south sulawesi","southeast sulawesi","gorontalo","west sulawesi","maluku","north maluku","west papua","papua","southwest papua","central papua","south papua","papua highlands",
#bangladesh
"dhaka division","chattogram division","rajshahi division","khulna division","barisal division","sylhet division","rangpur division","mymensingh division",
#france
"auvergne-rhone-alpes", "bourgogne-franche-comte", "brittany", "centre-val de loire", "corsica", "grand est", "hauts-de-france", "ile-de-france", "normandy", "nouvelle-aquitaine", "occitanie", "pays de la loire", "provence-alpes-cote d’azur", "guadeloupe", "martinique", "guyane", "la reunion", "mayotte","paris"
#italy
"piedmont", "valle d'aosta", "lombardy", "trentino-alto adige", "veneto", "friuli venezia giulia", "liguria", "emilia-romagna", "tuscany", "umbria", "marche", "lazio", "abruzzo", "molise", "campania", "apulia", "basilicata", "calabria", "sicily", "sardinia",
#Spain
"andalusia", "aragon", "asturias", "balearic islands", "basque country", "canary islands", "cantabria", "castile and leon", "castile-la mancha", "catalonia", "extremadura", "galicia", "la rioja", "madrid", "murcia", "navarre", "valencian community", "ceuta",
#Russia
"moscow", "saint petersburg", "moscow oblast", "leningrad oblast", "krasnodar krai", "stavropol krai", "rostov oblast", "nizhny novgorod oblast", "sverdlovsk oblast", "chelyabinsk oblast", "novosibirsk oblast", "omsk oblast", "tatarstan republic", "bashkortostan republic", "dagestan republic", "chechnya republic", "krasnoyarsk krai", "irkutsk oblast", "primorsky krai", "khabarovsk krai",
#argentina
"buenos aires", "catamarca", "chaco", "chubut", "cordoba", "corrientes", "entre rios", "formosa", "jujuy", "la pampa", "la rioja", "mendoza", "misiones", "neuquen", "rio negro", "salta", "san juan", "san luis", "santa cruz", "santa fe", "santiago del estero", "tierra del fuego", "tucuman",
#columbia
"amazonas", "antioquia", "arauca", "atlantico", "bolivar", "boyaca", "caldas", "caqueta", "casanare", "cauca", "cesar", "choco", "cordoba", "cundinamarca", "guainia", "guaviare", "huila", "la guajira", "magdalena", "meta", "narino", "norte de santander", "putumayo", "quindio", "risaralda", "san andres y providencia", "santander", "sucre", "tolima", "valle del cauca", "vaupes", "vichada",
#peru
"amazonas", "ancash", "apurimac", "arequipa", "ayacucho", "cajamarca", "callao", "cusco", "huancavelica", "huanuco", "ica", "junin", "la libertad", "lambayeque", "lima", "loreto", "madre de dios", "moquegua", "pasco", "piura", "puno", "san martin", "tacna", "tumbes", "ucayali",
#Nigeria
"abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue", "borno", "cross river", "delta", "ebonyi", "edo", "ekiti", "enugu", "gombe", "imo", "jigawa", "kaduna", "kano", "katsina", "kebbi", "kogi", "kwara", "lagos", "nasarawa", "niger", "ogun", "ondo", "osun", "oyo", "plateau", "rivers", "sokoto", "taraba", "yobe", "zamfara", "federal capital territory",
#south africa
"eastern cape", "free state", "gauteng", "kwazulu-natal", "limpopo", "mpumalanga", "north west", "northern cape", "western cape",
#egypt
"cairo", "alexandria", "giza", "qalyubia", "sharqia", "dakahlia", "beheira", "monufia", "gharbia", "kafr el sheikh", "damietta", "port said", "ismailia", "suez", "north sinai", "south sinai", "fayoum", "beni suef", "minya", "asyut", "sohag", "qena", "luxor", "aswan", "red sea", "new valley", "matruh",
#kenya
"nairobi county", "mombasa county", "kajiado county", "kiambu county", "nakuru county", "uasin gishu county", "kisumu county", "machakos county", "meru county", "embu county", "nyeri county", "nyandarua county", "laikipia county", "murang'a county", "kirinyaga county", "kilifi county", "kwale county", "taita taveta county", "tana river county", "lamu county", "garissa county", "wajir county", "mandera county", "marsabit county", "isiolo county", "samburu county", "turkana county", "west pokot county", "baringo county", "elgeyo-marakwet county", "bomet county", "kericho county", "narok county", "bungoma county", "busia county", "vihiga county", "vihiga county", "siaya county", "homa bay county", "migori county", "nyamira county", "kisii county",
#newzealand
"northland", "auckland", "waikato", "bay of plenty", "gisborne", "hawke's bay", "taranaki", "manawatu-whanganui", "wellington", "tasman", "nelson", "marlborough", "west coast", "canterbury", "otago", "southland",
        ]

        # Instantly create and return the Screen Manager so Android can render the UI without lag
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(StartScreen(name='start'))
        self.sm.add_widget(GameScreen(name='game'))
        return self.sm

    def on_start(self):
        # Wait 0.1 seconds for the graphics frame loop to render, then load files and variables safely
        Clock.schedule_once(self.deferred_game_init, 0.1)
        Clock.schedule_once(self.track_only_downloads, 1.5)

    def track_only_downloads(self, dt):
        """Silently registers device types and increments the global counter."""
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            raw_device = f"{Build.MANUFACTURER}_{Build.MODEL}".lower().replace(" ", "_")
        except Exception:
            raw_device = "desktop_pc_tester"

        namespace = "atlas_game_singhakshit_downloads"
        local_marker = "download_registered.marker"
        
        if not os.path.exists(local_marker):
            # 1. Add +1 to the main download counter displayed in the top corner
            UrlRequest(f"https://counterapi.dev{namespace}/total_downloads/up")
            
            # 2. Add +1 to this specific device bucket behind the scenes
            UrlRequest(f"https://counterapi.dev{namespace}/device_{raw_device}/up", 
                       on_success=lambda req, res: self.mark_download_locally(local_marker))
        
        # Fetch the clean total download tally back from the server to update the corner display
        UrlRequest(f"https://counterapi.dev{namespace}/total_downloads", 
                   on_success=self.display_top_downloads)

    def mark_download_locally(self, marker_path):
        """Generates a permanent local marker file so this device only increments your score once."""
        try:
            with open(marker_path, "w") as f:
                f.write("registered")
        except Exception:
            pass

    def display_top_downloads(self, req, result):
        """Parses the online count structural data and binds it to the top right text label."""
        try:
            if isinstance(result, str):
                result = json.loads(result)
                
            total_downloads = result.get('count', 0)
            
            if hasattr(self, 'top_download_lbl') and total_downloads > 0:
                self.top_download_lbl.text = f"Downloads: {total_downloads}"
        except Exception as e:
            print(f"Error rendering top download tracking metrics: {e}")


    def deferred_game_init(self, dt):
        # Move all heavy memory/startup allocations here
        self.game_mode = "country"
        self.active_pool = []
        self.used_countries = []
        self.bot_country = ""
        self.score = 0
        self.best_score = 0
        self.games_played_streak = 0
        self.timer_seconds = 30
        self.timer_event = None
        self.bot_timer_event = None
        self.first_turn = True

        # Loading audio files now runs safely after layout rendering completes
        self.success_sound = SoundLoader.load('success.wav') if os.path.exists('success.wav') else None
        self.fail_sound = SoundLoader.load('fail.wav') if os.path.exists('fail.wav') else None
        self.victory_sound = SoundLoader.load('victory.wav') if os.path.exists('victory.wav') else None
        print("Deferred engine and audio files loaded successfully!")

    def create_stat(self, parent, title, val, color):
        card = StyledCard(orientation='vertical', padding=dp(5))
        card.add_widget(Label(text=title, font_size='10sp', color=(0.4,0.4,0.4,1)))
        v = Label(text=val, font_size='18sp', bold=True, color=get_color_from_hex(color))
        card.add_widget(v)
        parent.add_widget(card)
        return v

    def add_history_item(self, sender, word, status="correct", error_msg=""):
        item = HistoryItem(sender=sender, word=word, status=status, error_msg=error_msg)
        item.opacity = 0
        self.history_layout.add_widget(item)
        Animation(opacity=1, duration=0.2).start(item)
        Clock.schedule_once(lambda dt: setattr(self.history_scroll, 'scroll_y', 0))

    def handle_turn(self, *args):
        val = self.user_input.text.strip().lower()
        if not val or self.user_input.disabled: return
        self.user_input.text = ""

        if val in ["don't know", "don'tknow", "dontknow", "dont know", "skip", "quit"]:
            self.add_history_item("YOU", "Forgot", status="error", error_msg="Gave Up!")
            self.game_over("You gave up!")
            return

        if not self.first_turn and not val.startswith(self.bot_country[-1]):
            err = f"Wrong! Starts with {self.bot_country[-1].upper()}"
            self.instruction.text = err
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val or "?", status="error", error_msg=err)
            self.user_input.disabled = False
            return 
        
        if val not in self.active_pool:
            hint_txt = "Not a valid country!" if self.game_mode == "country" else "Not a valid map item!"
            self.instruction.text = hint_txt
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val, status="error", error_msg="Not recognized")
            self.user_input.disabled = False
            return

        if val in self.used_countries:
            self.instruction.text = "Already used!"
            if self.fail_sound: self.fail_sound.play()
            self.add_history_item("YOU", val, status="warning", error_msg="Already used")
            self.user_input.disabled = False
            return

        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.success_sound: self.success_sound.play()
        
        self.score += 10
        self.score_lbl.text = str(self.score)
        self.used_countries.append(val)
        self.add_history_item("YOU", val, status="correct")
        self.first_turn = False
        self.user_input.disabled = True
        
        self.start_timer()
        self.instruction.text = "Bot thinking..."
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
        self.bot_timer_event = Clock.schedule_once(lambda dt: self.bot_move(val[-1]), random.uniform(1.0, 7))

    def bot_move(self, char):
        if self.timer_event: Clock.unschedule(self.timer_event)
        possible = [c for c in self.active_pool if c.startswith(char) and c not in self.used_countries]
        if not possible:
            if self.victory_sound: self.victory_sound.play()
            self.instruction.text = "YOU WIN! Bot stuck. ✓"
            self.last_letter_lbl.text = "[color=#FFC107]W[/color]"
            self.update_best_score()
            self.user_input.disabled = True
        else:
            if self.success_sound: self.success_sound.play()
            self.bot_country = random.choice(possible)
            self.used_countries.append(self.bot_country.lower())
            self.add_history_item("BOT", self.bot_country, status="correct")
            self.last_letter_lbl.text = self.bot_country[-1].upper()
            self.instruction.text = f"Bot: {self.bot_country.upper()}"
            self.user_input.disabled = False
            self.start_timer()

    def start_timer(self):
        if self.timer_event: Clock.unschedule(self.timer_event)
        self.timer_seconds = 30
        self.timer_lbl.text = "30s"
        self.timer_lbl.font_size = '18sp'
        self.timer_lbl.color = get_color_from_hex("#4CAF50")
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.timer_seconds -= 1
        self.timer_lbl.text = f"{self.timer_seconds}s"
        
        if self.timer_seconds <= 20:
            self.timer_lbl.color = get_color_from_hex("#F44336")
            if self.timer_seconds % 2 == 0:
                anim = Animation(font_size=sp(22), duration=0.15) + Animation(font_size=sp(18), duration=0.15)
                anim.start(self.timer_lbl)

        if self.timer_seconds <= 0:
            if self.timer_event: Clock.unschedule(self.timer_event)
            self.add_history_item("YOU", "TIMEOUT", status="error", error_msg="Out of time!")
            self.game_over("Time Out!")
            self.last_letter_lbl.text = "[color=#FF0000]X[/color]"

    def game_over(self, reason):
        if self.fail_sound: self.fail_sound.play()
        self.user_input.disabled = True
        self.update_best_score()
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)

        target_char = ""
        if self.first_turn:
            target_char = random.choice([c for c in self.active_pool])
        elif self.bot_country:
            target_char = self.bot_country[-1]

        missed_options = [c for c in self.active_pool if c.startswith(target_char) and c not in self.used_countries]
        if missed_options:
            suggestion = random.choice(missed_options).upper()
            self.instruction.text = f"{reason} Missed: {suggestion}"
        else:
            self.instruction.text = f"{reason} No answers left!"

    def update_best_score(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.best_lbl.text = str(self.best_score)

    def restart_game(self, *args):
        if self.timer_event: Clock.unschedule(self.timer_event)
        if self.bot_timer_event: Clock.unschedule(self.bot_timer_event)
        
        if self.game_mode == "country":
            self.active_pool = list(self.countries)
            self.instruction.text = "Enter a country!"
        else:
            self.active_pool = self.countries + self.continents + self.capitals + self.states
            self.instruction.text = "Enter Country, Capital,\n Continent, or State!"

        self.games_played_streak += 1
        self.streak_lbl.text = str(self.games_played_streak)
        self.used_countries = []
        self.score = 0
        self.score_lbl.text = "0"
        self.last_letter_lbl.text = "?"
        self.history_layout.clear_widgets()
        self.user_input.disabled = False
        self.first_turn = True
        self.start_timer()

if __name__ == '__main__':
    AtlasApp().run()
