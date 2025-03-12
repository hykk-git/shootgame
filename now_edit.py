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
    
    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable, ABC):
    # 충돌시 이벤트가 발생하는 객체-> 누구랑 충돌했는지 확인해야 함
    ck = CollisionHandler()

    def is_collide_at(self, unit):
        pass

class Bullet(Collidable):
    # fire할 때 생성되고 enemy, 벽이랑 충돌 체크해야 하는 Collidable 객체
    def __init__(self, angle, point_x, point_y, speed, size):
        self.angle = angle
        self.point_x = GameFrame.frame_size[0]//2
        self.point_y = GameFrame.frame_size[1]
        self.speed = speed
        self.size = size
    
    def update_position(self):
        self.point_x += self.speed * math.sin(math.radians(self.angle))
        self.point_y -= self.speed * math.cos(math.radians(self.angle))
    
    def reflex(self):
        self.angle = -self.angle
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    def is_collide_at(self, unit):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = unit.get_position()
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1
            ck.collide_occur(self, unit)

class Gun(Visible):
    # 총알을 발사하는 총 객체-> 내부에 총알을 가지고 있음
    bullets = []
    def __init__(self):
        self.max_bullet = 3
        self.point_x = GameFrame.frame_size[0]//2
        self.point_y = GameFrame.frame_size[1]

    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size
    
    def fire(self, angle):
        if len(self.bullets) >= self.max_bullet:
            self.bullets.pop(0)
        self.bullets.append(Bullet(angle))

class Enemy(Collidable):
    # start할 때 생성되고 바닥이랑 충돌 체크해야 하는 Collidable 객체
    def __init__(self, angle, point_x, point_y, speed, size):
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        self.speed = speed
        self.size = size
    
    def update_position(self):
        self.point_y += self.speed
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    def is_collide_at(self, unit):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = unit.get_position()
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1
            ck.collide_occur(self, unit)
            
class GameFrame(Visible):
    frame_size = (600, 800)
    
    def __init__(self):
        self.width, self.height = self.frame_size
    
    def get_position(self):
        return 0, 0, self.width, self.height

class PlayerStatus(GameObject):
    # User Info 관리 - DB에 저장 필요
    def __init__(self, score, life):
        self.score = score
        self.life = life

    def update_score(self):
        self.score += 1
    
    def lose_life(self):
        self.life -= 1

class CollType(ABC):
    ps = PlayerStatus()
    def activate(self):
        pass

class BulletToEnemy(CollType):
    def activate(self, bullet, enemy):
        bullet.delete()
        enemy.delete()
        self.ps.update_score()

class BulletToWalls(CollType):
    def activate(self, bullet, walls):
        bullet.reflex()

class EnemyToBottom(CollType):
    def activate(self, bullet, walls):
        self.ps.lose_life()

class CollisionHandler:
    # 충돌을 전달받고 충돌 타입에 따라 PlayerStatus에게 요청하는 객체
    ps = PlayerStatus()
    def collide_occur(self, unit1, unit2):
        # 절차형일 때
        if unit1 == Bullet and unit2 == GameFrame:
            unit1.reflex()
        elif unit1 == Bullet and unit2 == Enemy:
            unit1.delete()
            unit2.delete()
            self.ps.update_score()
        elif unit1 == Enemy and unit2 == GameFrame:
            unit1.delete()
            self.ps.lose_life()
        

class PositionCreater:
    # 모든 객체 생성을 담당하는 객체
    SPAWN_POS = [50, 150, 250, 350, 450]

    def create_object(self, object):
        pass

class PositionUpdater:
    # Movable 타입 객체 위치를 틱당 업데이트하는 객체
    pk = PositionCreater()
    ck = CollisionHandler()

    def update(self, unit):
        for bullet in self.bullets[:]:
            bullet.update_position()
            
        for enemy in self.enemies[:]:
            enemy.update_position()
        
        for bullet in self.bullets[:]:
            bullet.is_collide_at(enemy)
            bullet.is_collide_at(GameFrame)
        
        for enemy in self.enemies[:]:
            enemy.is_collide_at(GameFrame)

if __name__ == "__main__":
    game = ShootingGame()
    game.start()