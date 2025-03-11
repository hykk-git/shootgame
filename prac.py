from abc import *
import math
import random

class ShootingGame(ABC):
    def start(self):
        pass

class GameObject(ShootingGame, ABC):
    # 슈팅게임의 모든 오브젝트들은 이름과 생성순이 존재함
    def __init__(self, name):
        self.name = name

class Visible(GameObject):
    # 오브젝트 중 게임 화면에 보이는 것들은 크기와 좌표가 존재함
    def __init__(self, x, y, size):
        x = x
        y = y
        size = size
    
    @abstractmethod
    def get_position(self):
        pass

class Movable(Visible, ABC):
    # 화면에 보이는 객체 중 움직이는 객체도 있음

    # 움직이는 객체는 자기 위치를 갱신해야 함
    @abstractmethod
    def update_position(self):
        pass
        
class Collidable(Movable, ABC):
    # 움직이는 객체들 중엔 충돌하는 객체도 있음
    # 근데 지금 상황에선 모든 움직이는 객체들은 충돌함

    @abstractmethod
    def is_collision(self, visible):
        pass

class Bullet(Collidable):
    speed = 50

    def __init__(self, angle):
        super.__init__()
        self.angle = math.radians(angle)

    def update_position(self):
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.dx = -self.dx
        
        self.dx += self.speed * math.cos(self.angle)
        self.dy += self.speed * math.sin(self.angle)
    
    def get_position(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def isCollision(self, visible):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = visible.get_position()

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1
    
class Enemy(Collidable):
    speed = 20

    def __init__(self, x, y):
        self.dx = x
        self.dy = y

    def update_position(self):
        self.dy += self.speed
    
    def get_position(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def isCollision(self, visible):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = visible.get_position()

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1
    
class Gun(Visible):
    MAX_BULLETS = 3

    def __init__(self):
        self.x = x
        self.bullets = []

    def get_position(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def fire(self, angle):
        if len(self.bullets) < self.MAX_BULLETS:
            bullet = Bullet(self.x, self.y, angle)
            self.bullets.append(bullet)

class GameFrame(Visible):
    def __init__(self, width, height):
        self.height = height
        self.width = width
    
    def get_position(self):
        return 0, self.width, 0, self.height

class PlayerStatus(GameObject):
    def __init__(self, score, life):
        self.score = score
        self.life = life

    def update_score(self):
        self.score += 1
    
    def lose_life(self):
        self.life -= 1

if __name__ == "__main__":
    ShootingGame.start()
