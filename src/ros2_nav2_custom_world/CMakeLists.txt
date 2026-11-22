cmake_minimum_required(VERSION 3.8)
project(ros2_nav2_custom_world)

find_package(ament_cmake REQUIRED)

# The repository keeps its editable launch and SDF files at the workspace root.
# Install those same files as resources of this overlay package.
get_filename_component(workspace_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
install(DIRECTORY "${workspace_root}/launch/" DESTINATION "share/${PROJECT_NAME}/launch")
install(DIRECTORY "${workspace_root}/worlds/" DESTINATION "share/${PROJECT_NAME}/worlds")
install(DIRECTORY "${workspace_root}/rviz/" DESTINATION "share/${PROJECT_NAME}/rviz")
install(FILES "${workspace_root}/config/waffle_nav2.yaml" DESTINATION "share/${PROJECT_NAME}/config")
install(FILES "${workspace_root}/maps/maze_5x5.yaml" "${workspace_root}/maps/maze_5x5.pgm"
  DESTINATION "share/${PROJECT_NAME}/maps")

ament_package()
