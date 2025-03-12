import math
from abc import ABC, abstractmethod
import random

class GameObject:
    def __init__(self, position_creator):
        self.position_creator = position_creator

class ShootingGame:
    def __init__(self, position_creator, position_updater):
        self.position_creator = position_creator
        self.position_updater = position_updater
        self.obj = None  # 객체 생성 시 position_creator 활용

    def start(self):
        # PositionCreater를 통해 객체 생성
        self.obj = self.position_creator.create_object("GameObject")

    def player_input(self, gun):
        # 총이 발사되면 PositionUpdater를 통해 총알을 받음
        gun.fire(self.position_updater)

    def update_game(self):
        self.position_updater.update()

class Visible(GameObject, ABC):
    def __init__(self, point_x, point_y, size, position_creator):
        super().__init__(position_creator)
        self.point_x = point_x
        self.point_y = point_y
        self.size = size

    @abstractmethod
    def get_position(self):
        pass

class Movable(Visible, ABC):
    speed = 0
    angle = 0

    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable, ABC):
    def __init__(self, angle, point_x, point_y, speed, size, coll_handler, position_creator):
        super().__init__(point_x, point_y, size, position_creator)
        self.angle = angle
        self.speed = speed
        self.coll_handler = coll_handler

    def is_collide_at(self, unit):
        pass

class Bullet(Collidable):
    def __init__(self, angle, point_x, point_y, speed, size, coll_handler, position_creator):
        super().__init__(angle, point_x, point_y, speed, size, coll_handler, position_creator)

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
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1:
            self.coll_handler.collide_occur(self, unit)

class Gun(Visible):
    def __init__(self, position_creator):
        super().__init__(GameFrame.frame_size[0]//2, GameFrame.frame_size[1], 10, position_creator)
        self.max_bullet = 3
        self.bullets = []

    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    def fire(self, position_updater):
        if len(self.bullets) >= self.max_bullet:
            self.bullets.pop(0)
        bullet = position_updater.create_bullet(self.point_x, self.point_y)
        self.bullets.append(bullet)

class Enemy(Collidable):
    def __init__(self, angle, point_x, point_y, speed, size, position_creator):
        super().__init__(angle, point_x, point_y, speed, size, None, position_creator)

    def update_position(self):
        self.point_y += self.speed

    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

class GameFrame(Visible):
    frame_size = (600, 800)

    def __init__(self, position_creator):
        super().__init__(0, 0, GameFrame.frame_size[0], position_creator)

    def get_position(self):
        return 0, 0, self.width, self.height

class PlayerStatus(GameObject):
    def __init__(self, position_creator, score=0, life=3):
        super().__init__(position_creator)
        self.score = score
        self.life = life

    def update_score(self):
        self.score += 1

    def lose_life(self):
        self.life -= 1

class CollisionHandler(ABC):
    def __init__(self, position_creator):
        self.player_status = PlayerStatus(position_creator)

    @abstractmethod
    def collide_occur(self, unit1, unit2):
        pass

class BulletCollisionHandler(CollisionHandler):
    def collide_occur(self, bullet, enemy):
        bullet.delete()
        enemy.delete()
        self.player_status.update_score()

    def collide_occur(self, bullet, game_frame):
        bullet.reflex()

class EnemyCollisionHandler(CollisionHandler):
    def collide_occur(self, enemy, game_frame):
        enemy.delete()
        self.player_status.lose_life()

class PositionCreater:
    SPAWN_POS = [50, 150, 250, 350, 450]

    def create_object(self, obj_type):
        if obj_type == "Bullet":
            return Bullet(0, 300, 700, 5, 10, None, self)
        elif obj_type == "Enemy":
            return Enemy(random.choice([0, 180]), random.choice(self.SPAWN_POS), 0, 2, 20, self)
        elif obj_type == "Gun":
            return Gun(self)
        elif obj_type == "GameFrame":
            return GameFrame(self)
        elif obj_type == "PlayerStatus":
            return PlayerStatus(self)

class PositionUpdater:
    def __init__(self):
        self.pk = PositionCreater()
        self.bullets = []
        self.enemies = []

    def update(self):
        for bullet in self.bullets[:]:
            bullet.update_position()

        for enemy in self.enemies[:]:
            enemy.update_position()

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                bullet.is_collide_at(enemy)
            bullet.is_collide_at(GameFrame(self.pk))

        for enemy in self.enemies[:]:
            enemy.is_collide_at(GameFrame(self.pk))

    def create_bullet(self, x, y):
        bullet = self.pk.create_object("Bullet")
        bullet.point_x = x
        bullet.point_y = y
        self.bullets.append(bullet)
        return bullet

    def create_enemy(self):
        enemy = self.pk.create_object("Enemy")
        self.enemies.append(enemy)
        return enemy

if __name__ == "__main__":
    position_creator = PositionCreater()
    position_updater = PositionUpdater()
    game = ShootingGame(position_creator, position_updater)
    game.start()
