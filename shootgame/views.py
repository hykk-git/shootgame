from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import random
import math

from .models import (
    Gun, Bullet, Enemy, GameArea, LeftWall, RightWall, Bottom, 
    Reflex, Score, Life
)

def index(request):
    return render(request, 'game/index.html')

@method_decorator(csrf_exempt, name='dispatch')
class FrameView(View):
    def get(self, request):
        game_area = GameArea()
        height, width = game_area.frame_size
        
        score_obj = Score.objects.first()
        life_obj = Life.objects.first()
        
        if not score_obj:
            score_obj = Score.objects.create()
        
        if not life_obj:
            life_obj = Life.objects.create()
        
        context = {
            'height': height,
            'width': width,
            'score': score_obj.status,
            'life': life_obj.status
        }
        
        return JsonResponse(context)

@method_decorator(csrf_exempt, name='dispatch')
class SpawnView(View):
    def post(self, request):
        data = json.loads(request.body)
        spawn_type = data.get('type')
        
        if spawn_type == 'enemy':
            angle = random.randint(0, 360)
            enemy = Enemy.create_enemy(angle)
            
            return JsonResponse({
                'success': True,
                'enemy_id': enemy.id,
                'position': enemy.point()
            })
            
        elif spawn_type == 'gun':
            gun, created = Gun.objects.get_or_create(
                pk=1,
                defaults={'name': 'player_gun', 'max_bullet': 3}
            )
            gun.update()
            
            return JsonResponse({
                'success': True,
                'gun_id': gun.id,
                'position': gun.point()
            })
        
        return JsonResponse({'success': False, 'error': '잘못된 객체 유형'})

@method_decorator(csrf_exempt, name='dispatch')
class FireView(View):
    def post(self, request):
        data = json.loads(request.body)
        angle = data.get('angle', 90)
        
        gun = Gun.objects.first()
        if not gun:
            return JsonResponse({'success': False, 'error': '총 객체가 없습니다'})
        
        gun.fire(angle)
        
        return JsonResponse({
            'success': True,
            'message': f'{angle}도 각도로 발사 완료'
        })

@method_decorator(csrf_exempt, name='dispatch')
class GameUpdateView(View):
    def get(self, request):
        left_wall = LeftWall.objects.first()
        right_wall = RightWall.objects.first()
        bottom = Bottom.objects.first()
    
        score = Score.objects.first() or Score.objects.create()
        life = Life.objects.first() or Life.objects.create()
        
        gun = Gun.objects.first()
        gun.update()
        
        left_wall.update()
        right_wall.update()
        bottom.update()
        
        collisions = []
        bullets_to_delete = set()
        enemies_to_delete = set()
        
        bullets = Bullet.objects.all()
        enemies = Enemy.objects.all()
        
        for bullet in bullets:
            bullet.update()
            
            for enemy in enemies:
                if bullet.isCollision(enemy) and enemy.id not in enemies_to_delete and bullet.id not in bullets_to_delete:
                    score.activate()
                    
                    collisions.append({
                        'type': 'bullet_enemy',
                        'bullet_id': bullet.id,
                        'enemy_id': enemy.id
                    })
                    
                    bullets_to_delete.add(bullet.id)
                    enemies_to_delete.add(enemy.id)
                    break
            
            if left_wall and bullet.isCollision(left_wall):
                reflex = Reflex()
                reflex.activate(bullet)
                
                collisions.append({
                    'type': 'bullet_wall',
                    'bullet_id': bullet.id,
                    'wall': 'left'
                })
            
            if right_wall and bullet.isCollision(right_wall):
                reflex = Reflex()
                reflex.activate(bullet)
                
                collisions.append({
                    'type': 'bullet_wall',
                    'bullet_id': bullet.id,
                    'wall': 'right'
                })

        for enemy in enemies:
            if enemy.id in enemies_to_delete:
                continue

            enemy.update()

            if bottom and enemy.isCollision(bottom):
                life.activate()
                
                collisions.append({
                    'type': 'enemy_bottom',
                    'enemy_id': enemy.id
                })
                
                enemies_to_delete.add(enemy.id)
        
        for bullet_id in bullets_to_delete:
            Bullet.objects.filter(id=bullet_id).delete()
            
        for enemy_id in enemies_to_delete:
            Enemy.objects.filter(id=enemy_id).delete()
        
        return JsonResponse({
            'success': True,
            'bullets': [{'id': b.id, 'position': b.point()} for b in Bullet.objects.all() if b.id not in bullets_to_delete],
            'enemies': [{'id': e.id, 'position': e.point()} for e in Enemy.objects.all() if e.id not in enemies_to_delete],
            'gun': {'position': gun.point() if gun else None},
            'collisions': collisions,
            'score': score.status,
            'life': life.status
        })