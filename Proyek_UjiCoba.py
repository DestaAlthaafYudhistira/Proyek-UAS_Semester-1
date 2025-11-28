import pygame
import sys
import random
import time
import json
import os

# Inisialisasi PyGame
pygame.init()

# Konstanta layar
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Tebak Gambar")

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 150)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 150, 50)
GRAY = (200, 200, 200)
DARK_BLUE = (50, 100, 200)
DARK_RED = (200, 50, 50)

# Font
title_font = pygame.font.SysFont('arial', 48, bold=True)
header_font = pygame.font.SysFont('arial', 36, bold=True)
button_font = pygame.font.SysFont('arial', 28)
option_font = pygame.font.SysFont('arial', 24)
score_font = pygame.font.SysFont('arial', 32)

# ==================== BAGIAN INI YANG HARUS ANDA GANTI ====================
# Data game - GANTI dengan gambar dan pertanyaan Anda sendiri
GAME_DATA = [
    {
        "image_path": ["mita1.png", "mita2.png", "mita3.png"],  # GANTI dengan path gambar Anda
        "correct_answer": "Mita",
        "options": ["Shinoa", "Emilia", "Mari", "Mita"],
        "Clue": "Waifu Desta"
    },
    {
        "image_path": ["mita1.png", "mita2.png", "mita3.png"],
        "correct_answer": "Mita",
        "options": ["Rem", "Akeno", "Mita", "Basil"],
        "Clue": "Waifu Desta"
    },
    {
        "image_path": ["mita1.png", "mita3.png", "mita4.png"],
        "correct_answer": "Mita",
        "options": ["Mita", "Boboiboy", "Rias", "Zenon"],
        "Clue": "Waifu Desta"
    },
    {
        "image_path": ["mita1.png", "mita2.png", "mita4.png"],
        "correct_answer": "Mita",
        "options": ["Katagaki", "Chitose", "Mita", "Elysia"],
        "Clue": "Waifu Desta"
    },
    {
        "image_path": ["mita3.png", "mita2.png", "mita4.png"],
        "correct_answer": "Mita",
        "options": ["Yuki", "Sparkle", "Furina", "Mita"],
        "Clue": "Waifu Desta"
    }
]

