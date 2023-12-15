import pygame
import sys
import traceback
from pygame.locals import *
from random import *
import bullet
import enemy
import myplane
import supply

# initialize pygame
pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('aircraft battle')

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# load background and music
background = pygame.image.load('image/background.png').convert()
pygame.mixer.music.load('sound/game_music.wav')
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound('sound/bullet.wav')
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound('sound/use_bomb.wav')
bomb_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
# 小型飞机毁灭音效
enemy1_down_sound = pygame.mixer.Sound("sound\\enemy0_down.wav")
enemy1_down_sound.set_volume(0.2)
# 中型飞机毁灭音效
enemy2_down_sound = pygame.mixer.Sound("sound\\enemy1_down.wav")
enemy2_down_sound.set_volume(0.2)
# 大型飞机毁灭音效
enemy3_down_sound = pygame.mixer.Sound("sound\\enemy2_down.wav")
enemy3_down_sound.set_volume(0.2)
# 大型飞机出场音效
enemy3_fly_sound = pygame.mixer.Sound("sound\\big_plane_flying.wav")
enemy3_fly_sound.set_volume(0.2)
me_down_sound = pygame.mixer.Sound("sound\\game_over.wav")
me_down_sound.set_volume(0.2)


def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_middle_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MiddleEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def increase_speed(target, increase):
    for each in target:
        each.speed += increase


