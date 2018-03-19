import csv
import math
import sys
import numpy as np
import numpy.linalg
import pylablib as py
import matplotlib.pyplot as plt
from scipy import integrate
from datetime import datetime, timedelta


# ---------------------------------------------------------------------
# function to transform hex string like "0xff4c" into signed integer
# ---------------------------------------------------------------------
def hexStrToInt(hexstr):
    val = int(hexstr, 16)           # convert to unsigned
    if ((val & 0x8000) == 0x8000):  # check sign bit
        val = -((val ^ 0xffff) + 1) # if set, inver and add one to get the negative value, then add the negative sign
    return val
# ---------------------------------------------------------------------

def sg_filter(x, m, k=0):
    """
    x = Vector of sample times
    m = Order of the smoothing polynomial
    k = Which derivative
    """
    mid = len(x) / 2
    a = x - x[mid]
    expa = lambda x: map(lambda i: i**x, a)
    A = np.r_[map(expa, range(0,m+1))].transpose()
    Ai = np.linalg.pinv(A)

    return Ai[k]

def smooth(x, y, size=5, order=2, deriv=0):

    if deriv > order:
        raise Exception; "deriv must be <= order"

    n = len(x)
    m = size

    result = np.zeros(n)

    for i in xrange(m, n-m):
        start, end = i - m, i + m + 1
        f = sg_filter(x[start:end], order, deriv)
        result[i] = np.dot(f, y[start:end])

    if deriv > 1:
        result *= math.factorial(deriv)

    return result

def plot(t, plots):
    n = len(plots)

    for i in range(0,n):
        label, data = plots[i]

        plt = py.subplot(n, 1, i+1)
        plt.tick_params(labelsize=8)
        py.grid()
        py.xlim([t[0], t[-1]])
        py.ylabel(label)

        py.plot(t, data, 'k-')

    py.xlabel("Time")

def create_figure(size, order):
    fig = py.figure(figsize=(8,6))
    nth = 'th'
    if order < 4:
        nth = ['st','nd','rd','th'][order-1]

    title = "%s point smoothing" % size
    title += ", %d%s degree polynomial" % (order, nth)

    fig.text(.5, .92, title,
             horizontalalignment='center')

def load(name):
    f = open(name)
    dat = [map(float, x.split(' ')) for x in f]
    f.close()

    xs = [x[0] for x in dat]
    ys = [x[1] for x in dat]

    return np.array(xs), np.array(ys)

def plot_results(data, size, order):
    t, pos = load(data)
    params = (t, pos, size, order)

    plots = [
        ["Position",     pos],
        ["Velocity",     smooth(*params, deriv=1)],
        ["Acceleration", smooth(*params, deriv=2)]
    ]

    create_figure(size, order)
    plot(t, plots)


