from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QInputDialog, QMessageBox
)
from core.ai_engine import AIEngine
from core.system_info import snapshot
from database.database import Database
from ui.orb import IntelligenceOrb

STYLE = """
QMainWindow,QWidget{background:#080B14;color:#EAF4FF;font-family:'Inter','Arial';}
QFrame#Sidebar{background:#0D1423;border:1px solid #18243A;border-radius:18px;}
QFrame#Panel{background:#101A2B;border:1px solid #1B2A43;border-radius:18px;}
QLabel#Brand{color:#65E9FF;font-size:23px;font-weight:800;letter-spacing:3px;}
QLabel#Eyebrow{color:#7D91AD;font-size:10px;font-weight:700;letter-spacing:2px;}
QLabel#Heading{color:#F3F8FF;font-size:22px;font-weight:700;}
QLabel#Muted{color:#8293AA;}
QPushButton{background:#17253A;color:#DDEBFA;border:1px solid #263B58;border-radius:10px;padding:11px 14px;text-align:left;}
QPushButton:hover{background:#203650;border:1px solid #00CFE8;}
QPushButton#Primary{background:#00CFE8;color:#06111D;border:0;font-weight:800;text-align:center;}
QLineEdit,QTextEdit,QListWidget{background:#0A1220;color:#EAF4FF;border:1px solid #263B58;border-radius:10px;padding:10px;selection-background-color:#155A75;}
"""

