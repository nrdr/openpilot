import asyncio
import time
import threading
import json
from openpilot.common.swaglog import cloudlog
import cereal.messaging as messaging

class StreamDiagnostic:
    def __init__(self):
        self.sockets = {
            "driver": "livestreamDriverEncodeData",
            "road": "livestreamRoadEncodeData", 
            "wideRoad": "livestreamWideRoadEncodeData"
        }
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia el diagnóstico automático"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._diagnostic_loop, daemon=True)
        self.thread.start()
        cloudlog.info("Stream diagnostic service started")
        
    def stop(self):
        """Detiene el diagnóstico"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        cloudlog.info("Stream diagnostic service stopped")
        
    def _diagnostic_loop(self):
        """Loop principal de diagnóstico"""
        last_report = 0
        message_counts = {socket: 0 for socket in self.sockets}
        last_counts = {socket: 0 for socket in self.sockets}
        
        # Crear sockets
        sock_objects = {}
        for cam, socket_name in self.sockets.items():
            try:
                sock_objects[cam] = messaging.sub_sock(socket_name, conflate=True)
                cloudlog.info(f"Diagnostic socket created for {cam}: {socket_name}")
            except Exception as e:
                cloudlog.error(f"Failed to create diagnostic socket for {cam}: {e}")
        
        while self.running:
            try:
                # Verificar cada socket
                for cam, sock in sock_objects.items():
                    try:
                        msg = messaging.recv_one_or_none(sock)
                        if msg is not None:
                            message_counts[cam] += 1
                            
                            # Analizar el mensaje
                            evta = getattr(msg, msg.which())
                            header_size = len(evta.header) if hasattr(evta, 'header') else 0
                            data_size = len(evta.data) if hasattr(evta, 'data') else 0
                            
                            # Log cada 10 mensajes para evitar spam
                            if message_counts[cam] % 10 == 1:
                                cloudlog.info(f"{cam}: msg #{message_counts[cam]} - header: {header_size}B, data: {data_size}B")
                                
                                if header_size == 0 and data_size == 0:
                                    cloudlog.warning(f"{cam}: Empty packet detected!")
                    except Exception as e:
                        cloudlog.error(f"Error reading from {cam} socket: {e}")
                
                # Reporte cada 10 segundos
                current_time = time.time()
                if current_time - last_report >= 10.0:
                    for cam in self.sockets:
                        rate = (message_counts[cam] - last_counts[cam]) / 10.0
                        cloudlog.info(f"{cam} camera: {rate:.1f} msgs/sec (total: {message_counts[cam]})")
                        last_counts[cam] = message_counts[cam]
                        
                        if rate == 0:
                            cloudlog.warning(f"{cam} camera: NO DATA in last 10 seconds!")
                    
                    last_report = current_time
                
                time.sleep(0.1)  # 100ms entre checks
                
            except Exception as e:
                cloudlog.exception(f"Diagnostic loop error: {e}")
                time.sleep(1.0)
        
        # Cerrar sockets
        for cam, sock in sock_objects.items():
            try:
                sock.close()
            except:
                pass
        
        cloudlog.info("Diagnostic loop finished")

# Instancia global
stream_diagnostic = StreamDiagnostic()
