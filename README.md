# Dahua_IP_Camera_Motion_Detect
 External Python program that gets feed of Dahua IP Camera by using local ip, username and password and processing frame data to track motion (/or thumbs up for special purposes)
 
# How to use
Fill ipCamIPv4, ipCamUsername and ipCamPassword parameters with your credentials

# Can i hide camera feed window?
Sure. just set False 'showCameraFeedInWindow' param

# Which tracking methods is it track?
Program support both motion detect and thumbs up gesture for fun purpose only

# Does it process only at one camera feed?
For now yes, could be multiple however

# What if i want it to move detect everything or big movements?
Just change motion_threshold parameter. Lower means more sensitive. Bigger value is for big movements

# Which library/framworks used?
OpenCV for motion tracking, mediapipe for hand tracking & drawing

# What the heck is Timeout parameter??
It used to check last time it triggered. Within that timeout time, it does not print the statement (motion or thumbs up detection)

# Why not to use SmartPSS / Camera's own triggers?
I needed a python shit to do afterwards. Actually, i built this program within 1-2 hour to send a WhatsApp message to my friend when i perform thumbs up gesture on Valorant Agent Selection scene. Wait-what? Yep. My mates says me "notify me when it finds a match" every time. Just because my phone is not near when i play Valorant, i had to use a trigger when just sitting on my chair. So i decided to make a thumbs up gesture and notify them :)