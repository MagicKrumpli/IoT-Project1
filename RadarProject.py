import time
import pygame
import math
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor

# GPIO Pins
TRIG = 4  # Trigger pin
ECHO = 17  # Echo pin
SERVO_PIN = 18  # Servo motor pin

# Initialize Distance Sensor
sensor = DistanceSensor(echo=ECHO, trigger=TRIG)

# Setup Servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Pygame Initialization
pygame.init()
WIDTH, HEIGHT = 800, 600  # Increase radar size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultrasonic Radar")
clock = pygame.time.Clock()

# Radar Colors
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (0, 150, 0)
RADAR_COLOR = (0, 255, 0)
OBJECT_COLOR = (255, 0, 0)
#VIEW_ANGLE = 90  # Radar viewing angle in degrees


def set_angle(angle):
    # duty = 2 + (angle / 18)
    # pwm.ChangeDutyCycle(duty)
    # time.sleep(0.02)
    
    duty = max(2.0, min(12.5, 2 + (angle / 18)))  # Ensure duty cycle is between 2.0 and 12.5
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.02)
    GPIO.output(SERVO_PIN, False)
    time.sleep(0.02)

def get_distance():
    distance = sensor.distance * 100  # Convert meters to cm
    return max(2, min(500, distance))  # Limit range

def draw_grid():
    center = (WIDTH // 2, HEIGHT - 100)
    # draw 6 circles
    pygame.draw.circle(screen, GRID_COLOR, center, 60, 1)
    pygame.draw.circle(screen, GRID_COLOR, center, 120, 1)
    pygame.draw.circle(screen, GRID_COLOR, center, 180, 1)
    pygame.draw.circle(screen, GRID_COLOR, center, 240, 1)
    pygame.draw.circle(screen, GRID_COLOR, center, 300, 1)
    pygame.draw.circle(screen, GRID_COLOR, center, 360, 1)
    
    # draw horizontal and vertical lines
    pygame.draw.line(screen, GRID_COLOR, (center[0] - 360, center[1]), (center[0] + 360, center[1]), 1)
    pygame.draw.line(screen, GRID_COLOR, (center[0], center[1] - 360), (center[0], center[1]), 1)
    
    # draw diagonal lines (45-degree)
    pygame.draw.line(screen, GRID_COLOR, (center[0], center[1]), (center[0] - 255, center[1] - 255), 1)
    pygame.draw.line(screen, GRID_COLOR, (center[0], center[1]), (center[0] + 255, center[1] - 255), 1)
    

def draw_radar(angle, distance):
    screen.fill(BACKGROUND_COLOR)
    draw_grid()
    center = (WIDTH // 2, HEIGHT - 100)
    
    # Convert angle to position for detected object
    rad = math.radians(angle) 
    x_obj = center[0] + distance * math.cos(rad) * 4
    y_obj = center[1] - distance * math.sin(rad) * 4
    
        
    # Draw moving lines
    x_line = center[0] + 360 * math.cos(rad)
    y_line = center[1] - 360 * math.sin(rad)
    
    
    # Only draw object if within radar range (360 pixels radius)
    if math.sqrt((x_obj - center[0])**2 + (y_obj - center[1])**2) <= 360:
        pygame.draw.circle(screen, OBJECT_COLOR, (int(x_obj), int(y_obj)), 10) # red circle (object)
        pygame.draw.line(screen, OBJECT_COLOR, center, (int(x_line), int(y_line)), 4)  # Red line 
    else:
        pygame.draw.line(screen, RADAR_COLOR, center, (int(x_line), int(y_line)), 4)
    
    pygame.display.update()
    

def main():
    running = True
    #angle = -VIEW_ANGLE // 2  # Start at leftmost view angle
    angle = 0
    direction = 1
    
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            set_angle(angle)
            time.sleep(0.01)  # Allow servo to move before measuring
            distance = get_distance()
            draw_radar(angle, distance)
            
            angle += direction * 5  # Smaller steps for smoother motion
            if angle >= 180 or angle <= 0:
                direction *= -1
            # if angle >= VIEW_ANGLE // 2 or angle <= -VIEW_ANGLE // 2:
                # direction *= -1
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        pygame.quit()
        print("Radar Stopped")

if __name__ == "__main__":
    main()
