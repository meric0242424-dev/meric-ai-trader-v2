from datetime import datetime

class BotState:
    def __init__(self):
        self.running=False
        self.open_positions={}
        self.logs=[]
        self.last_scan=None
        self.signals=[]

    def log(self, msg: str, level: str="INFO"):
        e={"time": datetime.now().strftime("%H:%M:%S"), "level": level, "msg": msg}
        self.logs.insert(0,e)
        self.logs=self.logs[:300]
        print(f"[{e['time']}] {level}: {msg}")

state=BotState()
