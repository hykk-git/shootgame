import math
from abc import * 
from multipledispatch import dispatch
import random
import time
from out_module import *

class CollisionHandler(ABC):
    # 충돌 처리를 관리하는 객체 
    # 충돌 타입에 따라 PlayerStatus에게 요청
    player_status = PlayerStatus()

    @abstractmethod
    def collide_occur(self, unit1, unit2):
        pass

class BulletCollisionHandler(CollisionHandler):
    # 총알 객체의 충돌 처리
    # 분기 오버로딩 처리

    @dispatch(Bullet, Enemy)
    def collide_occur(self, bullet, enemy):
        bullet.delete()
        enemy.delete()
        self.ps.update_score()

    @dispatch(Bullet, GameFrame)
    def collide_occur(self, bullet):
        bullet.reflex()

class EnemyCollisionHandler(CollisionHandler):
    def collide_occur(self, enemy, GameFrame):
        enemy.delete()
        self.ps.lose_life()

class VisibleObjectCreater(ABC):
    def create_object(self):
        pass

class EnemyObjectCreater(VisibleObjectCreater):
    SPAWN_POS = [50, 150, 250, 350, 450]

    def create_object(self):
        return Enemy(random.choice(self.SPAWN_POS), 0, 20, 0, 100, EnemyCollisionHandler)

class GunObjectCreater(VisibleObjectCreater):
    def create_object(self):
        return Gun(GameFrame.frame_size[0]//2, GameFrame.frame_size[1])

class PositionUpdater:
    # Movable 타입 객체 위치를 틱당 업데이트하는 객체
    def update_object_position(self, unit):
        for bullet in self.bullets[:]:
            bullet.update_position()
            
        for enemy in self.enemies[:]:
            enemy.update_position()
        
        for bullet in self.bullets[:]:
            bullet.is_collide_at(enemy)
            bullet.is_collide_at(LeftWalls)
            bullet.is_collide_at(RightWalls)
        
        for enemy in self.enemies[:]:
            enemy.is_collide_at(Bottom)