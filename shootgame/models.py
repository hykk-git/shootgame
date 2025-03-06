from django.db import models
import math
import random
from overrides import overrides

class GameObject(models.Model):
    name = models.CharField()

    @property
    def name(self):
        return self.name
    
    class Meta:
        abstract = True

class Visible(GameObject):
    point_x = models.IntegerField()
    point_y = models.IntegerField()
    size = models.IntegerField()
    
    def point(self):
        return self.point_x, self.point_y
    
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
    speed = models.IntegerField()
    
    def isCollision(self, unit):
        pass

    class Meta:
        abstract = True

class Gun(Visible):
    max_bullet = models.IntegerField(default=3)

    @overrides
    def update(self):
        x, y = Bottom.point
        self.point_x, self.point_y = x//2, y
        self.save()
     
    def fire(self, angle):
        if Bullet.objects.count() >= self.max_bullet:
            Bullet.objects.last().delete()
        
        Bullet.create_bullet(angle)

class Bullet(Collidable):
    angle = models.IntegerField()
    gun = models.ForeignKey("Gun", on_delete=models.CASCADE)

    @classmethod
    def create_bullet(self, angle):
        return Bullet.objects.create(
            number=str(Bullet.objects.count()+1),
            point_x=self.width,
            point_y=self.height,
            angle=angle
        )
    
    @overrides
    def aabb(self):
        return (
            self.point_x,                 
            self.point_y,                
            self.point_x + self.size,    
            self.point_y + self.size    
        )
    
    @overrides
    def isCollision(self, unit):
        x1, y1, x2, y2 = self.aabb()
        a1, b1, a2, b2 = unit.aabb() # 너의 위치도 알려줘

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1

    @overrides
    def update(self):
        x, y = self.point_x, self.point_y
        x += self.speed * math.sin(math.radians(self.angle))
        y -= self.speed * math.cos(math.radians(self.angle))
        self.save()
    
    def reflex(self):
        temp_angle = self.angle
        self.angle = -temp_angle

class Enemy(Collidable):
    spawn_pos = models.CharField(max_length=50)

    @classmethod
    def create_enemy(self):
        self.spawn_pos = [50, 150, 250, 350, 450]

        return Enemy.objects.create(
            number=str(Bullet.objects.count()+1),
            point_x=random.choice(self.spawn_pos),
            point_y=self.height
        )
    
    @overrides
    def aabb(self):
        return (
            self.point_x,                 
            self.point_y,                
            self.point_x + self.size,    
            self.point_y + self.size    
        )
    
    @overrides
    def isCollision(self, unit):
        x1, y1, x2, y2 = self.aabb()
        a1, b1, a2, b2 = unit.aabb() # 너의 위치도 알려줘

        return x2<=a1 and y2<=b1 and a2<=x1 and b2<=y1

        # view에 가서 isColl->effect 호출

    @overrides
    def update(self):
        self.point_y += self.speed
        self.save()

class GameArea(Visible):
    # 게임 영역을 나타내는 객체
    height = models.IntegerField(default=800)
    width = models.IntegerField(default=600)
    
    @property
    def frame_size(self):
        return self.height, self.width
    
    @overrides
    def aabb(self):
        return (
            0,                                 
            0,    
            0,
            self.height
        )
    
    def update(self):
        self.point_x, self.point_y = 0, self.height
        self.save()

class Score(Effect):
    current_status = models.IntegerField(default=0)

    @property
    def status(self):
        return self.current_status
    
    @overrides
    def activate(self):
        self.status += 1

class Life(Effect):
    current_status = models.IntegerField(default=0)

    @property
    def status(self):
        return self.current_status

    @overrides
    def activate(self):
        self.status -= 1