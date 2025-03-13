import math
from abc import * 
from multipledispatch import dispatch
import random

class ShootingGameModel:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # 게임 경계 생성
        self.bottom = Bottom(width, height)
        self.left_wall = LeftWalls(width, height)
        self.right_wall = RightWalls(width, height)
        
        # 플레이어 상태 생성
        self.player_status = PlayerStatus()

        self.gun = GunObjectCreater().create_object()
        self.enemies = []
        
    def fire_gun(self, angle):
        self.gun.fire(angle)

class GameObject:
    pass

class Visible(GameObject, ABC):
    # 화면에 보이는 객체-> 위치(좌표)와 크기를 갖고 있음
    size = 0
    
    def __init__(self, point_x, point_y, size):
        self.point_x = point_x
        self.point_y = point_y
    
    @abstractmethod
    def get_position(self):
        # 자기 위치 반환 함수
        # 충돌 확인할 때 쓰임- 인자 순서가 x1, y1, x2, y2
        pass

class Movable(Visible, ABC):
    # 화면에 보이는 객체 중 움직이는 객체-> 속도(속력+방향) 갖고 있음
    size = 0
    speed = 0

    def __init__(self, angle, point_x, point_y):
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        
    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable, ABC):
    # 충돌시 이벤트가 발생하는 객체-> 누구랑 충돌했는지 확인해야 함
    speed = 20
    size = 20

    def __init__(self, angle, point_x, point_y, coll_handler):
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        self.coll_handler = coll_handler 

    def is_collide_at(self, object):
        pass

class Bullet(Collidable):
    # fire할 때 생성되고 enemy, 벽이랑 충돌 체크해야 하는 Collidable 객체
    speed = 50
    size = 20

    def __init__(self, angle, point_x, point_y, coll_handler):
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        self.coll_handler = coll_handler
    
    def update_position(self):
        self.point_x += self.speed * math.sin(math.radians(self.angle))
        self.point_y -= self.speed * math.cos(math.radians(self.angle))
    
    def reflex(self):
        self.angle = -self.angle
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    def is_collide_at(self, object):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = object.get_position()
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1:
            self.coll_handler.collide_occur(self, object)

class Gun(Visible):
    # 총알을 발사하는 총 객체-> 내부에 총알을 가지고 있음
    max_bullet = 3
    size = 100

    def __init__(self, point_x, point_y):
        # 현재 좌표(점) 초기화
        self.point_x = point_x
        self.point_y = point_y
        self.bullets = []

    def get_bullets(self):
        # 생성된 Bullet들을 리스트로 반환
        return self.bullets
    
    def get_position(self):
        # 현재 위치(영역) 반환
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size
    
    def fire(self, angle):
        if len(self.bullets) >= self.max_bullet:
            self.bullets.pop(0)
        self.bullets.append(Bullet(angle, self.get_position()[0], self.get_position()[1], BulletCollisionHandler()))

class Enemy(Collidable):
    # start할 때 생성되고 바닥이랑 충돌 체크해야 하는 Collidable 객체
    size = 100
    
    def __init__(self, angle, point_x, point_y, coll_handler):
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        self.coll_handler = coll_handler
    
    def update_position(self):
        self.point_y += self.speed
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    def is_collide_at(self, object):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = object.get_position()
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1:
            self.coll_handler.collide_occur(self)

class GameFrame(Visible, ABC):
    # GameObject들이 등장하는 게임 화면 크기를 정의한 객체
    width = 0
    height = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    @abstractmethod
    def get_position(self):
        pass

class Bottom(GameFrame):
    @classmethod
    def get_position(self):
        return 0, 0, self.width, 0
    
class LeftWalls(GameFrame):
    def get_position(self):
        return 0, 0, 0, self.height

class RightWalls(GameFrame):
    def get_position(self):
        return self.width, 0, self.width, self.height

class PlayerStatus(GameObject):
    # User Info 관리 - DB에 저장 필요
    def __init__(self):
        self.score = 0
        self.life = 3

    def update_score(self):
        self.score += 1
    
    def lose_life(self):
        self.life -= 1
        
    def is_game_over(self):
        return self.life <= 0

class VisibleObjectCreater(ABC):
    # Visible한 객체를 생성하는 추상 팩토리
    @abstractmethod
    def create_object(self):
        pass

class EnemyObjectCreater(VisibleObjectCreater):
    # Visible한 Enemy 객체를 생성하는 추상 팩토리
    SPAWN_POS = [50, 150, 250, 350, 450]

    def create_object(self):
        return Enemy(0, random.choice(self.SPAWN_POS), 0, EnemyCollisionHandler())

class GunObjectCreater(VisibleObjectCreater):
    # Visible한 Gun 객체를 생성하는 팩토리
    def create_object(self):
        return Gun(Bottom.get_position()[2]//2, 0)

class CollisionHandler(ABC):
    # 충돌 처리를 관리하는 객체 
    # 충돌 타입에 따라 PlayerStatus에게 요청
    def __init__(self):
        self.player_status = PlayerStatus()

    @abstractmethod
    def collide_occur(self, unit1, unit2=None):
        pass
    
class BulletCollisionHandler(CollisionHandler):
    # 총알 객체의 충돌 처리
    # 분기 오버로딩 처리

    @dispatch(Bullet, Enemy)
    def collide_occur(self, bullet, enemy):
        bullet.delete()
        enemy.delete()
        self.player_status.update_score()

    @dispatch(Bullet, GameFrame)
    def collide_occur(self, bullet):
        bullet.reflex()

class EnemyCollisionHandler(CollisionHandler):
    def collide_occur(self, enemy):
        enemy.delete()
        self.player_status.lose_life()
        
    def get_player_status(self):
        return self.player_status
