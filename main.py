
############################
#Imports
import time 
import ultrasonic_sensor as us
import vibrationmotor as vib
import DHT11 as weather
import WS2812B as LED
import ADC as micldr
import buzzer as play
from time import ticks_ms

# MQTT imports
from umqttsimple import MQTTClient
from credentials import credentials

###########################
#Global variables


###########################
#Variables for later use
temp_passed = 0
hum_passed = 0
light_passed = 0
mic_passed = 0


####################################################################################################
# MQTT

mqtt_server = credentials['mqtt_server']
client_id = credentials['client_id']
MQTT_TOPIC = 'mqtt_sensordata'

mqtt_start_ms = ticks_ms()

# ----------------------------------------
# MQTT methods

# Based on https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
def sub_cb(topic, msg):
  print((topic, msg))


# Taken from https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
def mqtt_connect(topic_sub):
  global client_id, mqtt_server
  
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client


# Responsible for trying to send a message to MQTT-server when called. Takes a message and mqtt topic as arguments.
def send_message(msg, topic, client: MQTTClient):
    try:
        # client.connect()
        client.publish(topic, msg)
        print(f"[MQTT] Topic: {topic} | Message: {msg}")
    except OSError as error:
        print(error)
        print(f"[MQTT] Message not sent. Topic: {topic} | Message: {msg}")



# ----------------------------------------
# Connect to MQTT

try:
    print("[MQTT] Connecting to broker...")
    mqtt_client = mqtt_connect(MQTT_TOPIC)
    vib.vibrate()
    play.success_melody()
except Exception as e:
    print(f"[MQTT] Connection failed: {e}")
    play.failure_melody()
    vib.vibrate(0.6)


####################################################################################################

#############
#Temperature and Humidity check
def temp_hum_check(timer = 0.5):
    global temp_passed
    global hum_passed
    if 19 < temp < 22:
        LED.fade_color(LED.last_color , ( 0, 80 , 0) )
        vib.vibrate()
        print(f"Just right. {temp}")
        temp_passed = 1
        play.success_melody()
    elif temp < 19:
        LED.fade_color(LED.last_color , ( 0, 0 , 80) )
        print(temp)
        print(f"Too cold! {temp}")
        temp_passed = 0
    else:
        LED.fade_color(LED.last_color , ( 80, 0 , 0) )
        print(f"Too warm! {temp}")
        temp_passed = 0
    LED.fade_color_flash()
    time.sleep(timer)
    
    
    if 30 < hum < 50:
        LED.fade_color(LED.last_color , ( 0, 80 , 0) )
        print(f"Humidity OK. {hum}")
        vib.vibrate()
        hum_passed = 1
        play.success_melody()
    elif hum < 30:
        LED.fade_color(LED.last_color , ( 80 , 0 ,  0) )
        print(hum)
        print(f"Too dry! {hum}")
        hum_passed = 0
    else:
        LED.fade_color(LED.last_color , ( 0 , 0 , 80) )
        print(hum)
        print(f"Too humid! {hum}")
        hum_passed = 0
    time.sleep(timer)
###############################
#Second function for dark mode of above checks (Less bright.)
def temp_hum_check_dark(timer = 0.5):
    global temp_passed
    global hum_passed
    if 19 < temp < 22:
        LED.fade_color(LED.last_color , ( 0, 20 , 0) )
        print(f"Temperature OK. {temp}")
        vib.vibrate()
        temp_passed = 1
        play.success_melody()
    elif temp < 19:
        LED.fade_color(LED.last_color , ( 0, 0 , 20) )
        print(temp)
        print(f"Too cold! {temp}")
        temp_passed = 0
    else:
        LED.fade_color(LED.last_color , ( 20, 0 , 0) )
        print(f"Too warm! {temp}")
        temp_passed = 0
    LED.fade_color_flash((20,4,0))
    time.sleep(timer)
    
    if 30 < hum < 50:
        LED.fade_color(LED.last_color , ( 0, 20 , 0) )
        print(f"Humidity is OK! {hum}")
        vib.vibrate()
        hum_passed = 1
        play.success_melody()
    elif hum < 30:
        LED.fade_color(LED.last_color , ( 20 , 0 ,  0) )
        print(f"Too dry! {hum}")
        hum_passed = 0
    else:
        LED.fade_color(LED.last_color , ( 0 , 0 , 20) )
        print(hum)
        print(f"Too humid! {hum}")
        hum_passed = 0
    time.sleep(timer)
    