class AIWorker(QThread):
    done = Signal(str)
    def __init__(self, engine, prompt, history, memories):
        super().__init__()
        self.engine, self.prompt, self.history, self.memories = engine, prompt, history, memories
    def run(self):
        self.done.emit(self.engine.respond(self.prompt, self.history, self.memories))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.ai = AIEngine()
        self.worker = None
        self.setWindowTitle("PROMETHEUS — Personal Intelligence System")
        self.resize(1380, 860)
        self.setMinimumSize(1050, 680)
        self.setStyleSheet(STYLE)
        self.build()
        self.refresh_dashboard()

    def panel(self):
        f = QFrame(); f.setObjectName("Panel"); return f

    def build(self):
        root = QWidget(); self.setCentralWidget(root)
        outer = QHBoxLayout(root); outer.setContentsMargins(22,20,22,20); outer.setSpacing(18)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(225)
        s = QVBoxLayout(sidebar); s.setContentsMargins(16,22,16,18)
        brand = QLabel("PROMETHEUS"); brand.setObjectName("Brand"); s.addWidget(brand)
        sub = QLabel("PERSONAL INTELLIGENCE"); sub.setObjectName("Eyebrow"); s.addWidget(sub)
        s.addSpacing(28)
        for text, idx in [("◈  Overview",0),("◈  AI Command",1),("◈  Mission Control",2),
                          ("◈  Echo Memory",3),("◈  System Monitor",4),("◈  Settings",5)]:
            b = QPushButton(text); b.clicked.connect(lambda checked=False, n=idx:self.go(n)); s.addWidget(b)
        s.addStretch()
        s.addWidget(QLabel("●  SYSTEM READY", styleSheet="color:#4CE6A3;font-weight:800;"))
        s.addWidget(QLabel("LOCAL-FIRST  •  SECURE  •  MODULAR"))
        right = QVBoxLayout()
        header = QHBoxLayout(); titles = QVBoxLayout()
        self.heading = QLabel("OVERVIEW"); self.heading.setObjectName("Heading")
        self.subtitle = QLabel("Your personal intelligence command center."); self.subtitle.setObjectName("Muted")
        titles.addWidget(self.heading); titles.addWidget(self.subtitle); header.addLayout(titles); header.addStretch()
        right.addLayout(header)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.overview()); self.pages.addWidget(self.chat_page())
        self.pages.addWidget(self.mission_page()); self.pages.addWidget(self.memory_page())
        self.pages.addWidget(self.system_page()); self.pages.addWidget(self.settings_page())
        right.addWidget(self.pages,1)
        outer.addWidget(sidebar); outer.addLayout(right,1)

    def metric(self, label, value):
        f=self.panel(); l=QVBoxLayout(f)
        a=QLabel(label); a.setObjectName("Eyebrow")
        b=QLabel(value); b.setStyleSheet("font-size:24px;font-weight:800;color:#62E9FF;")
        l.addWidget(a); l.addWidget(b); f.value=b
        return f

    def overview(self):
        page=QWidget(); v=QVBoxLayout(page); v.setSpacing(16)
        hero=self.panel(); h=QHBoxLayout(hero); col=QVBoxLayout()
        eyebrow=QLabel("YOUR AI  •  YOUR WORKSPACE  •  YOUR CONTROL"); eyebrow.setObjectName("Eyebrow")
        title=QLabel("Think bigger.\\nMove with clarity."); title.setStyleSheet("font-size:34px;font-weight:800;")
        desc=QLabel("A focused command center for ideas, projects and daily work."); desc.setObjectName("Muted")
        launch=QPushButton("OPEN AI COMMAND  →"); launch.setObjectName("Primary"); launch.clicked.connect(lambda:self.go(1))
        col.addWidget(eyebrow); col.addWidget(title); col.addWidget(desc); col.addStretch(); col.addWidget(launch,0,Qt.AlignmentFlag.AlignLeft)
        h.addLayout(col,1); self.orb=IntelligenceOrb(); h.addWidget(self.orb)
        v.addWidget(hero,2)
        cards=QHBoxLayout()
        self.mission_metric=self.metric("ACTIVE MISSIONS","0")
        self.memory_metric=self.metric("SAVED MEMORIES","0")
        self.ai_metric=self.metric("AI ENGINE","CHECKING")
        cards.addWidget(self.mission_metric); cards.addWidget(self.memory_metric); cards.addWidget(self.ai_metric)
        v.addLayout(cards)
        quick=self.panel(); q=QVBoxLayout(quick); label=QLabel("QUICK LAUNCH"); label.setObjectName("Eyebrow"); q.addWidget(label)
        row=QHBoxLayout()
        for text,idx in [("AI Command",1),("Mission Control",2),("Echo Memory",3),("System Monitor",4)]:
            b=QPushButton(text); b.clicked.connect(lambda checked=False,n=idx:self.go(n)); row.addWidget(b)
        q.addLayout(row); v.addWidget(quick)
        return page

    def chat_page(self):
        page=QWidget(); v=QVBoxLayout(page)
        self.chat=QTextEdit(); self.chat.setReadOnly(True)
        self.chat.append("<b style='color:#65E9FF'>PROMETHEUS</b><br>Intelligence systems initialized. What would you like to work on?")
        v.addWidget(self.chat,1)
        row=QHBoxLayout(); self.input=QLineEdit(); self.input.setPlaceholderText("Message PROMETHEUS…")
        self.input.returnPressed.connect(self.send)
        send=QPushButton("SEND  ➤"); send.setObjectName("Primary"); send.clicked.connect(self.send)
        row.addWidget(self.input,1); row.addWidget(send); v.addLayout(row)
        note=QLabel("AI chat requires your own API key. Local missions and memory work without it."); note.setObjectName("Muted"); v.addWidget(note)
        return page

    def mission_page(self):
        page=QWidget(); v=QVBoxLayout(page); self.missions=QListWidget(); v.addWidget(self.missions,1)
        row=QHBoxLayout()
        for text,fn,primary in [("+ NEW MISSION",self.add_mission,True),("TOGGLE COMPLETE",self.toggle_mission,False),("DELETE",self.delete_mission,False)]:
            b=QPushButton(text); b.clicked.connect(fn)
            if primary:b.setObjectName("Primary")
            row.addWidget(b)
        v.addLayout(row); return page

    def memory_page(self):
        page=QWidget(); v=QVBoxLayout(page); self.memories=QListWidget(); v.addWidget(self.memories,1)
        row=QHBoxLayout()
        a=QPushButton("+ SAVE MEMORY"); a.setObjectName("Primary"); a.clicked.connect(self.add_memory)
        d=QPushButton("DELETE SELECTED"); d.clicked.connect(self.delete_memory)
        row.addWidget(a); row.addWidget(d); v.addLayout(row); return page

    def system_page(self):
        page=QWidget(); v=QVBoxLayout(page); self.sys_labels={}
        for key in ("os","cpu","ram","storage"):
            f=self.panel(); box=QVBoxLayout(f); name=QLabel(key.upper()); name.setObjectName("Eyebrow")
            val=QLabel("Loading…"); val.setStyleSheet("font-size:20px;font-weight:700;color:#65E9FF;")
            box.addWidget(name); box.addWidget(val); self.sys_labels[key]=val; v.addWidget(f)
        b=QPushButton("REFRESH SYSTEM STATUS"); b.clicked.connect(self.refresh_system); v.addWidget(b); v.addStretch()
        return page

    def settings_page(self):
        page=QWidget(); v=QVBoxLayout(page)
        title=QLabel("CONFIGURATION"); title.setObjectName("Heading"); v.addWidget(title)
        for text in ["AI provider: OpenAI API","Model: "+self.ai.model,
                     "Database: local SQLite (prometheus.db)",
                     "API key: loaded from OPENAI_API_KEY in .env",
                     "Security: arbitrary AI-generated terminal commands are not executed."]:
            lab=QLabel(text); lab.setWordWrap(True); lab.setObjectName("Muted"); v.addWidget(lab)
        v.addStretch(); return page

    def go(self, idx):
        names=["OVERVIEW","AI COMMAND","MISSION CONTROL","ECHO MEMORY","SYSTEM MONITOR","SETTINGS"]
        subs=["Your personal intelligence command center.","Talk through ideas, questions and projects.",
              "Capture priorities and track progress.","A private local store for information you choose to save.",
              "A live snapshot of this Zorin OS machine.","Manage local application configuration."]
        self.pages.setCurrentIndex(idx); self.heading.setText(names[idx]); self.subtitle.setText(subs[idx])
        if idx==2:self.refresh_missions()
        if idx==3:self.refresh_memories()
        if idx==4:self.refresh_system()

    def send(self):
        prompt=self.input.text().strip()
        if not prompt:return
        self.input.clear(); self.chat.append(f"<br><b style='color:#B18AFF'>YOU</b><br>{self.esc(prompt)}")
        self.input.setEnabled(False)
        self.worker=AIWorker(self.ai,prompt,self.db.history(),self.db.memory_context())
        self.worker.done.connect(lambda answer:self.finish(prompt,answer)); self.worker.start()

    def finish(self,prompt,answer):
        self.db.save_message("user",prompt); self.db.save_message("assistant",answer)
        self.chat.append(f"<br><b style='color:#65E9FF'>PROMETHEUS</b><br>{self.esc(answer)}")
        self.input.setEnabled(True); self.input.setFocus()

    def esc(self,t):
        return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\\n","<br>")

    def add_mission(self):
        text,ok=QInputDialog.getText(self,"New mission","Mission title:")
        if ok and text.strip():self.db.add_mission(text.strip());self.refresh_missions();self.refresh_dashboard()

    def refresh_missions(self):
        self.missions.clear()
        for x in self.db.missions():
            item=QListWidgetItem(("✓" if x["completed"] else "○")+f"  {x['title']}  •  {x['priority']}")
            item.setData(Qt.ItemDataRole.UserRole,x["id"]);self.missions.addItem(item)

    def add_memory(self):
        text,ok=QInputDialog.getMultiLineText(self,"Save memory","Information to remember:")
        if ok and text.strip():self.db.add_memory(text.strip());self.refresh_memories();self.refresh_dashboard()

    def refresh_memories(self):
        self.memories.clear()
        for x in self.db.memories():
            item=QListWidgetItem(x["content"]+"  •  "+x["created_at"])
            item.setData(Qt.ItemDataRole.UserRole,x["id"]);self.memories.addItem(item)

    def selected_id(self,widget):
        item=widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def toggle_mission(self):
        mid=self.selected_id(self.missions)
        if mid is None:return
        row=next((x for x in self.db.missions() if x["id"]==mid),None)
        if row:self.db.toggle_mission(mid,not row["completed"]);self.refresh_missions();self.refresh_dashboard()

    def delete_mission(self):
        mid=self.selected_id(self.missions)
        if mid is not None:self.db.delete_mission(mid);self.refresh_missions();self.refresh_dashboard()

    def delete_memory(self):
        mid=self.selected_id(self.memories)
        if mid is not None:self.db.delete_memory(mid);self.refresh_memories();self.refresh_dashboard()

    def refresh_dashboard(self):
        self.mission_metric.value.setText(str(sum(not x["completed"] for x in self.db.missions())))
        self.memory_metric.value.setText(str(len(self.db.memories())))
        self.ai_metric.value.setText("CONNECTED" if self.ai.available() else "NOT CONFIGURED")
        self.ai_metric.value.setStyleSheet("font-size:20px;font-weight:800;color:"+("#4CE6A3;" if self.ai.available() else "#FFBD69;"))

    def refresh_system(self):
        try:
            for k,v in snapshot().items():self.sys_labels[k].setText(v)
        except Exception as exc:QMessageBox.warning(self,"System monitor",str(exc))

    def closeEvent(self,event):
        self.db.close()
        event.accept()
