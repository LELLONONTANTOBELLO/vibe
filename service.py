import time
import requests
from jnius import autoclass, cast
from plyer import vibrator

# Android imports
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
PowerManager = autoclass('android.os.PowerManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationManager = autoclass('android.app.NotificationManager')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')
Notification = autoclass('android.app.Notification')
NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
Color = autoclass('android.graphics.Color')

SERVER_URL = "https://www.crashando.it/vibe/vibra.php"
CHANNEL_ID = "vibration_service_channel"

class VibrationService:
    def __init__(self):
        self.service = None
        self.wake_lock = None
        self.running = False
        self.last_vibrate_id = None
        
        self.patterns = {
            'a': [0.4],
            'b': [0.4, 0.2, 0.4],
            'c': [0.4, 0.2, 0.4, 0.2, 0.4],
            'd': [0.4, 0.2, 0.4, 0.2, 0.4, 0.2, 0.4]
        }
    
    def start(self):
        """Avvia il servizio"""
        print("Starting Vibration Service...")
        self.service = cast('android.app.Service', PythonService.mService)
        
        # Crea notifica persistente (obbligatoria per servizi foreground)
        self.create_notification()
        
        # Acquisisci wakelock per tenere il dispositivo sveglio
        self.acquire_wake_lock()
        
        # Avvia il servizio come foreground service
        self.start_foreground()
        
        # Avvia il polling loop
        self.running = True
        self.polling_loop()
    
    def create_notification(self):
        """Crea il canale di notifica e la notifica"""
        try:
            notification_service = cast(
                NotificationManager,
                self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            )
            
            # Crea canale notifica (necessario per Android 8+)
            channel = NotificationChannel(
                CHANNEL_ID,
                "Vibration Service",
                NotificationManager.IMPORTANCE_LOW
            )
            channel.setDescription("Servizio di ricezione vibrazioni attivo")
            channel.enableLights(True)
            channel.setLightColor(Color.GREEN)
            notification_service.createNotificationChannel(channel)
            
        except Exception as e:
            print(f"Errore creazione canale: {e}")
    
    def start_foreground(self):
        """Avvia il servizio in modalità foreground"""
        try:
            # Crea intent per riaprire l'app quando si tocca la notifica
            app_class = self.service.getApplication().getClass()
            intent = Intent(self.service, app_class)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)
            
            pending_intent = PendingIntent.getActivity(
                self.service, 
                0, 
                intent, 
                PendingIntent.FLAG_IMMUTABLE
            )
            
            # Crea la notifica
            builder = NotificationCompat.Builder(self.service, CHANNEL_ID)
            builder.setContentTitle("Vibration Controller")
            builder.setContentText("Servizio in ascolto - Tocca per aprire")
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setOngoing(True)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setContentIntent(pending_intent)
            builder.setAutoCancel(False)
            
            notification = builder.build()
            
            # Avvia come foreground service (ID 1)
            self.service.startForeground(1, notification)
            print("Foreground service started")
            
        except Exception as e:
            print(f"Errore start foreground: {e}")
    
    def acquire_wake_lock(self):
        """Acquisisce un wakelock parziale per continuare in background"""
        try:
            power_manager = cast(
                PowerManager,
                self.service.getSystemService(Context.POWER_SERVICE)
            )
            
            self.wake_lock = power_manager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "VibrationController::WakeLock"
            )
            
            self.wake_lock.acquire()
            print("Wake lock acquired")
            
        except Exception as e:
            print(f"Errore wake lock: {e}")
    
    def polling_loop(self):
        """Loop principale del servizio"""
        print("Polling loop started")
        
        while self.running:
            try:
                response = requests.get(
                    f'{SERVER_URL}?poll&t={int(time.time() * 1000)}',
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('pattern') and data.get('id') != self.last_vibrate_id:
                        self.last_vibrate_id = data['id']
                        pattern = data['pattern']
                        
                        print(f"Ricevuto pattern: {pattern}")
                        self.execute_vibration(pattern)
                        self.update_notification(f"Ricevuto: {pattern.upper()}")
                        
            except Exception as e:
                print(f'Errore polling: {e}')
            
            time.sleep(0.15)
        
        # Cleanup
        self.stop()
    
    def execute_vibration(self, pattern_key):
        """Esegue il pattern di vibrazione"""
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
    
    def update_notification(self, text):
        """Aggiorna il testo della notifica"""
        try:
            builder = NotificationCompat.Builder(self.service, CHANNEL_ID)
            builder.setContentTitle("Vibration Controller")
            builder.setContentText(text)
            builder.setSmallIcon(self.service.getApplicationInfo().icon)
            builder.setOngoing(True)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            
            notification = builder.build()
            
            notification_service = cast(
                NotificationManager,
                self.service.getSystemService(Context.NOTIFICATION_SERVICE)
            )
            notification_service.notify(1, notification)
            
            # Ripristina il testo dopo 2 secondi
            time.sleep(2)
            builder.setContentText("Servizio in ascolto - Tocca per aprire")
            notification = builder.build()
            notification_service.notify(1, notification)
            
        except Exception as e:
            print(f"Errore aggiornamento notifica: {e}")
    
    def stop(self):
        """Ferma il servizio"""
        print("Stopping service...")
        self.running = False
        
        # Rilascia wake lock
        if self.wake_lock and self.wake_lock.isHeld():
            self.wake_lock.release()
            print("Wake lock released")
        
        # Ferma foreground service
        if self.service:
            self.service.stopForeground(True)
            self.service.stopSelf()
            print("Service stopped")

# Entry point per il servizio
if __name__ == '__main__':
    service = VibrationService()
    service.start()