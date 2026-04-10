# scenes/intro_scene.py — menu principal premium v4
import pygame, math, random
from settings import SCREEN_W, SCREEN_H, PALETTE_SERTAO as P, BLACK, GOLD
from art.fx import Particle

def _draw_pedra_castelo_large(surf, cx, cy):
    rock_mid  = P["rock_mid"]; rock_dark = P["rock_dark"]; rock_light= P["rock_light"]
    pygame.draw.ellipse(surf, (60,40,20), (cx-80,cy+85,160,20))
    pygame.draw.rect(surf, rock_dark,  (cx-22,cy-80,44,170))
    pygame.draw.rect(surf, rock_mid,   (cx-20,cy-80,40,170))
    pygame.draw.rect(surf, rock_light, (cx+8, cy-75,8, 160))
    for i in range(-20,21,10):
        pygame.draw.rect(surf, rock_dark, (cx+i-4,cy-95,8,18))
    pygame.draw.rect(surf, rock_mid, (cx-20,cy-82,40,10))
    pygame.draw.rect(surf, rock_dark,  (cx-62,cy-40,34,130))
    pygame.draw.rect(surf, rock_mid,   (cx-60,cy-40,30,130))
    pygame.draw.rect(surf, rock_light, (cx-34,cy-35,6, 120))
    for i in range(-60,-25,10):
        pygame.draw.rect(surf, rock_dark, (cx+i,cy-55,8,18))
    pygame.draw.rect(surf, rock_dark,  (cx+28,cy-20,30,110))
    pygame.draw.rect(surf, rock_mid,   (cx+30,cy-20,26,110))
    for i in range(28,60,10):
        pygame.draw.rect(surf, rock_dark, (cx+i,cy-35,8,18))
    for rect in [(cx-10,cy-60,8,12),(cx-8,cy-30,6,10),(cx-52,cy-20,6,10),(cx+36,cy,5,8)]:
        pygame.draw.rect(surf, (10,5,20), rect)
    base_pts = [(cx-80,cy+90),(cx-70,cy+80),(cx-60,cy+88),(cx-40,cy+82),
                (cx-22,cy+88),(cx,cy+90),(cx+22,cy+86),(cx+45,cy+88),
                (cx+58,cy+82),(cx+75,cy+90),(cx+80,cy+110),(cx-80,cy+110)]
    pygame.draw.polygon(surf, rock_dark, base_pts)
    pygame.draw.line(surf, rock_dark, (cx-5,cy-78),(cx-3,cy-20),1)
    pygame.draw.line(surf, rock_dark, (cx+8,cy-50),(cx+10,cy+40),1)

MENU_ITEMS = ["Iniciar Jogo", "Controles", "Opções", "Sair"]
CONTROLS = [("MOVER","A / ← →"),("PULAR","W / Espaço"),("ATACAR","Z ou J"),
            ("INTERAGIR","X ou K"),("PAUSAR","ESC"),("CONFIRMAR","ENTER")]

