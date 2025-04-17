# Temp base cmake
cmake_minimum_required(VERSION 3.14)
#cmake_policy(SET CMP0048 NEW)
project(argparse VERSION 0.9.2.0 LANGUAGES C CXX
        DESCRIPTION "Executable argument input parser utilities" HOMEPAGE_URL "https://github.com/randaleike/argparse")

option(BUILD_SHARED_LIBS "Build using shared libraries" ON)

if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    include(GNUInstallDirs)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
endif()

####
# Gtest setup
####
if(DEFINED ENV{GITHUB_ACTION})
    set(GTEST_GITHUB_REPO https://randaleike:$ENV{GTEST_FETCH}@github.com/google/googletest)
else()
    set(GTEST_GITHUB_REPO https://github.com/google/googletest)
endif()

include(CTest)
include(FetchContent)
FetchContent_Declare(googletest
    GIT_REPOSITORY ${GTEST_GITHUB_REPO}
    GIT_TAG v1.15.2)
if (${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    #set(gtest_force_shared_crt ON CACHE BOOL "Windows use msvcrt.dll" FORCE)
endif()
FetchContent_MakeAvailable(googletest)
set (GTEST_INCLUDE_DIR ${googletest_SOURCE_DIR}/googletest/include)
set (GMOCK_INCLUDE_DIR ${googletest_SOURCE_DIR}/googlemock/include)
set (GTEST_DLL_LIBRARY_PATH ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}/${CMAKE_BUILD_TYPE})
set (GTEST_LIB_LIBRARY_PATH ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/${CMAKE_BUILD_TYPE})
set (GTEST_LIBRARIES GTest::gmock_main GTest::gtest_main)
#message ("googletest_DLL: ${GTEST_DLL_LIBRARY_PATH}")
#message ("googletest_LIB: ${GTEST_LIB_LIBRARY_PATH}")
#message ("googletest BINdir: ${googletest_BINARY_DIR}")
#message ("googletest SRCdir: ${googletest_SOURCE_DIR}")
#LIST (APPEND CMAKE_PROGRAM_PATH ${GTEST_LIB_LIBRARY_PATH})

# Build parser strings
add_subdirectory(output)
