import pygame, sys, random, time, json, os

pygame.init()
W, H = 950, 650
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Game Tebak Gambar")

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (50,200,80)
RED = (220,60,60)
BLUE_LIGHT = (90,140,255)
YELLOW = (240,230,90)

TITLE_FONT  = pygame.font.SysFont("arial", 48, bold=True)
HEADER_FONT = pygame.font.SysFont("arial", 32)
TEXT_FONT   = pygame.font.SysFont("arial", 24)
BTN_FONT    = pygame.font.SysFont("arial", 26)

GAME_DATA = [
    {"Nama": "Black Cat", "gambar": "Black Cat.jpg", "Clue": "Pacar Spiderman"},
    {"Nama": "Captain America", "gambar": "Captain America.jpg", "Clue": "Perisai"},
    {"Nama": "Daredevil", "gambar": "Daredevil.jpg", "Clue": "Dr di Spiderman Far From Home"},
    {"Nama": "Deadpool", "gambar": "Deadpool.jpg", "Clue": "Gak Bisa Mati"},
    {"Nama": "Dr. Doom", "gambar": "Dr. Doom.jpg", "Clue": "Villain Avengers Nanti"},
    {"Nama": "Dr. Octopus", "gambar": "Dr. Octopus.jpg", "Clue": "Gurita"},
    {"Nama": "Falcon", "gambar": "Falcon.jpg", "Clue": "Burung"},
    {"Nama": "Hawkeye", "gambar": "Hawkeye.jpg", "Clue": "Pemanah"},
    {"Nama": "Magneto", "gambar": "Magneto.jpg", "Clue": "Besi dan Listrik"},
    {"Nama": "Moon Knight", "gambar": "Moon Knight.jpg", "Clue": "Kepribadian Banyak"},
    {"Nama": "Punisher", "gambar": "Punisher.jpg", "Clue": "Gak Tau"},
    {"Nama": "Thor", "gambar": "Thor.jpg", "Clue": "Dewa Petir"},
    {"Nama": "Vision", "gambar": "Vision.jpg", "Clue": "Suami Wanda"},
    {"Nama": "Winter Soldier", "gambar": "Winter Soldier.jpg", "Clue": "Dingin"},
    {"Nama": "Wolverine", "gambar": "Wolverine.jpg", "Clue": "Cakar"}
]

class Button:
    def __init__(self, rect, text, color, hover):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect) 
        t = BTN_FONT.render(self.text, True, WHITE)
        SCREEN.blit(t, t.get_rect(center=self.rect.center))

    def click(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)
    
