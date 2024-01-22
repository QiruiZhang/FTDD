cmake_minimum_required(VERSION 3.10)

project(cTDD)
set(CMAKE_CXX_STANDARD 20)
set(PYBIND11_PYTHON_VERSION 3.8)
set(CMAKE_CXX_FLAGS "-Wall -Wextra -fPIC")

find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)

pybind11_add_module(${PROJECT_NAME} cTDD.cpp)

target_compile_definitions(${PROJECT_NAME} PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
target_include_directories(${PROJECT_NAME} PRIVATE ${PYBIND11_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE Eigen3::Eigen)



# add the executable
# add_executable(${PROJECT_NAME} main.cpp)
# target_include_directories( ${PROJECT_NAME} PRIVATE)
# target_link_libraries(${PROJECT_NAME} PRIVATE Eigen3::Eigen)