with open('aconno_stream_4', 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line for line in stripped if line)
    with open('ext_aconno_stream_4.csv', 'w', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(('Time Stamp','X Acceleration','Y Acceleration','Z Acceleration','X Velocity','Y Velocity','Z Velocity','X Position', 'Y Position', 'Z Position'))

        #Create variables to recognize when notifications are enabled for each acceleration service
        acc_enabled = 0

        #Create empty acceleration lists
        x_acc, y_acc, z_acc = [],[],[];

        #Create timestamp for x,y,z
        acc_times = []
        g = 9.81
        out_string_x, out_string_y, out_string_z = '','','';

        for line in lines:
            line = line.strip()

            # Check for receiving values
            if line.find('Notifications enabled for 00005283-0000-1000-8000-00805f9b34fb') != -1:
                acc_enabled = 1

            # Start recording once receiving receiving acceleration values
            if acc_enabled == 1:

                if line.find('received from 00005283') != -1:

                    out_string_x = line[88:90]; out_string_y = line[88:90];out_string_z = line[88:90] #0x

                    out_string_x += line[92:94]
                    out_string_x += line[95:97]

                    out_string_y += line[98:100]
                    out_string_y += line[101:103]

                    out_string_z += line[104:106]
                    out_string_z += line[107:109]


                    if acc_times == []:
                        time_start = timedelta(hours=float(line[2:4]), minutes=float(line[5:7]),
                                               seconds=float(line[8:10]), milliseconds=float(line[11:14]))
                        print("Time Start: ", time_start)

                    acc_times.append(
                        timedelta(hours=float(line[2:4]), minutes=float(line[5:7]), seconds=float(line[8:10]),
                                  milliseconds=float(line[11:14])))

                    if abs(float(hexStrToInt(out_string_x)) * (0.061 / 1000) * g) <= 0.5:
                        x_acc.append(0.00)
                    else:
                        x_acc.append(float(hexStrToInt(out_string_x)) * (0.061 / 1000) * g)
                    #x_acc.append(float(hexStrToInt(out_string_x)) * (0.061 / 1000) * g)
                    y_acc.append(float(hexStrToInt(out_string_y)) * (0.061 / 1000) * g)
                    z_acc.append(float(hexStrToInt(out_string_z)) * (0.061 / 1000) * g)

                    out_string_x, out_string_y,out_string_z = '','',''

        del acc_times[0:4],x_acc[0:4]; del y_acc[0:4]; del z_acc[0:4]  #Delete 0xAAAA values

        time_end = acc_times[-1]
        print("Time End:   ",time_end)

        times = []
        for time in acc_times:
            new_time = (time/timedelta(seconds=1)) - (time_start/timedelta(seconds=1))
            times.append(new_time)

        # Check to make sure lengths are equal
        if len(x_acc) != len(y_acc) != len(z_acc) != len(times):
            print("Acceleration lengths don't match",'\n')
            acc_data_good = 0
        else:
            print("Acceleration Data is equal length",'\n')
            acc_data_good = 1


        print("Timestamp (seconds): ",times)
        print("X acceleration:", x_acc)
        print("Y acceleration:", y_acc)
        print("Z acceleration:", z_acc,'\n')

        # ------------------------------------------------------
        # Integrate Acceleration

        # Create empty acceleration lists
        vel_x, vel_y, vel_z= np.array([]),np.array([]),np.array([]);
        velocity_x, velocity_y, velocity_z = [0],[0],[0];
        position_x, position_y, position_z = [0],[0],[0];



        time_vec = np.array(acc_times)
        vel_x = np.array(x_acc)
        vel_y = np.array(y_acc)
        vel_z = np.array(z_acc)

        n_start = 0
        n_end = len(vel_z)

        interv_to_int = (np.linspace(n_start, n_end, n_end - n_start + 1, dtype=int))
        interv_to_int = interv_to_int[0:len(interv_to_int) - 2]

        print("1g is approximately: ",np.mean(vel_z[5:20]))

        vel_x = vel_x[interv_to_int] - np.mean(vel_x[5:20])
        vel_y = vel_y[interv_to_int] - np.mean(vel_y[5:20])
        vel_z = vel_z[interv_to_int] - np.mean(vel_z[5:20]) # value - approximate 1g


        total_seconds = (time_end - time_start) / timedelta(seconds=1)
        time_vec = time_vec[interv_to_int]

        delta_x = np.mean(np.diff(time_vec)) / timedelta(seconds=1)#average time between samples
        delta_y = delta_x
        delta_z = delta_x

        print("delta_z: ",delta_z)

        dx, dy, dz = total_seconds,total_seconds,total_seconds
        print("total seconds: ", dz,'\n')


        for acc_x, acc_y, acc_z in zip(vel_x, vel_y, vel_z):
            velocity_x.append(velocity_x[-1] + acc_x * delta_x)
            velocity_y.append(velocity_y[-1] + acc_y * delta_y)
            velocity_z.append(velocity_z[-1] + acc_z * delta_z)
        del velocity_x[0],velocity_y[0],velocity_z[0]



        print("velocity in x: ", velocity_x,'\n')
        print("velocity in y: ", velocity_y, '\n')
        print("velocity in z: ", velocity_z, '\n')

        for v_x,v_y,v_z in zip(velocity_x,velocity_y,velocity_z):
            position_x.append(position_x[-1] + v_x * delta_x)
            position_y.append(position_y[-1] + v_y * delta_y)
            position_z.append(position_z[-1] + v_z * delta_z)
        del position_x[0],position_y[0],position_z[0]

        print("position in x: ", position_x, '\n')
        print("position in y: ", position_y, '\n')
        print("position in z: ", position_z, '\n')

        # ------------------------------------------------------
        # Write to CSV file
        if acc_data_good == 1:
            for acc_time, x_acc_f, y_acc_f, z_acc_f, velocity_x_f, velocity_y_f, velocity_z_f, position_x_f, position_y_f, position_z_f in zip(
                    acc_times, x_acc, y_acc, z_acc, velocity_x, velocity_y, velocity_z, position_x, position_y, position_z):
                grouped = acc_time/timedelta(seconds=1)-time_start/timedelta(seconds=1), x_acc_f, y_acc_f, z_acc_f, velocity_x_f, velocity_y_f, velocity_z_f, position_x_f, position_y_f, position_z_f
                writer.writerow(grouped)

        # ------------------------------------------------------
        #Calculate Magnitudes

        Mag_acc, Mag_vel, Mag_pos = [],[],[];

        for  x_acc_f, y_acc_f, z_acc_f, velocity_x_f, velocity_y_f, velocity_z_f, position_x_f, position_y_f, position_z_f in zip(
                    x_acc, y_acc, z_acc, velocity_x, velocity_y, velocity_z, position_x, position_y, position_z):
            Mag_acc.append((x_acc_f**2 + y_acc_f**2 + z_acc_f**2)**(1.0/3.0))
            Mag_vel.append((velocity_x_f**2 + velocity_y_f**2 + velocity_z_f**2)**(1.0/3.0))
            Mag_pos.append((position_x_f**2 + position_y_f**2 + position_z_f**2)**(1.0/3.0))

        print(Mag_acc,'\n',Mag_vel,'\n',Mag_pos)


        # ------------------------------------------------------
        #Plot

        # Check to make sure lengths are equal
        if len(times) != len(x_acc):
            #print("times and acceleration x lengths don't match", '\n', len(times), len(velocity_x), '\n', times,'\n', velocity_x)
            del times[-1]
        else:
            print("times and acceleration x lengths DO match", '\n')


        plt.subplot(3,3,1)
        plt.plot(times, x_acc)
        plt.title("Acceleration")
        plt.ylabel("X")
        plt.ylim(-20,20)

        plt.subplot(3, 3, 4)
        plt.plot(times, y_acc)
        plt.ylabel("Y")
        plt.ylim(-20, 20)

        plt.subplot(3, 3, 7)
        plt.plot(times, z_acc)
        plt.ylabel("Z")
        plt.ylim(-20, 20)
        plt.xlabel("Time")

        # Check to make sure lengths are equal
        if len(times) != len(velocity_x):
            #print("times and velocity x lengths don't match", '\n',len(times),len(velocity_x),'\n',times,'\n',velocity_x)
            del times[-1]
        else:
            print("times and velocity x lengths DO match", '\n')

        plt.subplot(3,3, 2)
        plt.plot(times, velocity_x)
        plt.title("Velocity")

        plt.subplot(3, 3, 5)
        plt.plot(times, velocity_y)
        #plt.title("Y Velocity")

        plt.subplot(3, 3, 8)
        plt.plot(times, velocity_z)
        #plt.title("Z Velocity")
        plt.xlabel("Time")

        plt.subplot(3, 3, 3)
        plt.plot(times, position_x)
        plt.title("Position")

        plt.subplot(3, 3, 6)
        plt.plot(times, position_y)
        #plt.title("Y Position")

        plt.subplot(3, 3, 9)
        plt.plot(times, position_z)
        #plt.title("Z Position")
        plt.xlabel("Time")

        plt.show(block=True)
