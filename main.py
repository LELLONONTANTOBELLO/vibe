from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from plyer import vibrator
import requests
from threading import Thread
import time

SERVER_URL = "https://www.crashando.it/vibe/vibra.php"

class VibrationController(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20
        
        self.patterns = {
            'a': [0.4],
            'b': [0.4, 0.2, 0.4],
            'c': [0.4, 0.2, 0.4, 0.2, 0.4],
            'd': [0.4, 0.2, 0.4, 0.2, 0.4, 0.2, 0.4]
        }
        
        self.service_running = False
        self.last_vibrate_id = None
        self.polling_thread = None
        
        header = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=10)
        title = Label(text='Vibration Controller', font_size='24sp', bold=True, color=(1, 1, 1, 1))
        self.status_label = Label(text='Pronto', font_size='14sp', color=(1, 1, 1, 0.9), size_hint_y=0.4)
        header.add_widget(title)
        header.add_widget(self.status_label)
        
        send_section = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=10)
        send_title = Label(text='INVIA VIBRAZIONE A TUTTI', font_size='14sp', bold=True, color=(1, 1, 1, 0.9), size_hint_y=0.2)
        send_grid = GridLayout(cols=2, spacing=12, size_hint_y=0.8)
        
        for option, (num, desc) in [('a', ('A', '1 vib')), ('b', ('B', '2 vib')), ('c', ('C', '3 vib')), ('d', ('D', '4 vib'))]:
            btn = Button(text=f'{num}\n{desc}', background_color=(1, 1, 1, 1), color=get_color_from_hex('#667eea'), font_size='16sp', bold=True)
            btn.bind(on_press=lambda x, opt=option: self.send_vibrate(opt))
            send_grid.add_widget(btn)
        
        send_section.add_widget(send_title)
        send_section.add_widget(send_grid)
        
        receive_section = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=10)
        receive_title = Label(text='RICEZIONE VIBRAZIONI', font_size='14sp', bold=True, color=(1, 1, 1, 0.9), size_hint_y=0.2)
        control_layout = BoxLayout(orientation='vertical', spacing=12, size_hint_y=0.8)
        
        self.start_btn = Button(text='AVVIA SERVIZIO', background_color=get_color_from_hex('#51cf66'), color=(1, 1, 1, 1), font_size='16sp', bold=True)
        self.start_btn.bind(on_press=self.start_service)
        
        self.stop_btn = Button(text='FERMA SERVIZIO', background_color=get_color_from_hex('#ff6b6b'), color=(1, 1, 1, 1), font_size='16sp', bold=True, opacity=0, disabled=True)
        self.stop_btn.bind(on_press=self.stop_service)
        
        control_layout.add_widget(self.start_btn)
        control_layout.add_widget(self.stop_btn)
        receive_section.add_widget(receive_title)
        receive_section.add_widget(control_layout)
        
        self.add_widget(header)
        self.add_widget(send_section)
        self.add_widget(receive_section)
    
    def update_status(self, text, active=False):
        self.status_label.text = text
        self.status_label.color = get_color_from_hex('#51cf66') if active else (1, 1, 1, 0.9)
    
    def send_vibrate(self, option):
        def send():
            try:
                response = requests.post(SERVER_URL, data={'vibrate': option}, timeout=5)
                if response.status_code == 200:
                    Clock.schedule_once(lambda dt: self.update_status(f'OK {option.upper()} inviato!'), 0)
                    Clock.schedule_once(lambda dt: self.update_status('Servizio attivo' if self.service_running else 'Pronto', self.service_running), 2)
                else:
                    Clock.schedule_once(lambda dt: self.update_status('Errore invio'), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f'Errore: {str(e)}'), 0)
        Thread(target=send, daemon=True).start()
    
    def start_service(self, instance):
        if self.service_running:
            return
        self.service_running = True
        self.start_btn.opacity = 0
        self.start_btn.disabled = True
        self.stop_btn.opacity = 1
        self.stop_btn.disabled = False
        self.update_status('Servizio attivo', True)
        try:
            vibrator.vibrate(0.1)
        except:
            pass
        self.polling_thread = Thread(target=self.polling_loop, daemon=True)
        self.polling_thread.start()
    
    def stop_service(self, instance):
        self.service_running = False
        self.stop_btn.opacity = 0
        self.stop_btn.disabled = True
        self.start_btn.opacity = 1
        self.start_btn.disabled = False
        self.update_status('Servizio fermato')
    
    def polling_loop(self):
        while self.service_running:
            try:
                response = requests.get(f'{SERVER_URL}?poll&t={int(time.time() * 1000)}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('pattern') and data.get('id') != self.last_vibrate_id:
                        self.last_vibrate_id = data['id']
                        pattern = data['pattern']
                        self.execute_vibration(pattern)
                        Clock.schedule_once(lambda dt: self.update_status(f'{pattern.upper()} ricevuto!', True), 0)
                        Clock.schedule_once(lambda dt: self.update_status('Servizio attivo', True), 2)
            except Exception as e:
                print(f'Errore polling: {e}')
            time.sleep(0.15)
    
    def execute_vibration(self, pattern_key):
        pattern = self.patterns.get(pattern_key)
        if not pattern:
            return
        try:
            for i, duration in enumerate(pattern):
                if i > 0:
                    time.sleep(0.2)
                vibrator.vibrate(duration)
        except Exception as e:
            print(f'Errore vibrazione: {e}')

class VibrationApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = get_color_from_hex('#667eea')
        return VibrationController()

if __name__ == '__main__':
    VibrationApp().run()