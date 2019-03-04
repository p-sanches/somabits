# OSC Server using Processing IDE

This is the example server for receiving accelerometer values at address "/acc" over OSC and sending a message to Arduino at address "/led" to turn on/off the built-in LED.

Install Processing using the following link:

` https://processing.org/download/`

Then install <b>OscP5</b> library using Library Manager <b>(Tools > Manage Libraries…)</b>

Change the IP to your PC's IP address and start the server.

After running the server, you will find a screen like this:
![](server.png)

The white circle will change it location based on the <b>X</b> and <b>Y</b> values of the accelerometer. If you click on the screen the led on the Arduino will turn <b>ON</b>. If you click it again it will turn <b>OFF</b>

