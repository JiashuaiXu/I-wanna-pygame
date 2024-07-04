import sys
import pygame
from scripts.sprites import PlayerSprite, SpikeManage, BlockManage
from scripts.tilemap import TileMap
from scripts.utils import load_image, load_images, load_images_to_dict, load_sound

SIZE = (800, 608)
FPS = 60

class Game:
    def __init__(self, size: tuple[int, int], fps: int):
        pygame.init()
        pygame.display.set_caption('mygame')
        pygame.display.set_icon(pygame.image.load('data/images/fruit32.ico'))

        self.size = size
        self.fps = fps
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.time = 0

        self.assets = {
            'maskPlayer': load_image('player/maskPlayer.png'),
            'player/idle': load_images('player/idle'),
            'player/fall': load_images('player/fall'),
            'player/jump': load_images('player/jump'),
            'player/run': load_images('player/run'),
            'bullet': load_images('bullet'),
            'game_over': load_image('GAMEOVER.png'),    
            'spike': load_image('spike_up.png'),
            # 'spike_up': load_image('spike_up.png'),
            'blood': load_images('blood'),
            'block': load_images_to_dict('block'),
            'portal': load_image('protal-48.png'),

        }

        self.sfx = {
            'jump': load_sound('sndJump.wav'),
            'djump': load_sound('sndDjump.wav'),
            'shoot': load_sound('sndShoot.wav')
        }

        self.levels = ['title', 'level1', 'level2', 'level3']  # 定义关卡ID列表
        self.current_level_index = 0  # 当前关卡索引
        self.tilemap = None
        self.block_manage = None
        self.spike_manage = None
        self.player = None
        self.portal_pos = None  # 通关入口位置

    def reset_game(self):
        print("Resetting the game to initial state.")
        self.current_level_index = 0  # 假设游戏的初始关卡索引为0
        self.load_level(self.levels[self.current_level_index])
        # 在这里添加任何其他必要的状态重置代码，例如重置分数，玩家生命值等

    def load_level(self, map_id):
        self.tilemap = TileMap(self)  # 初始化 tilemap
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.block_manage = BlockManage(self)
        for block in self.tilemap.extract('block', True):
            self.block_manage.create(block['variant'], block['pos'], block['flip'])

        self.spike_manage = SpikeManage(self)
        for spike in self.tilemap.extract('spike'):
            self.spike_manage.create(spike['pos'], spike['flip'])

        if self.tilemap.map_type == 'normal':
            self.player = PlayerSprite(self, self.tilemap.player_pos)
            self.portal_pos = self.tilemap.portal_pos  # 读取 portal 的位置
        else:
            self.player = None  # 如果不是 normal 类型的地图，将 player 设为 None
            self.portal_pos = None  # 重置 portal 位置


    def switch_level(self):
        self.current_level_index = (self.current_level_index + 1) % len(self.levels)
        print(f"Switching to level {self.current_level_index}: {self.levels[self.current_level_index]}")
        self.load_level(self.levels[self.current_level_index])

    def reset_level(self):
        self.current_level_index = 0
        print(f"Resetting to level {self.current_level_index}: {self.levels[self.current_level_index]}")
        self.load_level(self.levels[self.current_level_index])

    def stop(self):
        pygame.quit()
        sys.exit()

    # def check_portal(self):
    #     if self.player is not None and self.portal_pos is not None:
    #         try:
    #             portal_position = self.portal_pos['pos']
    #             player_rect = self.player.rect
    #             portal_rect = pygame.Rect(portal_position[0] * self.tilemap.tile_size, 
    #                                     portal_position[1] * self.tilemap.tile_size, 
    #                                     self.tilemap.tile_size, 
    #                                     self.tilemap.tile_size)
    #             if player_rect.colliderect(portal_rect):
    #                 self.switch_level()  # 切换到下一个关卡
    #         except KeyError:
    #             print("Portal position key error.")
    # def check_portal(self):
    #     if self.player is not None and self.portal_pos is not None:
    #         # 直接使用解包的方式获取坐标值
    #         portal_x, portal_y = self.portal_pos
    #         player_rect = self.player.rect
    #         portal_rect = pygame.Rect(portal_x * self.tilemap.tile_size, 
    #                                 portal_y * self.tilemap.tile_size, 
    #                                 self.tilemap.tile_size, 
    #                                 self.tilemap.tile_size)
    #         if player_rect.colliderect(portal_rect):
    #             self.switch_level()  # 切换到下一个关卡

    def check_portal(self):
        if self.player is not None and self.portal_pos is not None:
            # 使用解包的方式获取坐标值，并检查是否为 None
            portal_x, portal_y = self.portal_pos
            if portal_x is None or portal_y is None:
                print("Portal position is not correctly set.")
                return  # 如果坐标不完整，直接返回，不执行下面的代码

            player_rect = self.player.rect
            portal_rect = pygame.Rect(portal_x * self.tilemap.tile_size, 
                                    portal_y * self.tilemap.tile_size, 
                                    self.tilemap.tile_size, 
                                    self.tilemap.tile_size)
            if player_rect.colliderect(portal_rect):
                self.switch_level()  # 切换到下一个关卡


    def check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                print(f"Key down: {pygame.key.name(event.key)}")  # 打印所有按下的键
                if event.key == pygame.K_ESCAPE:
                    self.stop()
                elif event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_q and self.player is not None:
                    self.player.die()
                elif event.key == pygame.K_z and self.player is not None:
                    self.player.shoot()
                elif event.key == pygame.K_SPACE and self.player is not None:
                    self.player.jump()
                elif event.key == pygame.K_RSHIFT:
                    self.switch_level()
                elif event.key == pygame.K_BACKSPACE:
                    print("Backspace key pressed for resetting the game.")
                    self.reset_game()  # 重置游戏
            elif event.type is pygame.KEYUP:
                print(f"Key up: {pygame.key.name(event.key)}")  # 打印所有释放的键
                if event.key == pygame.K_SPACE and self.player is not None:
                    self.player.vjump()

    # def run(self):
    #     self.time = 0
    #     self.tilemap = TileMap(self)

    #     self.load_level(self.levels[self.current_level_index])  # Load the initial level

    #     pygame.mixer.music.load('data/sounds/bgm2014.ogg')
    #     pygame.mixer.music.set_volume(0.5)
    #     pygame.mixer.music.play(-1)
    #     while True:
    #         self.time += 1
    #         self.check_event()

    #         self.screen.fill(self.tilemap.background)
    #         self.spike_manage.update()
    #         self.block_manage.update()
    #         if self.player is not None:
    #             self.player.update()
    #             self.check_portal()  # Check if the player has reached the portal

    #         # Render the portal image
    #         if self.portal_pos is not None:
    #             portal_image = self.assets['portal']
    #             # Correctly accessing the tuple indices
    #             self.screen.blit(portal_image, 
    #                             (self.portal_pos[0] * self.tilemap.tile_size, 
    #                             self.portal_pos[1] * self.tilemap.tile_size))

    #         pygame.display.flip()
    #         self.clock.tick(self.fps)

    def run(self):
        self.time = 0
        self.tilemap = TileMap(self)
        self.load_level(self.levels[self.current_level_index])  # 加载初始关卡
        pygame.mixer.music.load('data/sounds/bgm2014.ogg')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        while True:
            self.time += 1
            self.check_event()

            self.screen.fill(self.tilemap.background)
            self.spike_manage.update()
            self.block_manage.update()
            if self.player is not None:
                self.player.update()
                self.check_portal()  # 检查玩家是否到达传送门

            # 如果 portal_pos 已正确定义，渲染传送门图像
            if self.portal_pos and None not in self.portal_pos:
                portal_image = self.assets['portal']
                self.screen.blit(portal_image, (self.portal_pos[0] * self.tilemap.tile_size, self.portal_pos[1] * self.tilemap.tile_size))

            pygame.display.flip()
            self.clock.tick(self.fps)

if __name__ == '__main__':
    Game(SIZE, FPS).run()
