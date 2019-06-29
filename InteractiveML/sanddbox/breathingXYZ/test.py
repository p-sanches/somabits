import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# import tmp102

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []


a=0

# # Initialize communication with TMP102
# tmp102.init()

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    global a
    global ani

    # if a==5:
    #     ani.event_source.stop()

    # Read temperature (Celsius) from TMP102
    temp_c = round(3, 2)

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)

    # Limit x and y lists to 20 items
    xs = xs[-5:]
    ys = ys[-5:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

    a+=1

def animate2(i, xs, ys):

    global a
    global ani

    # if a==5:
    #     ani.event_source.stop()

    # Read temperature (Celsius) from TMP102
    temp_c = round(3, 2)

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)

    # Limit x and y lists to 20 items
    xs = xs[-5:]
    ys = ys[-5:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('T12121212121212ver Time')
    plt.ylabel('Temperature (deg C)')

    a+=1



# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, frames=3, fargs=(xs, ys), interval=200)
plt.show()
plt.close()
print("test")


fig2 = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
a=0
ani2 = animation.FuncAnimation(fig2, animate2, fargs=(xs, ys), interval=200)
plt.show()