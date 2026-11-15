cmake_minimum_required(VERSION 3.20)
project(Articulaciones LANGUAGES CXX)

add_executable(articulaciones articulaciones.cpp)
target_compile_features(articulaciones PRIVATE cxx_std_17)
set_target_properties(articulaciones PROPERTIES CXX_EXTENSIONS OFF)
if(MSVC)
    target_compile_options(articulaciones PRIVATE /W4 /utf-8)
else()
    target_compile_options(articulaciones PRIVATE -Wall -Wextra -pedantic)
endif()

include(CTest)
if(BUILD_TESTING)
    find_package(Python3 COMPONENTS Interpreter)
    if(Python3_Interpreter_FOUND)
        add_test(NAME articulaciones_oraculo
            COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_articulaciones.py"
                --executable "$<TARGET_FILE:articulaciones>")
    endif()
endif()
