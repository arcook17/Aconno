import csv
import numpy as np
from scipy import integrate
from datetime import datetime, timedelta
#import itertools

with open('Rotating', 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line for line in stripped if line)
    with open('ext_aconno_stream_no_movement.csv', 'w', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(('Time Stamp','X Acceleration','Y Acceleration','Z Acceleration','X Velocity','Y Velocity','Z Velocity','X Position', 'Y Position', 'Z Position'))

        #Create variables to recognize when notifications are enabled for each acceleration service
        acc_enabled = 0

        #Create empty acceleration lists
        x_acc, y_acc, z_acc = [],[],[];

        #Create timestamp for x,y,z
        acc_times = []
        g = 9.81
        time_string, out_string_x, out_string_y, out_string_z = '','','',''

        for line in lines:
            line = line.strip()

            # Check for receiving values
            if line.find('Notifications enabled for 00005283-0000-1000-8000-00805f9b34fb') != -1:
                acc_enabled = 1


            # Start recording once receiving receiving acceleration values
            if acc_enabled == 1:

                if line.find('received from 00005283') != -1:

                    out_string_x = line[88:90]  #0x
                    out_string_y = line[88:90]  #0x
                    out_string_z = line[88:90]  #0x

                    out_string_x += line[92:94]
                    out_string_x += line[95:97]

                    out_string_y += line[98:100]
                    out_string_y += line[101:103]

                    out_string_z += line[104:106]
                    out_string_z += line[107:109]

                    #acc_times.append(line[2:14])
                    if acc_times == []:
                        time_start = timedelta(hours=float(line[2:4]), minutes=float(line[5:7]), seconds=float(line[8:10]), milliseconds=float(line[11:14]))
                        print(time_start)
                        #time_start = float(line[8:14])
                        print("Time Start: ",time_start)

                    #acc_times.append(float(line[8:14]))
                    acc_times.append(timedelta(hours=float(line[2:4]), minutes=float(line[5:7]), seconds=float(line[8:10]), milliseconds=float(line[11:14])))

                    # function to transform hex string like "0xff4c" into signed integer
                    def hexStrToInt(hexstr):
                        val = int(hexstr, 16)           # convert to unsigned
                        if ((val & 0x8000) == 0x8000):  # check sign bit
                            val = -((val ^ 0xffff) + 1) # if set, inver and add one to get the negative value, then add the negative sign
                        return val

                    x_acc.append(float(hexStrToInt(out_string_x)) * (0.061/1000)*g)
                    y_acc.append(float(hexStrToInt(out_string_y)) * (0.061/1000)*g)
                    z_acc.append(float(hexStrToInt(out_string_z)) * (0.061/1000)*g)

                    out_string_x, out_string_y,out_string_z = '','',''


        time_end = acc_times[-1]
        print("Time End:   ",time_end)

        # Check to make sure lengths are equal
        if len(x_acc) != len(y_acc) != len(z_acc):
            print("Acceleration lengths don't match",'\n')
            acc_data_good = 0
        else:
            print("Acceleration Data is equal length",'\n')
            acc_data_good = 1


        print("Timestamp (seconds): ",acc_times)

        print("X acceleration:", x_acc)
        print("Y acceleration:", y_acc)
        print("Z acceleration:", z_acc,'\n')



        # ------------------------------------------------------
        # Integrate Acceleration

        # Create empty acceleration lists
        vel_x, vel_y, vel_z= np.array([]),np.array([]),np.array([]);
        velocity_x, velocity_y, velocity_z = np.array([]),np.array([]),np.array([]);
        position_x, position_y, position_z = np.array([]),np.array([]),np.array([]);

        time_vec = np.array(acc_times)
        vel_x = np.array(x_acc)
        vel_y = np.array(y_acc)
        vel_z = np.array(z_acc)

        n_start = 0
        n_end = len(vel_z)

        interv_to_int = (np.linspace(n_start, n_end, n_end - n_start + 1, dtype=int))
        interv_to_int = interv_to_int[0:len(interv_to_int) - 2]

        print("1g is approximately: ",np.mean(vel_z[0:15]))

        vel_x = vel_x[interv_to_int] - np.mean(vel_x[0:15])
        vel_y = vel_y[interv_to_int] - np.mean(vel_y[0:15])
        vel_z = vel_z[interv_to_int] - np.mean(vel_z[0:15]) # value - approximate 1g

        #conv_size = 10

        #vel_z = np.convolve(vel_z, np.ones(conv_size), 'same') / conv_size

        total_seconds = (time_end - time_start) / timedelta(seconds=1)
        time_vec = time_vec[interv_to_int]
        #print(time_end.total_seconds(),time_start.total_seconds())

        delta_x = np.mean(np.diff(time_vec)) #average time between samples
        delta_y = delta_x
        delta_z = delta_x

        print("delta_z: ",delta_z)
        # dx = delta_x.total_seconds()
        # dy = delta_y.total_seconds()
        # dz = delta_z.total_seconds()
        dx, dy, dz = total_seconds,total_seconds,total_seconds
        print("total seconds: ", dz,'\n')
        print(abs(vel_x[0]))

        velocity_x = integrate.cumtrapz(vel_x) - vel_x[0]# * dx
        velocity_y = integrate.cumtrapz(vel_y)# * dy
        velocity_z = integrate.cumtrapz(vel_z)# * dz

        #velocity_x = integrate.simps(vel_x,interv_to_int,dx)
        # velocity_y = integrate.simps(vel_y,interv_to_int,dy)
        # velocity_z = integrate.simps(vel_z,interv_to_int,dz)
        # print("velocity in x: ", velocity_x,'\n')
        # print("velocity in y: ", velocity_y, '\n')
        # print("velocity in z: ", velocity_z, '\n')


        position_x = integrate.cumtrapz(velocity_x) * dx
        position_y = integrate.cumtrapz(velocity_y) * dy
        position_z = integrate.cumtrapz(velocity_z) * dz
        #print("position_z: ", position_z)

        # dist_x = np.trapz(vel_x) * dx
        # dist_y = np.trapz(vel_y) * dy
        # dist_z = np.trapz(vel_z) * dz

        # ------------------------------------------------------
        # Write to CSV file
        if acc_data_good == 1:
            for acc_time, x_acc_f, y_acc_f, z_acc_f, velocity_x_f, velocity_y_f, velocity_z_f, position_x_f, position_y_f, position_z_f in zip(
                    acc_times, x_acc, y_acc, z_acc, velocity_x, velocity_y, velocity_z, position_x, position_y, position_z):
                grouped = acc_time/timedelta(seconds=1)-time_start/timedelta(seconds=1), x_acc_f, y_acc_f, z_acc_f, velocity_x_f, velocity_y_f, velocity_z_f, position_x_f, position_y_f, position_z_f
                writer.writerow(grouped)

