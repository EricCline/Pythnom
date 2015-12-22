import os, pygame
from pygame.locals import *
from random import randint
import pickle


def open_file(name):
    """loads a txt file"""
    fullname = os.path.join('data', name)
    return open(fullname)


def load_image(name, colorkey = None):
    """loads an image and converts it to pixels. raises an exception if image not found"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    # set the colorkey to be the color of the top left pixel
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    """loads a sound. raises an exception if not found"""
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound

def check_high_scores():
    global current_length
    highscores = open(os.path.join('data', 'highscores'))
    score_list = pickle.load(highscores)
    highscores.close()
    for i in range(0, 10):
        if current_length > score_list[i]:
            score_list.insert(i, current_length)
            score_list.pop()

            break
    print score_list
    highscores = open(os.path.join('data', 'highscores'), 'wb')
    pickle.dump(score_list, highscores)
    highscores.close()


def manage_events():
    global snake_bits
    global snake
    global current_length
    global delay

    #wall collisions
    if (snake_bits[0].rect.top < 0 or
        snake_bits[0].rect.bottom > 480 or
        snake_bits[0].rect.left < 0 or
        snake_bits[0].rect.right > 640):
        check_high_scores()
        current_length = 1
        crash_sound.play()
        snakesprites.empty()
        snake_bits = [snake]
        snakesprites.add(snake)
        snake.start()
        delay = 120

    #eat an apple!
    if snake_bits[0].rect.contains(apple.rect):
        new_bit = SnakeBit()
        snake_bits.append(new_bit)
        new_bit.add(snakesprites)
        apple.update()
        nom_sound.play()
        current_length += 1
        delay -= 1

    #snake eats itself!!!
    for i in range(1, len(snake_bits)):
        if snake_bits[0].rect == snake_bits[i].rect:
            check_high_scores()
            current_length = 1
            crash_sound.play()
            snakesprites.empty()
            snake_bits = [snake]
            snakesprites.add(snake)
            snake.start()
            delay = 120
            break #essential because we don't want to iterate again if True


class Apple(pygame.sprite.Sprite):
    """create an apple in a random spot"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('apple.png', -1)
        self.update()

    def update(self):
        self.posx = randint(1, 31)*20
        self.posy = randint(1, 21)*20
        self.pos = self.posx, self.posy
        self.rect.center = self.pos
        #prevent the apple from appearing inside the snake
        for i in range(0, len(snake_bits)):
            if self.rect == snake_bits[i].rect:
                self.update()


class SnakeBit(pygame.sprite.Sprite):
    """create the snake"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('snakebit.png')
        self.start()

    def start(self):
        self.posx = 320
        self.posy = 240
        self.pos = self.posx, self.posy
        self.rect.center = self.pos
        self.direction = 'left'

    def update(self):
        if len(snake_bits) > 1:
            snake_bits.insert(0, snake_bits.pop())
            old_front = snake_bits[1].rect
            new_front = snake_bits[0].rect
            if self.direction == 'left':
                new_front.x = old_front.x - 20
                new_front.y = old_front.y
            if self.direction == 'right':
                new_front.x = old_front.x + 20
                new_front.y = old_front.y
            if self.direction == 'up':
                new_front.y = old_front.y - 20
                new_front.x = old_front.x
            if self.direction == 'down':
                new_front.y = old_front.y + 20
                new_front.x = old_front.x

        if len(snake_bits) == 1:
            if self.direction == 'left':
                self.posx -= 20
            if self.direction == 'right':
                self.posx += 20
            if self.direction == 'up':
                self.posy -= 20
            if self.direction == 'down':
                self.posy += 20

            self.pos = self.posx, self.posy
            self.rect.center = self.pos


class Score(pygame.sprite.Sprite):
    """score contained in sprite to prevent text overwriting"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('white')
        self.last_length = 0
        self.update()

    def update(self):
        global current_length

        if current_length != self.last_length:
            self.font = pygame.font.Font(None, 20)
            self.font.set_italic(1)
            self.color = Color('white')
            self.last_length = current_length
            msg = "Length: %d" % (current_length)
            self.image = self.font.render(msg, 0, self.color)
            self.rect = self.image.get_rect().move(10, 450)


if __name__ == '__main__':
    pygame.init()

    #globals
    clock = pygame.time.Clock()
    done = False
    current_length = 1
    delay = 120

    #create window
    pygame.event.set_grab(1)
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('PYTHNOM')
    pygame.mouse.set_visible(0)

    #load background and sounds
    background = pygame.Surface(screen.get_size())
    background, _ = load_image('grass.jpg')
    crash_sound = load_sound('crash.wav')
    nom_sound = load_sound('nom.wav')

    #create snake and apple, order is important.  apple.init uses snake_bits
    snake = SnakeBit()
    snake_bits = [snake]
    apple = Apple()

    #create score sprite
    score = Score()

    #sprite groups
    applesprite = pygame.sprite.RenderPlain((apple))
    snakesprites = pygame.sprite.RenderPlain((snake))
    scoresprite = pygame.sprite.RenderPlain((score))


    #GAME LOOP
    while done == False:
        clock.tick(60) # set our max framerate
        for e in pygame.event.get():
            if e.type == KEYUP:
                if e.key == K_ESCAPE:
                    done = True
            if e.type == KEYDOWN:
                if e.key == K_UP and snake.direction != 'down':
                    snake.direction = 'up'
                    break
                if e.key == K_DOWN and snake.direction != 'up':
                    snake.direction = 'down'
                    break
                if e.key == K_LEFT and snake.direction != 'right':
                    snake.direction = 'left'
                    break
                if e.key == K_RIGHT and snake.direction != 'left':
                    snake.direction = 'right'
                    break

        #check for collisions
        manage_events()

        #pause increment
        pygame.time.delay(delay)

        #update sprites
        snake.update()
        score.update()

        screen.blit(background, (0,0))
        applesprite.draw(screen)
        snakesprites.draw(screen)
        scoresprite.draw(screen)
        pygame.display.update()
