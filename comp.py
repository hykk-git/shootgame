import math
from abc import * 
import random

class GameObject(ABC):
    # 슈팅게임의 모든 오브젝트들은 이름과 생성순이 존재함
    def __init__(self, name):
        self.name = name

class Visible(GameObject):
    # 오브젝트 중 게임 화면에 보이는 것들은 크기와 좌표가 존재함
    def __init__(self, name, point_x, point_y, size):
        super().__init__(name)
        self.point_x = point_x
        self.point_y = point_y
        self.size = size

    def point(self):
        return self.point_x, self.point_y

    def aabb(self):
        pass

    def update(self):
        pass

class Movable(Visible):
    # 화면에 보이는 객체 중 움직이는 객체도 있음

    # 움직이는 객체는 자기 위치를 갱신해야 함
    def __init__(self, name, point_x, point_y, size, speed):
        super().__init__(name, point_x, point_y, size)
        self.speed = speed

    def move(self, dx, dy):
        self.point_x += dx
        self.point_y += dy

class Collidable(Movable):
    # 움직이는 객체들 중엔 충돌하는 객체도 있음
    # 근데 지금 상황에선 모든 움직이는 객체들은 충돌함
    def is_collision(self, unit):
        x1, y1, x2, y2 = self.aabb()
        a1, b1, a2, b2 = unit.aabb()
        return x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1

class Gun(Visible):
    def __init__(self):
        super().__init__("Gun", 300, 800, 20)
        self.max_bullet = 3

    def update(self):
        self.point_x, self.point_y = GameArea.frame_size[0] // 2, GameArea.frame_size[1]

    def fire(self, angle):
        if len(Bullet.bullets) >= self.max_bullet:
            Bullet.bullets.pop(0)
        Bullet.create_bullet(angle)

class Bullet(Collidable):
    bullets = []
    
    def __init__(self, angle):
        super().__init__("Bullet", 300, 800, 5, 10)
        self.angle = angle
        self.dx = self.speed * math.sin(math.radians(self.angle))
        self.dy = -self.speed * math.cos(math.radians(self.angle))
        Bullet.bullets.append(self)
    
    @classmethod
    def create_bullet(cls, angle):
        return cls(angle)

    def update(self):
        self.move(self.dx, self.dy)
    
    def reflex(self):
        self.angle = -self.angle

class Enemy(Collidable):
    enemies = []
    SPAWN_POS = [50, 150, 250, 350, 450]

    def __init__(self):
        x = random.choice(self.SPAWN_POS)
        super().__init__("Enemy", x, 0, 30, 3)
        Enemy.enemies.append(self)
    
    @classmethod
    def create_enemy(cls):
        return cls()
    
    def update(self):
        self.move(0, self.speed)

class GameArea(Visible):
    frame_size = (600, 800)
    
    def __init__(self):
        super().__init__("GameArea", 0, 0, 0)
        self.width, self.height = self.frame_size
    
    def aabb(self):
        return self.point_x, self.point_y, self.width, self.height
    
    def update(self):
        self.point_x, self.point_y = 0, self.height

class Score(GameObject):
    def __init__(self):
        super().__init__("Score")
        self.status = 0
    
    def activate(self):
        self.status += 1

class Life(GameObject):
    def __init__(self):
        super().__init__("Life")
        self.status = 3
    
    def activate(self):
        self.status -= 1

class ShootingGame:
    def __init__(self):
        self.game_area = GameArea()
        self.gun = Gun()
        self.score = Score()
        self.life = Life()
        self.bullets = []
        self.enemies = []
        self.running = True
    
    def spawn_enemy(self):
        if self.running:
            self.enemies.append(Enemy())
    
    def update(self):
        if not self.running:
            return
        
        self.gun.update()
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.point_y < 0:
                self.bullets.remove(bullet)
        
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.point_y >= self.game_area.height:
                self.enemies.remove(enemy)
                self.life.activate()
                if self.life.status <= 0:
                    self.running = False
        
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.is_collision(enemy):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score.activate()

    def run(self):
        while self.running:
            self.spawn_enemy()
            self.update()
            print(f"Score: {self.score.status}, Life: {self.life.status}")

if __name__ == "__main__":
    game = ShootingGame()
    game.run()