#################################
#Checks light and mic ADC values
def light_mic_check(timer = 0.5):
    global light_passed
    global mic_passed
    lux = micldr.read_lux()
    mic_val = micldr.adc_to_db()
    if lux < 20:
        print(f"Optimal light level! {lux}")
        vib.vibrate()
        LED.fade_color_flash((0,0,20))
        LED.fade_color_flash((0,0,20))
        light_passed = 1
    else:
        print(f"Lower the light level for optimal sleep! {lux}")
        LED.fade_color(LED.last_color , ( 80 , 80 , 80) )
        light_passed = 0
        
    if mic_val <= 30 and micldr.on_off == 1:
        print(f"Current average mic level: {mic_val}")
        vib.vibrate()
        mic_passed = 1
    else:
        print(f"Current average mic level: {mic_val}")
        mic_passed = 0
    time.sleep(timer)
    
##################################
#To check for perfect sleep conditions
def sleep_condition():
    number_satisfied = 0 + light_passed + temp_passed + hum_passed + mic_passed
    if number_satisfied == 4 and on_off == 1:
        print(f"Total satisfaction:{number_satisfied} out of 4")
        LED.fade_color_flash((0,0,100))
        LED.fade_color_flash((0,0,100))
        play.success_melody
        vib.vibrate()
        time.sleep(0.5)
        vib.vibrate()
        print("Perfect condition!")
    elif number_satisfied == 3 and on_off == 0:
        print(f"Total satisfaction:{number_satisfied} out of 3")
        play.success_melody
        vib.vibrate()
        time.sleep(0.5)
        vib.vibrate()
        print("Perfect condition, sound not measured!")
    else:
        print("Conditions for a good sleep not met.")
        play.failure_melody()
        LED.fade_color_flash((100,0,0))
        LED.fade_color_flash((100,0,0))

        
##########################
#Unpacking / creating the variables for startup use





vib.vibrate()


#########################
#Main loop, uses the different features on the board for sleep condition monitoring
try:
    micldr.microphone_on_off()
    while True:
        # Unpacking / creating temp and hum variables for use in functions
        
        temp, hum = weather.DHT11_READ()
        # If too bright, use bright LED
        if micldr.read_lux() > 200: 
            LED.fade_color(LED.last_color , (120, 100 ,0) )
            bright = True
            # If too dark, use weaker values to avoid waking user
        else: 
            LED.fade_color(LED.last_color , (30, 16 ,0) )
            bright = False
# For interacting with unit, 15 cm or under solution to trigger in darkmode
#Runs checks on different features and displays status using colored LED.
        if 30 < us.read_distance() < 50:
            global on_off
            vib.vibrate()
            on_off = micldr.microphone_on_off()
            print(on_off)
            time.sleep(0.5)
            


        if 0 < us.read_distance() < 15 and bright == False: 
            vib.vibrate()
            print("Low light level!")
            previous_color = LED.last_color
            LED.fade_color(LED.last_color , (20, 4 ,0) )
            temp_hum_check_dark()
            LED.fade_color_flash((20,4,0))
            light_mic_check()
            LED.fade_color(LED.last_color , previous_color )
            sleep_condition()

 # For interacting with unit, 15 cm or under solution to trigger in bright mode
 #Runs checks on different features and displays status using colored LED.
        elif 0 < us.read_distance() < 15:
            print("Bright light level!")
            vib.vibrate()
            previous_color = LED.last_color
            LED.fade_color(LED.last_color , (160, 40 ,0) )
            temp_hum_check()
            LED.fade_color_flash()
            light_mic_check()
            LED.fade_color_flash()
            LED.fade_color(LED.last_color , previous_color )
            sleep_condition()
            
            # If not under 15cm, repeat loop
        else:
            pass
        #To allow escape from Loop incase of bad code
        
        
        #------------------------
        # Send sensordata over MQTT
        
            MQTT_DELAY_MS = 10000
        try:
        
            if ticks_ms() - mqtt_start_ms > MQTT_DELAY_MS: # Non breaking delay for sending MQTT data.
                mqtt_start_ms = ticks_ms()
            
                mic_, _ = micldr.read_adc()
                temp_, hum_ = weather.DHT11_READ()
            
                light_lux = micldr.read_lux()
                mic_db = micldr.adc_to_db()
            
                data = [temp_, hum_, mic_db, light_lux]
                data_string = str(data)
            
            #print(f"read_db: {mic_db}")
                send_message(data_string, MQTT_TOPIC, mqtt_client)
        except:
            pass

            
            
except KeyboardInterrupt:
    play.failure_melody()
    LED.fade_color(LED.last_color , (0, 0 ,0) )
    print("Exiting loop. Good day!")
    
    
        
        
        
        
        
    