class Game:
    def __init__(self):
        self.state = "home"
        self.name = ""
        self.input_active = False
        self.current_q = 0
        self.score = 0
        self.correct = 0
        self.time_left = 30
        self.timer_start = 0
        self.max_q = 5
        self.used = set()
        self.answer = ""
        self.answered = None
        self.load_assets()
        self.load_leaderboard()
        self.setup_buttons()
        self.setup_handlers()

    def load_assets(self):
        try:
            bg = pygame.image.load("Test.png")
            self.background = pygame.transform.scale(bg, (W, H))
        except:
            self.background = pygame.Surface((W,H))
            self.background.fill((40,90,200))   

    def load_image(self, path, size):
        try:
            img = pygame.image.load(path)
            return pygame.transform.scale(img, size)
        except:
            surf = pygame.Surface(size); surf.fill(BLACK)
            msg = TEXT_FONT.render("Gambar tidak ditemukan", True, WHITE)
            surf.blit(msg, msg.get_rect(center=(size[0]//2,size[1]//2)))
            return surf

    def load_leaderboard(self):
        if os.path.exists("leaderboard.json"):
            try: self.leaderboard = json.load(open("leaderboard.json"))
            except: self.leaderboard = []
        else:
            self.leaderboard = []

    def save_leaderboard(self):
        self.leaderboard.append({
            "name": self.name or "Player",
            "score": self.score,
            "correct": self.correct,
            "date": time.strftime("%d/%m/%Y %H:%M")
        })
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x["score"], reverse=True)[:10]
        json.dump(self.leaderboard, open("leaderboard.json","w"), indent=2)

    def setup_buttons(self):
        cx = W//2 - 150
        self.btn_home = [
            Button((cx,300,300,55), "Mulai Game", GREEN, (40,160,60)),
            Button((cx,370,300,55), "Leaderboard", BLUE_LIGHT, (50,110,220)),
            Button((cx,440,300,55), "Keluar", RED, (180,40,40))
        ]
        self.btn_results = [
            Button((cx,450,300,55), "Main Lagi", GREEN, (40,160,60)),
            Button((cx,520,300,55), "Kembali", BLUE_LIGHT, (50,110,220))
        ]

        self.btn_skip = Button((W-150, H-70, 130,40), "Skip", YELLOW, (220,210,40))

    def setup_handlers(self):
        self.draw_state = {
            "home": self.draw_home,
            "input": self.draw_input,
            "play": self.draw_play,
            "result": self.draw_result,
            "leader": self.draw_leader
        }
        self.event_state = {
            "home": self.event_home,
            "input": self.event_input,
            "play": self.event_play,
            "result": self.event_result,
            "leader": self.event_leader
        }

    def start_game(self):
        self.state = "play"
        self.current_q = 0
        self.score = 0
        self.correct = 0
        self.used = set()
        self.next_question()

    def next_question(self):
        self.current_q += 1
        self.answered = None

        if self.current_q > self.max_q:
            self.state = "result"
            self.save_leaderboard()
            return

        available = [x for x in GAME_DATA if x["gambar"] not in self.used]
        q = random.choice(available)
        self.used.add(q["gambar"])
        self.data = q
        self.answer = q["Nama"]

        wrong = [x["Nama"] for x in GAME_DATA if x["Nama"] != self.answer]
        opts = random.sample(wrong, 3) + [self.answer]
        random.shuffle(opts)

        self.options = [
            opts[0], opts[1],
            opts[2], opts[3]
        ]
        self.time_left = 30
        self.timer_start = time.time()

    def update_timer(self):
        if self.state == "play":
            elapsed = int(time.time() - self.timer_start)
            self.time_left = max(0, 30 - elapsed)
            if self.time_left == 0:
                self.next_question()

    def draw_home(self):
        SCREEN.blit(self.background, (0, 0))
        t = TITLE_FONT.render("GAME TEBAK GAMBAR", True, WHITE)
        SCREEN.blit(t, t.get_rect(center=(W//2,150)))
        for b in self.btn_home: b.draw()

    def draw_input(self):
        SCREEN.blit(self.background, (0, 0))
        msg = HEADER_FONT.render("Masukkan Nama", True, WHITE)
        SCREEN.blit(msg, msg.get_rect(center=(W//2,150)))

        box = pygame.Rect(W//2-250, 240, 500, 60)
        pygame.draw.rect(SCREEN, BLUE_LIGHT, box)
        pygame.draw.rect(SCREEN, WHITE, box, 2)

        text = TEXT_FONT.render(self.name, True, WHITE)
        SCREEN.blit(text, (box.x+10, box.y+18))

    def draw_play(self):
        SCREEN.blit(self.background, (0, 0))
        info = HEADER_FONT.render(
            f"Soal {self.current_q}/{self.max_q}   Waktu: {self.time_left}s   Skor: {self.score}",
            True, WHITE
        )
        SCREEN.blit(info, (20, 20))
        img = self.load_image(os.path.join("images", self.data['gambar']), (380,280))
        SCREEN.blit(img, img.get_rect(center=(W//2,250)))
        clue = TEXT_FONT.render(f"Clue: {self.data['Clue']}", True, BLACK)
        SCREEN.blit(clue, clue.get_rect(center=(W//2,420)))

        positions = [
            (W//2 - 260, 480), 
            (W//2 + 20, 480),   
            (W//2 - 260, 540),  
            (W//2 + 20, 540)    
        ]

        self.option_rects = []
        for opt, pos in zip(self.options, positions):
            r = pygame.Rect(pos[0], pos[1], 240, 45)
            color = BLUE_LIGHT
            if self.answered:
                if opt == self.answer: color = GREEN
                elif opt == self.answered: color = RED

            pygame.draw.rect(SCREEN, color, r)
            t = TEXT_FONT.render(opt, True, WHITE)
            SCREEN.blit(t, t.get_rect(center=r.center))

            self.option_rects.append((r, opt))
        self.btn_skip.draw()

    def draw_result(self):
        SCREEN.blit(self.background, (0, 0))

        t = TITLE_FONT.render("GAME SELESAI!", True, WHITE)
        SCREEN.blit(t, t.get_rect(center=(W//2,150)))
        s = HEADER_FONT.render(f"Skor: {self.score}", True, WHITE)
        SCREEN.blit(s, s.get_rect(center=(W//2,260)))
        c = HEADER_FONT.render(f"Benar: {self.correct}/{self.max_q}", True, WHITE)
        SCREEN.blit(c, c.get_rect(center=(W//2,320)))

        for b in self.btn_results: b.draw()

    def draw_leader(self):
        SCREEN.blit(self.background, (0, 0))
        t = TITLE_FONT.render("LEADERBOARD", True, WHITE)
        SCREEN.blit(t, t.get_rect(center=(W//2,125)))
        y = 170
        for i, e in enumerate(self.leaderboard):
            line = TEXT_FONT.render(f"{i+1}. {e['name']} - {e['score']} pts - {e['correct']} benar - {e['date']}", True, RED)
            SCREEN.blit(line, (200,y))
            y += 30
        self.btn_results[1].draw()

    def event_home(self, e):
        if self.btn_home[0].click(e): self.state = "input"
        elif self.btn_home[1].click(e): self.state = "leader"
        elif self.btn_home[2].click(e): pygame.quit(); sys.exit()

    def event_input(self, e):
        box = pygame.Rect(W//2-250,240,500,60)

        if e.type == pygame.MOUSEBUTTONDOWN:
            self.input_active = box.collidepoint(e.pos)

        if e.type == pygame.KEYDOWN and self.input_active:
            if e.key == pygame.K_RETURN and self.name.strip():
                self.start_game()
            elif e.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                if len(self.name) < 20 and e.unicode.isprintable():
                    self.name += e.unicode

    def event_play(self, e):
        if self.btn_skip.click(e):
            self.next_question()

        if e.type == pygame.MOUSEBUTTONDOWN and self.answered is None:
            for rect, opt in self.option_rects:
                if rect.collidepoint(e.pos):
                    self.answered = opt
                    if opt == self.answer:
                        self.score += 10 + self.time_left//3
                        self.correct += 1
                    pygame.time.set_timer(pygame.USEREVENT, 700)

        if e.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 0)
            self.next_question()

    def event_result(self, e):
        if self.btn_results[0].click(e): self.start_game()
        if self.btn_results[1].click(e): self.state = "home"

    def event_leader(self, e):
        if self.btn_results[1].click(e): self.state = "home"

    def update(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            self.event_state[self.state](e)
        self.update_timer()
        self.draw_state[self.state]()
        pygame.display.flip()

def main():
    if not os.path.exists("images"): os.makedirs("images")
    clock = pygame.time.Clock()
    game = Game()

    while True:
        game.update()
        clock.tick(60)

if __name__ == "__main__":
    main()