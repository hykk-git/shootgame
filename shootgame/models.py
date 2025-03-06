from django.db import models
import math
import random
from overrides import overrides

class GameObject:
    __name = models.CharField()

    @property
    def name(self):
        return self.name
    
    class Meta:
        abstract = True

class Visible(GameObject):
    __point_x = models.IntegerField()
    __point_y = models.IntegerField()
    __size = models.IntegerField()
    
    def point(self):
        return self.__point_x, self.__point_y
    
    # size 포함 본인 위치 반환
    def aabb(self):
        pass
    
    def update(self):
        # 자기 상태 화면에 업데이트(이동)
        pass

    class Meta:
        abstract = True

class Effect(GameObject):
    def activate(self):
        # 점수나 life, 반사 효과 활성화
        pass
    
    class Meta:
        abstract = True

class Collidable(Visible):
    # 충돌하는 객체들은 속도가 있음(움직임)
    __speed = models.IntegerField()
    
    def isCollision(self, unit):
        pass

    class Meta:
        abstract = True

class Gun(Visible):
    __max_bullet = models.IntegerField(default=3)

    @overrides
    def update(self):
        x, y = GameArea.point
        self.__point_x, self.__point_y = x//2, y
        self.save()
     
    def fire(self, angle):
        if Bullet.objects.count() >= self.max_bullet:
            Bullet.objects.last().delete()
        
        Bullet.create_bullet(angle)

class Bullet(Collidable):
    __angle = models.IntegerField()
    gun = models.ForeignKey(Gun)

    @classmethod
    def create_bullet(self, angle):
        return Bullet.objects.create(
            number=str(Bullet.objects.count()+1),
            __point_x=self.__width,
            __point_y=self.__height,
            __angle=angle
        )
    
    @overrides
    def aabb(self):
        return (
            self.__point_x,                 
            self.__point_y,                
            self.__point_x + self.size,    
            self.__point_y + self.size    
        )
    
    @overrides
    def isCollision(self, unit):
        x1, y1, x2, y2 = self.aabb()
        a1, b1, a2, b2 = unit.aabb() # 너의 위치도 알려줘

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1

    @overrides
    def update(self):
        x, y = self.__point_x, self.__point_y
        x += self._speed * math.sin(math.radians(self._angle))
        y -= self._speed * math.cos(math.radians(self._angle))
        self.save()
    
    def reflex(self):
        temp_angle = self.__angle
        self.__angle = -temp_angle

class Enemy(Collidable):
    spawn_pos = models.CharField()

    @classmethod
    def create_enemy(self):
        self.spawn_pos = [50, 150, 250, 350, 450]

        return Enemy.objects.create(
            number=str(Bullet.objects.count()+1),
            __point_x=random.choice(self.spawn_pos),
            __point_y=self.__height
        )
    
    @overrides
    def aabb(self):
        return (
            self.__point_x,                 
            self.__point_y,                
            self.__point_x + self.size,    
            self.__point_y + self.size    
        )
    
    @overrides
    def isCollision(self, unit):
        x1, y1, x2, y2 = self.aabb()
        a1, b1, a2, b2 = unit.aabb() # 너의 위치도 알려줘

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1

        # view에 가서 isColl->effect 호출

    @overrides
    def update(self):
        self.__point_y += self.__speed
        self.save()

class GameArea(Visible):
    __height = models.IntegerField(default=800) 
    __width = models.IntegerField(default=600)

    @property
    def frame_size(self):
        return self.__height, self.__width
    
    class Meta:
        abstract = True

class LeftWall(GameArea):
    @overrides
    def aabb(self):
        return (
            0,                                 
            0,    
            0,
            self.__height
        )
    
    def update(self):
        self.__point_x, self.__point_y = 0, self.__height
        self.save()

class RightWall(GameArea):
    @overrides
    def aabb(self):
        return (
            self.__width,                                 
            0,    
            self.__width,
            self.__height
        )
    
    @overrides
    def update(self):
        self.__point_x, self.__point_y = self.__width, self.__height
        self.save()

class Bottom(GameArea):
    @overrides
    def aabb(self):
        return (
            0,                                 
            0,    
            self.__width,
            0
        )
    
    @overrides
    def update(self):
        self.__point_x, self.__point_y = self.__width, 0
        self.save()

class Reflex(Effect):
    # 충돌시 반사해라

    @overrides
    def activate(self, unit):
        unit.reflex()

class Score(Effect):
    __current_status = models.IntegerField(default=0)

    @property
    def status(self):
        return self.__current_status
    
    @overrides
    def activate(self):
        self.status += 1

class Life(Effect):
    __current_status = models.IntegerField(default=0)

    @property
    def status(self):
        return self.__current_status

    @overrides
    def activate(self):
        self.status -= 1