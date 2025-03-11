import math
from abc import * 
import random

class GameObject:
    def __init__(self, name):
        self.name = name

    def create_object(self):
        pass

class ShootingGame:
    # 내부에 GameObject 객체를 갖고 있음(합성)
    obj = GameObject()
    def start(self, obj):
        # 게임 시작시 필요한 행동
        # 1. obj 생성해라
        self.obj.create_object()
    
    def player_input(self, obj):
        # 플레이어가 fire 누르면 총알 나가게
        self.obj.fire()
        pass
    
    def update_game(self, obj):
        # 객체 상태 갱신(위치, 플레이어 상태)
        self.obj.update_position()

class Visible(GameObject, ABC):
    # 화면에 보이는 객체-> 위치(좌표)와 크기를 갖고 있음
    def __init__(self, point_x, point_y, size):
        self.point_x = point_x
        self.point_y = point_y
        self.size = size
    
    @abstractmethod
    def get_position(self):
        # 자기 위치 반환 함수
        # 충돌 확인할 때 쓰임- 인자 순서가 x1, y1, x2, y2
        pass

class Movable(Visible, ABC):
    # 화면에 보이는 객체 중 움직이는 객체-> 속도(속력+방향) 갖고 있음
    speed = 0
    angle = 0
    def __init__(self, point_x, point_y, size):
        super().__init__(point_x, point_y, size)
    
    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable):
    # 충돌시 이벤트가 발생하는 객체-> 누구랑 충돌했는지 확인해야 함
    def is_collision(self, unit):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = unit.get_position()
        return x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1

class Gun(Visible):
    bullets = []
    def __init__(self, bullet):
        self.max_bullet = 3
        self.bullet = bullet
        self.point_x = GameFrame.frame_size[0]//2
        self.point_y = GameFrame.frame_size[1]

    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size
    
    def fire(self, angle):
        if len(self.bullets) >= self.max_bullet:
            self.bullets.pop(0)
        self.bullets.append(Bullet(angle))

class Bullet(Collidable):
    speed = 50
    
    def __init__(self, angle):
        self.angle = angle
        self.point_x = GameFrame.frame_size[0]//2
        self.point_y = GameFrame.frame_size[1]
    
    def update_position(self):
        self.point_x += self.speed * math.sin(math.radians(self.angle))
        self.point_y -= self.speed * math.cos(math.radians(self.angle))
    
    def reflex(self):
        self.angle = -self.angle
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

class Enemy(Collidable):
    SPAWN_POS = [50, 150, 250, 350, 450]
    speed = 20
    
    def __init__(self):
        x = random.choice(self.SPAWN_POS)
        super().__init__("Enemy", x, 0, 30, self.speed)
    
    def update_position(self):
        self.point_y += self.speed
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

class GameFrame(Visible):
    frame_size = (600, 800)
    
    def __init__(self):
        self.width, self.height = self.frame_size
    
    def get_position(self):
        return 0, 0, self.width, self.height

class PlayerStatus(GameObject):
    def __init__(self, score, life):
        self.score = score
        self.life = life

    def update_score(self):
        self.score += 1
    
    def lose_life(self):
        self.life -= 1

class FrameUpdater(GameObject):
    # 움직이는 객체 위치 업데이트하고, 충돌하는 객체 충돌 확인
    bullet = Bullet()
    enemy = Enemy()

    @abstractmethod
    def update(self):
        pass

class CollisionChecker(FrameUpdater):
    ps = PlayerStatus()
    def check(self, punit, unit):
        # 여기서 if문 쓰면 디미터 위반됨
        punit.is_collision(unit) 
        if punit.is_collision(unit):
                bullet.delete()
                self.ps.update_score()

        if punit.is_collision(unit):
                enemy.delete()
                self.ps.lose_life()

class PositionUpdater(FrameUpdater):
    ck = CollisionChecker()

    def update(self, unit):
        for bullet in self.bullets[:]:
            bullet.update_position()
            self.ck.check(bullet, enemy)
            self.ck.check(bullet, GameFrame)
            
        for enemy in self.enemies[:]:
            enemy.update_position()
            self.ck.check(enemy, GameFrame)

if __name__ == "__main__":
    game = ShootingGame()
    game.start()
