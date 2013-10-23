import pygame, pypong
from pypong.player import BasicAIPlayer, KeyboardPlayer, MousePlayer
input_state = {'key': None, 'mouse': None}
    
def run(p1,p2,render=True,seed=None):
    global input_state
    configuration = {
        'screen_size': (686,488),
        'paddle_image': 'pong/assets/paddle.png',
        'paddle_left_position': 84.,
        'paddle_right_position': 594.,
        'paddle_velocity': 6.,
        'paddle_bounds': (0, 488), # This sets the upper and lower paddle boundary.The original game didn't allow the paddle to touch the edge, 
        'line_image': 'pong/assets/dividing-line.png',
        'ball_image': 'pong/assets/ball.png',
        'ball_velocity': 4.,
        'ball_velocity_bounce_multiplier': 1.105,
        'ball_velocity_max': 32.,
        'score_left_position': (141, 30),
        'score_right_position': (473, 30),
        'digit_image': 'pong/assets/digit_%i.png',
        'sound_missed': 'pong/assets/missed-ball.wav',
        'sound_paddle': 'pong/assets/bounce-paddle.wav',
        'sound_wall': 'pong/assets/bounce-wall.wav',
        'sound': True,
        'seed':seed,
        'render':render
    }

   
    pygame.init()
    if(render):
     pygame.mixer.pre_init(22050, -16, 2, 1024)
     display_surface = pygame.display.set_mode(configuration['screen_size'])
     output_surface = display_surface.copy().convert_alpha()
     output_surface.fill((0,0,0))
    debug_surface = None
    clock = pygame.time.Clock()

    input_state['key']=None
    input_state['mouse']=None

    # Prepare game
    #~ player_left = KeyboardPlayer(input_state, pygame.K_w, pygame.K_s)
    #player_right = MousePlayer(input_state)
    
    player_left = p1 #BasicAIPlayer()
    player_right = p2 #BasicAIPlayer()
    game = pypong.Game(player_left, player_right, configuration)
    cycles=0
    # Main game loop
    timestamp = 1
    while game.running and cycles<2000:
        cycles+=1
        if(render):
         clock.tick(60)
        now = pygame.time.get_ticks()
        if timestamp > 0 and timestamp < now:
            timestamp = now + 5000
            #print clock.get_fps()
        input_state['key'] = pygame.key.get_pressed()
        input_state['mouse'] = pygame.mouse.get_pos()

        game.update()

        if(render):
         game.draw(output_surface)
         #~ pygame.surfarray.pixels_alpha(output_surface)[:,::2] = 12
         display_surface.blit(output_surface, (0,0))
         if debug_surface:
             display_surface.blit(debug_surface, (0,0))
         pygame.display.flip()

         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 game.running = False
             elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 game.running = False
    return game.score_left.score,game.score_right.score    

if __name__ == '__main__': 
 left_player=BasicAIPlayer()
 right_player=BasicAIPlayer()
 print run(left_player,right_player,False)