# Placeholder images jika gambar tidak ditemukan
def create_placeholder_image(width, height, text, color):
    surf = pygame.Surface((width, height))
    surf.fill(color)
    font = pygame.font.SysFont('arial', 20)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(width//2, height//2))
    surf.blit(text_surf, text_rect)
    return surf

# ===========================================================================

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.popup_scale = 1.0  # ukuran awal
        
        self.font_size = 24
        self.anim_font = 0      # <= WAJIB ADA

        self.font = pygame.font.SysFont(None, self.font_size)
        
    def draw(self, surface):
        # Animasi membesar saat hover
        target_scale = 1.08 if self.is_hovered else 1.0
        self.popup_scale += (target_scale - self.popup_scale) * 0.2

        new_w = int(self.original_rect.width * self.popup_scale)
        new_h = int(self.original_rect.height * self.popup_scale)

        self.rect.width = new_w
        self.rect.height = new_h
        self.rect.center = self.original_rect.center
        
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)
        
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class OptionButton(Button):
    def __init__(self, x, y, width, height, text, index):
        super().__init__(x, y, width, height, text, BLUE, DARK_BLUE)
        self.index = index
        self.is_correct = False
        self.is_wrong = False
        
    def draw(self, surface):

        # Pilih warna berdasarkan status
        if self.is_correct:
            color = GREEN
        elif self.is_wrong:
            color = RED
        else:
            color = self.hover_color if self.is_hovered else self.color
        
        # === Animasi POPUP SCALE ===
        target_scale = 1.1 if self.is_hovered else 1.0
        self.popup_scale += (target_scale - self.popup_scale) * 0.2
        
        # Hitung ukuran baru
        new_w = int(self.original_rect.width * self.popup_scale)
        new_h = int(self.original_rect.height * self.popup_scale)
        self.rect.width = new_w
        self.rect.height = new_h
        self.rect.center = self.original_rect.center
        
        # Draw tombol
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)

        # === ANIMASI FONT POPUP ===
        scaled_font_size = int(24 * self.popup_scale)
        scaled_font_size = max(20, scaled_font_size)
        popup_font = pygame.font.SysFont('arial', scaled_font_size, bold=True)

        text_surf = popup_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Game:
    def __init__(self):
        self.state = "home"  # home, gameplay, results, leaderboard
        self.player_name = ""
        self.input_active = False
        self.caret_visible = True
        self.last_caret_time = time.time()
        self.current_question = 0
        self.score = 0
        self.correct_answers = 0
        self.time_left = 30
        self.timer_start = 0
        self.game_active = False
        self.current_image_path = None
        
        # Load leaderboard
        self.leaderboard = self.load_leaderboard()
        
        # Setup buttons
        self.setup_buttons()
    def draw_input_name_screen(self):
        SCREEN.fill(DARK_BLUE)

        # Judul
        title = title_font.render("Masukkan Nama Anda", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))

        # Kotak input
        box_rect = pygame.Rect(300, 260, 400, 60)
        pygame.draw.rect(SCREEN, WHITE, box_rect, border_radius=10)
        pygame.draw.rect(SCREEN, BLUE, box_rect, 3, border_radius=10)

        # Teks input
        text_surface = header_font.render(self.player_name, True, BLACK)
        SCREEN.blit(text_surface, (box_rect.x + 15, box_rect.y + 10))

        # Caret blinking
        if self.input_active:
            if time.time() - self.last_caret_time > 0.5:
                self.caret_visible = not self.caret_visible
                self.last_caret_time = time.time()

            if self.caret_visible:
                caret_x = box_rect.x + 15 + text_surface.get_width() + 3
                caret_y = box_rect.y + 10
                pygame.draw.line(SCREEN, BLACK, (caret_x, caret_y),
                                (caret_x, caret_y + 40), 2)

        # Info
        info = option_font.render("Tekan ENTER untuk memulai game", True, YELLOW)
        SCREEN.blit(info, info.get_rect(center=(SCREEN_WIDTH//2, 360)))

    
    def draw_input_name_screen(self):
        SCREEN.fill(DARK_BLUE)

        # Judul
        title = title_font.render("Masukkan Nama Anda", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))

        # Kotak input
        box_rect = pygame.Rect(300, 260, 400, 60)
        pygame.draw.rect(SCREEN, WHITE, box_rect, border_radius=10)
        pygame.draw.rect(SCREEN, BLUE, box_rect, 3, border_radius=10)

        # Teks input
        text_surface = header_font.render(self.player_name, True, BLACK)
        SCREEN.blit(text_surface, (box_rect.x + 15, box_rect.y + 10))

        # Caret blinking
        if self.input_active:
            if time.time() - self.last_caret_time > 0.5:
                self.caret_visible = not self.caret_visible
                self.last_caret_time = time.time()

            if self.caret_visible:
                caret_x = box_rect.x + 15 + text_surface.get_width() + 3
                caret_y = box_rect.y + 10
                pygame.draw.line(SCREEN, BLACK, (caret_x, caret_y),
                                (caret_x, caret_y + 40), 2)

        # Info
        info = option_font.render("Tekan ENTER untuk memulai game", True, YELLOW)
        SCREEN.blit(info, info.get_rect(center=(SCREEN_WIDTH//2, 360)))

        
    def setup_buttons(self):
        # Home screen buttons
        button_width, button_height = 300, 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.start_button = Button(center_x, 300, button_width, button_height, 
                                 "Mulai Game", GREEN, (50, 200, 50))
        self.leaderboard_button = Button(center_x, 380, button_width, button_height, 
                                       "Lihat Leaderboard", BLUE, DARK_BLUE)
        
        # ==================== TOMBOL EXIT BARU ====================
        self.exit_button = Button(center_x, 460, button_width, button_height, 
                                "Keluar Game", DARK_RED, (150, 0, 0))
        # ==========================================================
        
        # Game screen buttons
        self.skip_button = Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 75, 90, 40, 
                                "Skip", ORANGE, (255, 120, 0))
        
        # Results screen buttons
        self.play_again_button = Button(center_x, 400, button_width, button_height, 
                                      "Main Lagi", GREEN, (50, 200, 50))
        self.home_button = Button(center_x, 480, button_width, button_height, 
                                "Kembali ke Home", BLUE, DARK_BLUE)
        
        # Leaderboard screen button
        self.back_button = Button(center_x, 550, button_width, button_height, 
                                "Kembali ke Home", BLUE, DARK_BLUE)
    
    def load_leaderboard(self):
        try:
            if os.path.exists("leaderboard.json"):
                with open("leaderboard.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_leaderboard(self):
        # Add current score
        player_name = self.player_name if self.player_name.strip() != "" else "Player"
        self.leaderboard.append({
            "name": player_name,
            "score": self.score,
            "correct": self.correct_answers,
            "date": time.strftime("%d/%m/%Y %H:%M")
        })
        
        # Sort by score (descending)
        self.leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        # Keep only top 10
        self.leaderboard = self.leaderboard[:10]
        
        # Save to file
        try:
            with open("leaderboard.json", "w") as f:
                json.dump(self.leaderboard, f)
        except:
            pass
    
    def start_game(self):
        self.state = "gameplay"
        self.current_question = 0
        self.score = 0
        self.correct_answers = 0
        self.game_active = True
        self.load_question()
    
    def load_question(self):
        if self.current_question >= len(GAME_DATA):
            self.end_game()
            return
        
        # Pilih gambar secara acak dari image_paths
        image_path = GAME_DATA[self.current_question]["image_path"]
        self.current_image_path = random.choice(image_path)

        self.time_left = 30
        self.timer_start = time.time()
        self.create_option_buttons()
    
    def create_option_buttons(self):
        self.option_buttons = []
        option_width, option_height = 350, 50
        spacing_x = 40
        spacing_y = 20

        # Salin options dan acak urutannya untuk randomisasi jawaban
        options = GAME_DATA[self.current_question]["options"][:]
        random.shuffle(options)

        # total 2 kolom
        left_x = SCREEN_WIDTH//2 - option_width - spacing_x//2
        right_x = SCREEN_WIDTH//2 + spacing_x//2

        # posisi mulai Y
        start_y = 480  

        for i, option in enumerate(options):
            x = left_x if i % 2 == 0 else right_x
            y = start_y + (i//2) * (option_height + spacing_y)

            btn = OptionButton(x, y, option_width, option_height, option, i)
            self.option_buttons.append(btn)

    def check_answer(self, selected_option):
        if not self.game_active:
            return
        
        correct_answer = GAME_DATA[self.current_question]["correct_answer"]
        
        # Tandai jawaban yang benar dan salah
        for btn in self.option_buttons:
            if btn.text == correct_answer:
                btn.is_correct = True
            elif btn.text == selected_option and selected_option != correct_answer:
                btn.is_wrong = True
            btn.is_hovered = False
        
        # Beri skor jika benar
        if selected_option == correct_answer:
            time_bonus = max(0, self.time_left)  # Bonus berdasarkan waktu tersisa
            self.score += 10 + time_bonus // 3  # Base 10 + bonus waktu
            self.correct_answers += 1

        self.game_active = False
        pygame.time.set_timer(pygame.USEREVENT, 2000)  # Timer untuk lanjut ke soal berikutnya
    
    def skip_question(self):
        if self.game_active:
            self.game_active = False
            self.next_question()
    
    def next_question(self):
        self.current_question += 1
        self.game_active = True
        self.load_question()
        pygame.time.set_timer(pygame.USEREVENT, 0)  # Hentikan timer
    
    def end_game(self):
        self.state = "results"
        self.save_leaderboard()
    
    def update_timer(self):
        if self.game_active and self.state == "gameplay":
            elapsed = time.time() - self.timer_start
            self.time_left = max(0, 30 - int(elapsed))
            
            if self.time_left == 0:
                self.skip_question()
    
    def draw_home_screen(self):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color = (
                int(100 + (155 * y / SCREEN_HEIGHT)),
                int(150 + (105 * y / SCREEN_HEIGHT)),
                255
            )
            pygame.draw.line(SCREEN, color, (0, y), (SCREEN_WIDTH, y))
        
        # Title
        title_text = title_font.render("GAME TEBAK GAMBAR", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        SCREEN.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = header_font.render("Uji Pengetahuan Anda!", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 220))
        SCREEN.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        self.start_button.draw(SCREEN)
        self.leaderboard_button.draw(SCREEN)
        
        # ==================== TOMBOL EXIT BARU ====================
        self.exit_button.draw(SCREEN)
        
        # Credit atau informasi tambahan
        credit_text = option_font.render("Klik 'Keluar Game' untuk menutup aplikasi", True, WHITE)
        credit_rect = credit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        SCREEN.blit(credit_text, credit_rect)
        # ==========================================================
    
    def draw_game_screen(self):
        # Background
        SCREEN.fill(DARK_BLUE)
        
        # Header dengan informasi game
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(SCREEN, BLUE, header_rect)
        pygame.draw.line(SCREEN, WHITE, (0, 80), (SCREEN_WIDTH, 80), 2)
        
        # Timer dengan efek visual
        timer_color = RED if self.time_left <= 10 else YELLOW if self.time_left <= 20 else GREEN
        timer_text = header_font.render(f"Waktu: {self.time_left}s", True, timer_color)
        SCREEN.blit(timer_text, (20, 20))
        
        # Skor
        score_text = header_font.render(f"Skor: {self.score}", True, WHITE)
        SCREEN.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        # Progress soal
        progress_text = header_font.render(f"Soal: {self.current_question + 1}/{len(GAME_DATA)}", True, WHITE)
        SCREEN.blit(progress_text, (SCREEN_WIDTH//2 - 60, 20))
        
        # Gambar pertanyaan
        try:
            # ==================== BAGIAN INI YANG HARUS ANDA GANTI ====================
            # GANTI dengan cara load gambar Anda yang sebenarnya
            image = pygame.image.load(self.current_image_path)
            image = pygame.transform.scale(image, (400, 300))
            # =========================================================================
        except:
            # Fallback ke placeholder jika gambar tidak ditemukan
            image = create_placeholder_image(400, 300, 
                                           f"Gambar {self.current_question + 1}", 
                                           PURPLE)
        
        image_rect = image.get_rect(center=(SCREEN_WIDTH//2, 250))
        SCREEN.blit(image, image_rect)
        
        # Clue
        Clue_text = option_font.render(f"Clue: {GAME_DATA[self.current_question]['Clue']}", True, YELLOW)
        Clue_rect = Clue_text.get_rect(center=(SCREEN_WIDTH//2, 435))
        SCREEN.blit(Clue_text, Clue_rect)
        
        # Opsi jawaban
        for btn in self.option_buttons:
            btn.draw(SCREEN)
        
        # Skip button
        self.skip_button.draw(SCREEN)
    
    def draw_results_screen(self):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color = (
                int(100 + (155 * y / SCREEN_HEIGHT)),
                int(150 + (105 * y / SCREEN_HEIGHT)),
                255
            )
            pygame.draw.line(SCREEN, color, (0, y), (SCREEN_WIDTH, y))
        
        # Title
        title_text = title_font.render("GAME SELESAI!", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        SCREEN.blit(title_text, title_rect)
        
        # Skor akhir
        score_text = header_font.render(f"Skor Akhir: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 230))
        SCREEN.blit(score_text, score_rect)
        
        # Jawaban benar
        correct_text = header_font.render(f"Jawaban Benar: {self.correct_answers}/{len(GAME_DATA)}", True, GREEN)
        correct_rect = correct_text.get_rect(center=(SCREEN_WIDTH//2, 290))
        SCREEN.blit(correct_text, correct_rect)
        
        # Pesan berdasarkan performa
        if self.correct_answers == len(GAME_DATA):
            message = "Luar Biasa! Nilai Sempurna!"
            color = YELLOW
        elif self.correct_answers >= len(GAME_DATA) * 0.7:
            message = "Hebat! Hampir Sempurna!"
            color = GREEN
        elif self.correct_answers >= len(GAME_DATA) * 0.5:
            message = "Bagus! Terus Berlatih!"
            color = BLUE
        else:
            message = "Jangan Menyerah! Coba Lagi!"
            color = ORANGE
        
        message_text = header_font.render(message, True, color)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        SCREEN.blit(message_text, message_rect)
        
        # Draw buttons
        self.play_again_button.draw(SCREEN)
        self.home_button.draw(SCREEN)
    
    def draw_leaderboard_screen(self):
        # Background
        SCREEN.fill(DARK_BLUE)
        
        # Title
        title_text = title_font.render("LEADERBOARD", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        SCREEN.blit(title_text, title_rect)
        
        # Header table
        def draw_leaderboard_screen(self):
            # Background
            SCREEN.fill(DARK_BLUE)
            
        # Title
        title_text = title_font.render("LEADERBOARD", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        SCREEN.blit(title_text, title_rect)
        
        # Header table
        header_rect = pygame.Rect(100, 150, SCREEN_WIDTH-200, 50)
        pygame.draw.rect(SCREEN, BLUE, header_rect, border_radius=10)
        
        headers = ["Peringkat", "Nama", "Skor", "Benar", "Tanggal"]
        column_width = (SCREEN_WIDTH - 200) // len(headers)
        
        for i, header in enumerate(headers):
            header_text = button_font.render(header, True, WHITE)
            header_pos = (100 + i * column_width + column_width//2, 175)
            SCREEN.blit(header_text, header_text.get_rect(center=header_pos))
        
        # Entries
        start_y = 220
        row_height = 40
        for idx, entry in enumerate(self.leaderboard):
            y = start_y + idx * row_height
            rank_text = option_font.render(str(idx + 1), True, WHITE)
            name_text = option_font.render(entry.get("name", "-"), True, WHITE)
            score_text = option_font.render(str(entry.get("score", "-")), True, WHITE)
            correct_text = option_font.render(str(entry.get("correct", "-")), True, WHITE)
            date_text = option_font.render(entry.get("date", "-"), True, WHITE)
            
            SCREEN.blit(rank_text, rank_text.get_rect(center=(100 + column_width*0 + column_width//2,y)))
            SCREEN.blit(name_text, name_text.get_rect(center=(100 + column_width*1 + column_width//2,y)))
            SCREEN.blit(score_text, score_text.get_rect(center=(100 + column_width*2 + column_width//2,y)))
            SCREEN.blit(correct_text, correct_text.get_rect(center=(100 + column_width*3 + column_width//2,y)))
            SCREEN.blit(date_text, date_text.get_rect(center=(100 + column_width*4 + column_width//2,y)))
        
        # Back button
        self.back_button.draw(SCREEN)
    
    def draw(self):
        if self.state == "home":
            self.draw_home_screen()
        elif self.state == "input_name":
            self.draw_input_name_screen()
        elif self.state == "gameplay":
            self.draw_game_screen()
        elif self.state == "results":
            self.draw_results_screen()
        elif self.state == "leaderboard":
            self.draw_leaderboard_screen()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        # INPUT NAMA PEMAIN
        if self.state == "input_name":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.input_active = True

                if event.type == pygame.KEYDOWN and self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.player_name.strip() != "":
                            self.start_game()
                        return True

                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]

                    else:
                        if len(self.player_name) < 12:
                            self.player_name += event.unicode
            return True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle button hovers
            if self.state == "home":
                self.start_button.check_hover(mouse_pos)
                self.leaderboard_button.check_hover(mouse_pos)
                self.exit_button.check_hover(mouse_pos)  # ← TAMBAHAN: Hover effect tombol exit
                
                if self.start_button.is_clicked(mouse_pos, event):
                    self.state = "input_name"
                    self.player_name = ""
                    self.input_active = True

                elif self.leaderboard_button.is_clicked(mouse_pos, event):
                    self.state = "leaderboard"
                
                # ==================== FUNGSI EXIT BARU ====================
                elif self.exit_button.is_clicked(mouse_pos, event):
                    return False  # Keluar dari game
                # ==========================================================
            
            elif self.state == "gameplay":
                self.skip_button.check_hover(mouse_pos)
                
                if self.skip_button.is_clicked(mouse_pos, event):
                    self.skip_question()
                
                if self.game_active:
                    for btn in self.option_buttons:
                        btn.check_hover(mouse_pos)
                        if btn.is_clicked(mouse_pos, event):
                            self.check_answer(btn.text)
            
            elif self.state == "results":
                self.play_again_button.check_hover(mouse_pos)
                self.home_button.check_hover(mouse_pos)
                
                if self.play_again_button.is_clicked(mouse_pos, event):
                    self.start_game()
                elif self.home_button.is_clicked(mouse_pos, event):
                    self.state = "home"
            
            elif self.state == "leaderboard":
                self.back_button.check_hover(mouse_pos)
                
                if self.back_button.is_clicked(mouse_pos, event):
                    self.state = "home"
            
            # Timer event untuk lanjut ke soal berikutnya
            if event.type == pygame.USEREVENT:
                self.next_question()
        
        return True

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    # Buat folder images jika belum ada
    if not os.path.exists("images"):
        os.makedirs("images")
    
    running = True
    while running:
        running = game.handle_events()
        game.update_timer()
        
        SCREEN.fill(BLACK)  # Clear screen
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
