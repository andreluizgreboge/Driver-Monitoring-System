from ultralytics import YOLO
import cv2
import time
import sqlite3
import datetime
import os
import threading
import sys

# =============================
# CONFIGURAÇÕES DE CAMINHO E DB
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
CAPTURE_DIR = os.path.join(BASE_DIR, "static", "captures")
os.makedirs(CAPTURE_DIR, exist_ok=True)

# =============================
# CLASSE DE STREAM DE VÍDEO
# =============================
class VideoStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.ret, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        t = threading.Thread(target=self.update, args=(), daemon=True)
        t.start()
        return self

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                self.stopped = True

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        time.sleep(0.5)
        self.cap.release()

# =============================
# PROCESSO PRINCIPAL
# =============================
try:
    model = YOLO("yolov8n.pt") 
    vs = VideoStream(src=0).start()
    time.sleep(1.0)

    TRUCK_ID = "TRUCK_01"
    CONF_THRESHOLD = 0.4
    last_event_time = 0

    print("\n" + "="*45)
    print("🚀 Driver Monitoring System AI - MONITORAMENTO ATIVO")
    print("   Terminal limpo. Avisarei apenas ao capturar.")
    print("="*45 + "\n")

    while True:
        frame = vs.read()
        if frame is None: continue

        display_frame = frame.copy()
        
        # Inferência ultra veloz
        results = model(frame, imgsz=224, verbose=False, conf=CONF_THRESHOLD)
        
        risk_detected = False
        label_found = ""

        for r in results:
            if not r.boxes: continue
            for box in r.boxes:
                cls = int(box.cls[0])
                name = model.names[cls]
                
                if name in ["cell phone", "bottle"]:
                    risk_detected = True
                    label_found = name
                    
                    # Desenha o retângulo no preview (sem printar no terminal ainda)
                    b = box.xyxy[0].cpu().numpy()
                    cv2.rectangle(display_frame, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), (0, 0, 255), 2)

        # Registro de Evento (Apenas se passar o tempo de respiro)
        curr_time = time.time()
        if risk_detected and (curr_time - last_event_time > 15):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{TRUCK_ID}_{timestamp}.jpg"
            
            # Print imediato da ação de captura
            color_code = "\033[94m" # Azul para captura
            print(f"{color_code}[INFO] Risco '{label_found}' detectado. Capturando evidência... \033[0m")
            
            # Salvamento da imagem
            cv2.imwrite(os.path.join(CAPTURE_DIR, filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            
            def save_to_db(tid, ts, lbl, fname):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO events (truck_id, timestamp, event_type, status, image_path) VALUES (?, ?, ?, ?, ?)",
                                (tid, ts.replace("_", " "), f"Detected: {lbl}", "PENDING", fname))
                    conn.commit()
                    conn.close()
                    print(f"✔️ Evento registrado e enviado para auditoria IA.")
                except Exception as e:
                    print(f"❌ Erro ao salvar no banco: {e}")

            # Thread para não travar o vídeo durante a escrita no banco
            threading.Thread(target=save_to_db, args=(TRUCK_ID, timestamp, label_found, filename), daemon=True).start()
            last_event_time = curr_time

        cv2.imshow("Driver Monitoring System AI - Preview", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\n⚠️ Interrupção via teclado (Ctrl+C).")

finally:
    print("🛑 Encerrando sistema...")
    vs.stop()
    cv2.destroyAllWindows()
    print("✅ Recursos liberados.")
    sys.exit(0)