import math
from abc import * 
from multipledispatch import dispatch
import random
import time
import threading

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
        # 현재 객체의 위치를 영역으로 반환하는 함수
        # 충돌 확인할 때 쓰임- 인자 순서가 x1, y1, x2, y2
        pass

class Movable(Visible, ABC):
    # 화면에 보이는 객체 중 움직이는 객체-> 속도(속력+방향) 갖고 있음
    size = 0
    speed = 0

    def __init__(self, angle, point_x, point_y):
        # 어떤 각도로 움직일지는 외부에서 지정 필요
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        
    # 움직임을 갱신하는 함수: 반환값 없이 좌표 상태 변경
    @abstractmethod
    def update_position(self):
        pass

class Collidable(Movable, ABC):
    # 충돌시 이벤트가 발생하는 객체-> 누구랑 충돌했는지 확인해야 함
    speed = 20
    size = 20

    def __init__(self, angle, point_x, point_y, coll_handler):
        # 내부에 충돌 처리 관리 객체 coll_handler를 가짐
        self.angle = angle
        self.point_x = point_x
        self.point_y = point_y
        self.coll_handler = coll_handler 

    # 충돌을 확인하는 함수. 인자로 객체를 받고, 충돌했다면 자신과 그 객체를 반환
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
    
    # 반사되어 튕기는 기능
    def reflex(self):
        self.angle = -self.angle
    
    def get_position(self):
        return self.point_x, self.point_y, self.point_x + self.size, self.point_y + self.size

    # object와 충돌했냐고 물어보면, 충돌했다고 알리며 자신과 충돌한 객체를 반환
    def is_collide_at(self, object):
        x1, y1, x2, y2 = self.get_position()
        a1, b1, a2, b2 = object.get_position()
        
        if x2 >= a1 and y2 >= b1 and a2 >= x1 and b2 >= y1:
            # 충돌 관리자에게 알림
            self.coll_handler.collide_occur(self, object)
            print("bullet 충돌")

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
        print(f"Bullet {angle}도로 발사됨")

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
            print("enemy 충돌")

class GameFrame(Visible, ABC):
    # GameObject들이 등장하는 게임 화면 크기를 정의한 객체
    width = 0
    height = 0

    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    # 충돌 처리를 위해 위치를 선이 아닌 영역으로 반환
    @abstractmethod
    def get_position(self):
        # 순서: x1, y1, x2, y2
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
        # 초기값
        self.score = 0
        self.life = 3

    def update_score(self):
        # 플레이어 점수를 1씩 업데이트
        self.score += 1
        print(f"현재 점수: {self.score}")
    
    def lose_life(self):
        # 플레이어 생명을 1씩 깎음
        self.life -= 1
        print(f"남은 생명: {self.life}")
        
    def get_life(self):
        # 게임 종료 조건 판단에 사용
        return self.life
    
    def get_score(self):
        # 현재 점수 프레임 밖에 띄우는 데 사용
        return self.score

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

class PositionUpdater:
    # Movable 타입 객체 위치를 틱당 업데이트하는 객체
    
    # bullet, enemy 리스트를 받아서 위치 업데이트하는 함수
    @dispatch(list)
    def update_object_position(self, objects):
        for obj in objects:
            obj.update_position()

    @dispatch(GameObject)
    def update_object_position(self, obj):
        obj.update_position()
    
    # 바뀐 위치에 대해 충돌이 일어났는지 확인하는 함수: 분리 필요
    @dispatch(list, list)
    def update_object_collision(self, moving_objects, collided_objects):
        for moved in moving_objects:
            for attacked in collided_objects:
                moved.is_collide_at(attacked)

    @dispatch(list, Visible)  
    def update_object_collision(self, objects, visible):
        for object in objects:
            object.is_collide_at(visible)

class PlayerInputHandler(ABC):
    # 콘솔로 받은 input이 의미하는 구체적인 동작을 실행하게 하는 추상 클래스
    @abstractmethod
    def handle_input(self, controller, *args): 
        pass

class FireHandler(PlayerInputHandler):
    # 총알 발사-> Gun에 angle을 지정해 발사하도록 함
    def __init__(self, gun):
        self.gun = gun

    def handle_input(self, controller, *args):
        angle = int(args[0])
        self.gun.fire(angle)

