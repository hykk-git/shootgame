import math
from abc import * 
import random

class ShootingGame(ABC):
    @abstractmethod
    def spawn_enemy(self):
        pass
    
    @abstractmethod
    def update(self):
        pass
    
    @abstractmethod
    def run(self):
        pass

class GameObject(ABC):
    def __init__(self, name):
        self.name = name

class Visible(GameObject, ABC):
    def __init__(self, name, point_x, point_y, size):
        super().__init__(name)
        self.point_x = point_x
        self.point_y = point_y
        self.size = size
    
    @abstractmethod
    def get_position(self):
        pass

class Movable(Visible, ABC):
    def __init__(self, name, point_x, point_y, size, speed):
        super().__init__(name, point_x, point_y, size)
        self.speed = speed
    
    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable):
    def is_collision(self, unit):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = unit.get_position()
        return x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1

class Gun(Collidable):
    def __init__(self):
        super().__init__("Gun", 300, 800, 20, 0)
        self.max_bullet = 3
    
    def update_position(self):
        self.point_x, self.point_y = GameArea.frame_size[0] // 2, GameArea.frame_size[1]
    
    def get_position(self):
        return self.point_x, self.point_y
    
    def fire(self, angle):
        if len(Bullet.bullets) >= self.max_bullet:
            Bullet.bullets.pop(0)
        Bullet.create_bullet(angle)

class Bullet(Collidable):
    bullets = []
    speed = 50
    
    def __init__(self, angle):
        super().__init__("Bullet", 300, 800, 5, self.speed)
        self.angle = angle
        self.dx = self.speed * math.sin(math.radians(self.angle))
        self.dy = -self.speed * math.cos(math.radians(self.angle))
        Bullet.bullets.append(self)
    
    def update_position(self):
        self.point_x += self.dx
        self.point_y += self.dy
    
    def reflex(self):
        self.angle = -self.angle
    
    def get_position(self):
        return self.point_x, self.point_y

class Enemy(Collidable):
    SPAWN_POS = [50, 150, 250, 350, 450]
    speed = 20
    
    def __init__(self):
        x = random.choice(self.SPAWN_POS)
        super().__init__("Enemy", x, 0, 30, self.speed)
    
    def update_position(self):
        self.point_y += self.speed
    
    def get_position(self):
        return self.point_x, self.point_y

class GameArea(Visible):
    frame_size = (600, 800)
    
    def __init__(self):
        super().__init__("GameArea", 0, 0, 0)
        self.width, self.height = self.frame_size
    
    def get_position(self):
        return self.point_x, self.point_y, self.width, self.height

class PlayerStatus(GameObject):
    def __init__(self, score, life):
        super().__init__("PlayerStatus")
        self.score = score
        self.life = life
    
    def update_score(self):
        self.score += 1
    
    def lose_life(self):
        self.life -= 1

if __name__ == "__main__":
    game_area = GameArea()
    gun = Gun()
    player_status = PlayerStatus(score=0, life=3)
    bullets = []
    enemies = []
    running = True
    
    def spawn_enemy():
        if running:
            enemies.append(Enemy())
    
    def update():
        global running
        if not running:
            return
        
        gun.update_position()
        for bullet in bullets[:]:
            bullet.update_position()
            if bullet.point_y < 0:
                bullets.remove(bullet)
        
        for enemy in enemies[:]:
            enemy.update_position()
            if enemy.point_y >= game_area.height:
                enemies.remove(enemy)
                player_status.lose_life()
                if player_status.life <= 0:
                    running = False
        
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.is_collision(enemy):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    player_status.update_score()
    
    while running:
        spawn_enemy()
        update()
        print(f"Score: {player_status.score}, Life: {player_status.life}")