class IntroScene:
    def __init__(self, scene_manager, bus, karma, input_manager):
        self.scene_manager = scene_manager
        self.bus = bus; self.karma = karma; self.input = input_manager
        self.time = 0; self.particles = []; self._initialized = False
        self._star_rng = random.Random(7); self._stars = []
        self._sel = 0; self._screen = "main"   # main|controls|options
        self._sel_cd = 0
        self._fonts = {}

    def _f(self, size, bold=False):
        k = (size, bold)
        if k not in self._fonts:
            try: self._fonts[k] = pygame.font.SysFont("Courier New", size, bold=bold)
            except: self._fonts[k] = pygame.font.Font(None, size+4)
        return self._fonts[k]

    def on_enter(self): self._initialized = False
    def on_exit(self): pass
    def on_resume(self): pass

    def _init(self):
        if self._initialized: return
        self._initialized = True
        for _ in range(80):
            self._stars.append((
                self._star_rng.randint(0, SCREEN_W-1),
                self._star_rng.randint(0, SCREEN_H//3),
                self._star_rng.choice([1,1,1,2])
            ))

    def handle_event(self, event):
        self._init()
        if event.type != pygame.KEYDOWN: return
        k = event.key

        if self._screen != "main":
            if k in (pygame.K_ESCAPE, pygame.K_x, pygame.K_k):
                self._screen = "main"
            return

        if k in (pygame.K_UP, pygame.K_w):
            self._sel = (self._sel-1) % len(MENU_ITEMS)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self._sel = (self._sel+1) % len(MENU_ITEMS)
        elif k in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_x, pygame.K_k, pygame.K_z):
            self._activate(self._sel)

    def _activate(self, idx):
        if idx == 0: self._start_game()
        elif idx == 1: self._screen = "controls"
        elif idx == 2: self._screen = "options"
        elif idx == 3: pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _start_game(self):
        from scenes.village_scene import VillageScene
        self.scene_manager.replace(VillageScene(self.scene_manager, self.bus, self.karma, self.input))

    def update(self):
        self._init()
        self.time += 1
        if self.time % 8 == 0:
            x = random.randint(0, SCREEN_W)
            self.particles.append(Particle(x, SCREEN_H, (160,120,80),
                random.uniform(-0.3,0.3), random.uniform(-0.8,-0.3),
                life=random.randint(60,120), size=1))
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles: p.update()

    def draw(self, surf):
        self._init()
        # Céu gradiente
        for y in range(SCREEN_H):
            t = y/SCREEN_H
            if t < 0.3:
                t2=t/0.3; r=int(80+t2*100); g=int(30+t2*20); b=int(100-t2*50)
            elif t < 0.7:
                t2=(t-0.3)/0.4; r=int(180+t2*75); g=int(50+t2*90); b=int(50)
            else:
                r=255; g=int(140+(t-0.7)/0.3*60); b=int(60+(t-0.7)/0.3*20)
            pygame.draw.line(surf,(r,g,b),(0,y),(SCREEN_W,y))

        for sx,sy,sz in self._stars:
            if sz==1: surf.set_at((sx,sy),(220,220,200))
            else: pygame.draw.rect(surf,(240,240,220),(sx,sy,2,2))

        mx,my=60,45
        pygame.draw.circle(surf,(240,235,200),(mx,my),18)
        pygame.draw.circle(surf,(200,190,140),(mx+6,my-4),12)

        _draw_pedra_castelo_large(surf, SCREEN_W//2, SCREEN_H//2+20)
        for p in self.particles: p.draw(surf)

        if self._screen == "main":   self._draw_main(surf)
        elif self._screen == "controls": self._draw_controls(surf)
        elif self._screen == "options":  self._draw_options(surf)

    def _draw_main(self, surf):
        W,H = SCREEN_W, SCREEN_H
        ft = self._f(20, bold=True)
        title = "A PEDRA DOS ANCESTRAIS"
        sh = ft.render(title, True, (40,20,0))
        ts = ft.render(title, True, GOLD)
        tx = (W-ts.get_width())//2
        surf.blit(sh,(tx+2,18)); surf.blit(ts,(tx,16))
        sub = self._f(10).render("Uma lenda do Piauí", True, (220,180,120))
        surf.blit(sub,((W-sub.get_width())//2,40))

        # Painel menu
        pw,ph = 180, len(MENU_ITEMS)*24+16
        px = (W-pw)//2; py = H//2-20
        panel = pygame.Surface((pw,ph), pygame.SRCALPHA)
        panel.fill((8,4,18,215))
        surf.blit(panel,(px,py))
        pygame.draw.rect(surf,(50,40,25),(px,py,pw,ph),1)
        pygame.draw.rect(surf,GOLD,(px+2,py+2,pw-4,ph-4),1)

        fi = self._f(11)
        for i,item in enumerate(MENU_ITEMS):
            iy = py+10+i*24
            sel = (i == self._sel)
            if sel:
                hl = pygame.Surface((pw-8,20), pygame.SRCALPHA)
                hl.fill((220,170,40,28))
                surf.blit(hl,(px+4,iy-2))
                pulse = int(abs(math.sin(self.time*0.1))*4)
                surf.blit(fi.render("▶",True,GOLD),(px+8+pulse,iy))
                col = GOLD
            else:
                col = (155,135,78)
            surf.blit(fi.render(item,True,col),(px+26,iy))

        ver = self._f(9).render("v4",True,(50,42,28))
        surf.blit(ver,(W-ver.get_width()-6,H-12))

    def _draw_submenu_bg(self, surf, title):
        W,H = SCREEN_W,SCREEN_H
        ov = pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,185))
        surf.blit(ov,(0,0))
        pw,ph=280,180; px=(W-pw)//2; py=(H-ph)//2
        panel=pygame.Surface((pw,ph),pygame.SRCALPHA); panel.fill((8,4,18,245))
        surf.blit(panel,(px,py))
        pygame.draw.rect(surf,(50,40,25),(px,py,pw,ph),1)
        pygame.draw.rect(surf,GOLD,(px+2,py+2,pw-4,ph-4),1)
        t=self._f(13,bold=True).render(title,True,GOLD)
        surf.blit(t,((W-t.get_width())//2,py+10))
        pygame.draw.line(surf,(60,48,24),(px+16,py+30),(px+pw-16,py+30),1)

    def _draw_controls(self, surf):
        W,H = SCREEN_W,SCREEN_H
        self._draw_submenu_bg(surf,"CONTROLES")
        fb=self._f(10,bold=True); fi=self._f(10)
        y0=H//2-46
        for i,(action,key) in enumerate(CONTROLS):
            y=y0+i*18
            surf.blit(fb.render(action,True,GOLD),(W//2-90,y))
            surf.blit(fi.render(key,True,(200,178,120)),(W//2+10,y))
        back=self._f(9).render("[ESC / X] Voltar",True,(90,76,44))
        surf.blit(back,((W-back.get_width())//2,H//2+70))

    def _draw_options(self, surf):
        W,H = SCREEN_W,SCREEN_H
        self._draw_submenu_bg(surf,"OPÇÕES")
        fi=self._f(10)
        for i,txt in enumerate(["Volume: ████████░░","Velocidade do texto: Normal"]):
            t=fi.render(txt,True,(180,160,100))
            surf.blit(t,((W-t.get_width())//2,H//2-20+i*20))
        hint=fi.render("(em breve)",True,(80,68,42))
        surf.blit(hint,((W-hint.get_width())//2,H//2+40))
        back=self._f(9).render("[ESC / X] Voltar",True,(90,76,44))
        surf.blit(back,((W-back.get_width())//2,H//2+70))