class GameOverHandler(PlayerInputHandler):
    def handle_input(self, controller, *args):
        print("Game Over")
        controller.stop()

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
        print("score를 얻음!")

    @dispatch(Bullet, GameFrame)
    def collide_occur(self, bullet):
        bullet.reflex()
        print("bullet 반사됨")

class EnemyCollisionHandler(CollisionHandler):
    def collide_occur(self, enemy):
        enemy.delete()
        self.player_status.lose_life()
        print("life 깎임")

# 콘솔 input을 반복해서 받기 위한 클래스
class GameLoopController:
    def __init__(self, input_processor, game_updater, enemy_spawner):
        self.input_processor = input_processor
        self.game_updater = game_updater
        self.enemy_spawner = enemy_spawner
        self.running = True
        
    def start(self):
        threading.Thread(target=self.enemy_spawner.start_spawning, daemon=True).start()
        
        # 메인 게임 루프
        while self.running:
            user_input = input("> ")
            self.input_processor.process_input(user_input, self)
            time.sleep(1)
            self.game_updater.update()
            
            # 종료조건: life가 0이 될 때
            if self.game_updater.check_game_over():
                self.stop()
                print("Game Over")
            
    def stop(self):
        self.running = False
        self.enemy_spawner.stop()

# 사용자 콘솔 입력 토큰 단위로 받아 넘겨주는 클래스
class InputProcessor:
    def __init__(self, handlers):
        self.handlers = handlers
    
    def process_input(self, user_input, controller):
        tokens = user_input.strip().lower().split()
        if not tokens:
            return
            
        command = tokens[0]
        args = tokens[1:]
        
        if command in self.handlers:
            self.handlers[command].handle_input(controller, *args)

# 게임 상태(이동) 업데이트
class GameUpdater:
    def __init__(self, position_updater, gun, enemy_spawner):
        self.position_updater = position_updater
        self.gun = gun
        self.enemy_spawner = enemy_spawner
        
        self.bottom = Bottom(800, 600)  
        self.left_wall = LeftWalls(800, 600)
        self.right_wall = RightWalls(800, 600)
        
        # 플레이어 상태 참조 (충돌 핸들러로부터)
        enemy = self.enemy_spawner.enemy_creator.create_object()
        self.player_status = enemy.coll_handler.player_status
    
    def update(self):
        # 각 오브젝트 위치 업데이트
        bullets = self.gun.get_bullets()
        enemies = self.enemy_spawner.get_enemies()
        
        self.position_updater.update_object_position(bullets)
        self.position_updater.update_object_position(enemies)

        # 바뀐 위치가 충돌이 일어난 곳인지
        self.position_updater.update_object_collision(bullets, enemies)
        self.position_updater.update_object_collision(bullets, self.left_wall)
        self.position_updater.update_object_collision(bullets, self.right_wall) 
        self.position_updater.update_object_collision(enemies, self.bottom) 

# Enemy 틱당 반복 생성
class EnemySpawner:
    def __init__(self, enemy_creator):
        self.enemy_creator = enemy_creator
        self.enemies = []
        self.running = True
    
    def start_spawning(self):
        while self.running:
            time.sleep(random.uniform(2, 5))

            # enemy 공장으로부터 받아 옴
            enemy = self.enemy_creator.create_object()

            self.enemies.append(enemy)
            print(f"Enemy 생성됨")
    
    def get_enemies(self):
        return self.enemies
        
    def stop(self):
        self.running = False

class ShootingGame:
    def __init__(self):
        self.gun = GunObjectCreater().create_object()
        self.enemy_creator = EnemyObjectCreater()
        self.position_updater = PositionUpdater()
        
        self.enemy_spawner = EnemySpawner(self.enemy_creator)

        self.handlers = {
            "fire": FireHandler(self.gun),
            "gameover": GameOverHandler()
        }
        
        self.input_processor = InputProcessor(self.handlers)
        self.game_updater = GameUpdater(self.position_updater, self.gun, self.enemy_spawner)
        self.game_loop = GameLoopController(self.input_processor, self.game_updater, self.enemy_spawner)
    
    def start(self):
        self.game_loop.start()

if __name__ == "__main__":
    game = ShootingGame()
    game.start()