# Aconno

The most up to date file is the Data_Parse_csv.py file

Currently it parses the incoming log file (ex. "Rotating")

Then it essentially calculates velocity and position using the following method,

        for acc_x, acc_y, acc_z in zip(vel_x, vel_y, vel_z):
            velocity_x.append(velocity_x[-1] + acc_x * delta_x)
            velocity_y.append(velocity_y[-1] + acc_y * delta_y)
            velocity_z.append(velocity_z[-1] + acc_z * delta_z)
        del velocity_x[0],velocity_y[0],velocity_z[0]
        
        for v_x,v_y,v_z in zip(velocity_x,velocity_y,velocity_z):
            position_x.append(position_x[-1] + v_x * delta_x)
            position_y.append(position_y[-1] + v_y * delta_y)
            position_z.append(position_z[-1] + v_z * delta_z)
        del position_x[0],position_y[0],position_z[0]
        
 Then writes the data to a csv file
 Then plots it
