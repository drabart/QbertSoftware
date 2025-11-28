import pyrealsense2 as rs

ctx = rs.context()

for dev in ctx.query_devices():
    print("Device:", dev.get_info(rs.camera_info.name))
    
    for sensor in dev.query_sensors():
        print(" Sensor:", sensor.get_info(rs.camera_info.name))

        for profile in sensor.get_stream_profiles():
            v = profile.as_video_stream_profile()
            print("  Stream:", v.stream_type(), 
                  "Format:", v.format(),
                  "Resolution:", f"{v.width()}x{v.height()}",
                  "FPS:", v.fps())
            