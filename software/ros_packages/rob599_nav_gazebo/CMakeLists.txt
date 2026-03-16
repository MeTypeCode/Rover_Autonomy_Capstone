cmake_minimum_required(VERSION 3.8)
project(rob599_nav_gazebo)
set(lib_name ${PROJECT_NAME})

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

#find dependancies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(nav2_voxel_grid REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(laser_geometry REQUIRED)
find_package(PCL REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(pcl_ros REQUIRED)

add_library(${lib_name} SHARED
  src/volumetric_layer.cpp
  src/elevation_layer.cpp
  # src/clearance_layer.cpp
)

ament_target_dependencies(${lib_name}
  rclcpp
  pluginlib
  nav2_costmap_2d
  nav2_msgs
  nav2_voxel_grid
  nav_msgs
  sensor_msgs
  laser_geometry
  pcl_conversions
  pcl_ros
)

pluginlib_export_plugin_description_file(
  nav2_costmap_2d
  volumetriclayer.xml
)

install(
  TARGETS ${lib_name}
  LIBRARY DESTINATION lib
)

install(
  FILES volumetriclayer.xml
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

target_link_libraries(${lib_name}
  ${PCL_LIBRARIES}
)

# Export plugins
pluginlib_export_plugin_description_file(nav2_costmap_2d volumetriclayer.xml)
pluginlib_export_plugin_description_file(nav2_costmap_2d elevationlayer.xml)
# pluginlib_export_plugin_description_file(nav2_costmap_2d clearancelayer.xml)

# Install launch + configs
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

# Install headers
install(DIRECTORY include/
  DESTINATION include
)

# Install plugin xml
install(FILES
  volumetriclayer.xml
  elevationlayer.xml
  # clearancelayer.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_package()