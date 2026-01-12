cmake_minimum_required(VERSION 3.10)
project(qbert_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Generate message interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MoveToPos.action"

  "srv/Motor.srv"
  "srv/MoveWithVel.srv"
  "srv/SetupDrive.srv"
  "srv/GripperState.srv"
)

# Export runtime dependencies for Python
ament_export_dependencies(rosidl_default_runtime)

# Testing (optional)
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