def main():
    pygame.mixer.music.play(-1)

    # 生成我方飞机
    me = myplane.MyPlane(bg_size)

    enemies = pygame.sprite.Group()

    # 生成敌方小型飞机
    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, 15)
    # 生成敌方中型飞机
    middle_enemies = pygame.sprite.Group()
    add_middle_enemies(middle_enemies, enemies, 4)
    # 生成敌方大型飞机
    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, 2)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))
    clock = pygame.time.Clock()

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 8
    for i in range(BULLET2_NUM//2):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30, me.rect.centery)))
    clock = pygame.time.Clock()

    # 中弹图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    # 统计得分
    score = 0
    score_font = pygame.font.Font('font/font1.ttf', 36)

    # 标志是否暂停游戏
    pause = False
    pause_nor_image = pygame.image.load('image/game_pause_nor.png').convert_alpha()
    pause_pressed_image = pygame.image.load('image/game_pause_pressed.png').convert_alpha()
    resume_nor_image = pygame.image.load('image/game_resume_nor.png').convert_alpha()
    resume_pressed_image = pygame.image.load('image/game_resume_pressed.png').convert_alpha()
    pause_rec = pause_nor_image.get_rect()
    pause_rec.left, pause_rec.top = width - pause_rec.width - 10, 10
    pause_image = pause_nor_image

    # 设置难度级别
    level = 1

    # 全屏炸弹
    bomb_image = pygame.image.load('image/bomb.png').convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font('font/font1.ttf', 48)
    bomb_num = 3

    # 每30秒发放补给包
    bullet_supply = supply.BulletSupply(bg_size)
    bomb_supply = supply.BombSupply(bg_size)
    SUPPLY_TIME = USEREVENT
    # pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
    pygame.time.set_timer(SUPPLY_TIME, 15 * 1000)

    # 超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    # 标志是否使用超级子弹
    is_double_bullet = False

    # 接触无敌计时器
    INVINCIBLE_TIME = USEREVENT + 2

    # 生命数量
    life_image = pygame.image.load('image/icon.png').convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3

    # 阻止重复打开文件
    recorded = False
    # 切换图片
    switch_image = True
    running = True

    # 用于延迟
    delay = 100
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button ==1 and pause_rec.collidepoint(event.pos):
                    pause = not pause
                    if pause:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()

            elif event.type == MOUSEMOTION:
                if pause_rec.collidepoint(event.pos):
                    if pause:
                        pause_image = resume_pressed_image
                    else:
                        pause_image = pause_pressed_image
                else:
                    if pause:
                        pause_image = resume_nor_image
                    else:
                        pause_image = pause_nor_image
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False
            elif event.type == SUPPLY_TIME:
                if choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()
            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)
            elif event.type == INVINCIBLE_TIME:
                me.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)

        # 根据用户得分增加难度
        if level == 1 and score > 50000:
            level = 2
            # 增加3架小型敌机 2型中型 1架大型
            add_small_enemies(small_enemies, enemies, 3)
            add_middle_enemies(middle_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升速度
            increase_speed(small_enemies, 1)
        elif level == 2 and score > 300000:
            level = 3
            # 增加5架小型敌机 3型中型 2架大型
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            # 增加5架小型敌机 3型中型 2架大型
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            # 增加5架小型敌机 3型中型 2架大型
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)

        screen.blit(background, (0, 0))

        if life_num and not pause:
            # 检测键盘操作
            key_pressed = pygame.key.get_pressed()

            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()

            # 绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            # 绘制超级子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000)
                    bullet_supply.active = False

            # 发射子弹
            if not (delay % 10):
                bullet_sound.play()
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx - 33, me.rect.centery))
                    bullets[bullet2_index + 1].reset((me.rect.centerx + 30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullet1[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM
            # 检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemies_hit:
                        b.active = False
                        for e in enemies_hit:
                            if e in middle_enemies or e in big_enemies:
                                e.hit = True
                                e.energy -= 1
                                if e.energy == 0:
                                    e.active = False
                            else:
                                e.active = False
            # 绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()
                    # 绘制被打中的画面
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)
                    # 即将出现，播放音效
                    if each.rect.bottom == -50:
                        enemy3_fly_sound.play(-1)
                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    # 大于20% 显示绿色，否则红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width * energy_remain,
                                      each.rect.top - 5),
                                     2)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e3_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index+1) % 6
                        if e3_destroy_index == 0:
                            enemy3_fly_sound.stop()
                            score += 10000
                            each.reset()
            # 绘制小型敌机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index+1) % 4
                        if e1_destroy_index == 0:
                            score += 1000
                            each.reset()
            # 绘制中型敌机
            for each in middle_enemies:
                if each.active:
                    each.move()
                    # 绘制被打中的画面
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)
                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.right, each.rect.top - 5),
                                     2)
                    # 大于20% 显示绿色，否则红色
                    energy_remain = each.energy / enemy.MiddleEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + each.rect.width * energy_remain,
                                      each.rect.top - 5),
                                     2)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6000
                            each.reset()
            # 检测我方飞机是否被撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:
                me.active = False
                for e in enemies_down:
                    e.active = False
            # 绘制我方飞机
            if me.active:
                if switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                if not (delay % 3):
                    if me_destroy_index == 0:
                        me_down_sound.play()
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        me.reset()
                        # 3秒无敌
                        pygame.time.set_timer(INVINCIBLE_TIME, 3 * 1000)

            # 绘制剩余炸弹数量
            bomb_text = bomb_font.render('x %d' % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height))

            # 绘制生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image,
                                (width-10-(i+1)*life_rect.width,
                                 height-10-life_rect.height))
            # 绘制分数
            score_text = score_font.render('Score : %s' % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))
        # 绘制游戏结束画面
        elif life_num == 0:
            # 背景音乐停止
            pygame.mixer.music.stop()

            # 停止所有音效
            pygame.mixer.stop()

            # 停止发放补给
            pygame.time.set_timer(SUPPLY_TIME, 0 )

            if not recorded:
                recorded = True
                # 读取历史最高分
                with open("record.txt","r") as f:
                    record_score = int(f.read())
                # 如果玩家高于最高分 则存档
                if score >record_score:
                    with open('record.txt', 'w') as f:
                        f.write(str(score))
            # 绘制结束画面
            game_over_font = pygame.font.Font('font/font1.ttf', 48)
            again_image = pygame.image.load('image/again.png').convert_alpha()
            again_rect = again_image.get_rect()
            game_over_image = pygame.image.load('image/game over.png')
            game_over_rect = game_over_image.get_rect()

            record_score_text = score_font.render('Best : %d' % record_score, True,WHITE)
            screen.blit(record_score_text, (50, 50))

            game_over_text1 = game_over_font.render('Your Score', True, WHITE)
            game_over_text1_rect = game_over_text1.get_rect()
            game_over_text1_rect.left, game_over_text1_rect.top = \
                (width - game_over_text1_rect.width) // 2, \
                    (height - game_over_text1_rect.height)//2
            screen.blit(game_over_text1, game_over_text1_rect)

            game_over_text2 = game_over_font.render('%d' % score, True, WHITE)
            game_over_text2_rect = game_over_text1.get_rect()
            game_over_text2_rect.left, game_over_text2_rect.top = \
                (width - game_over_text2_rect.width) // 2 + \
                game_over_text1_rect.width//4, \
                game_over_text1_rect.bottom + 10
            screen.blit(game_over_text2, game_over_text2_rect)


            again_rect.left, again_rect.top = \
                (width - again_rect.width) // 2,\
                game_over_text2_rect.bottom + 25
            screen.blit(again_image, again_rect)

            game_over_rect.left, game_over_rect.top = \
                (width - again_rect.width) // 2, \
                again_rect.bottom + 10
            screen.blit(game_over_image, game_over_rect)

            # 检测用户鼠标操作，如果按下左建
            if pygame.mouse.get_pressed()[0]:
                # 获取鼠标坐标
                pos = pygame.mouse.get_pos()
                # 如果点击重新开始
                if again_rect.left < pos[0] < again_rect.right and \
                    again_rect.top < pos[1] < again_rect.bottom:
                    # 重新开始
                    main()
                elif game_over_rect.left < pos[0] < game_over_rect.right and \
                    game_over_rect.top < pos[1] < game_over_rect.bottom:
                    pygame.quit()
                    sys.exit()

        # 绘制暂停按钮
        screen.blit(pause_image, pause_rec)

        # 5秒切换一次 飞机图片 让玩家看起来更流畅
        if not(delay % 5):
            switch_image = not switch_image

        delay -= 1
        if not delay:
            delay = 100
        # flip game
        pygame.display.flip()
        # set fps as 60
        clock.tick(60)


if __name__ == '__main__':
    # 避免游戏出错一闪而过
    try:
        main()
    except SystemExit:
        pass
    except Exception as e:
        traceback.print_exc()
        print(e)
        pygame.quit()
        input()
