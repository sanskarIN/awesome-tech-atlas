# CMake Tutorial

**Official source:** https://cmake.org/cmake/help/latest/guide/tutorial/index.html  
**Type:** official guide  
**Category:** [Developer tools](../categories/developer-tools.md) · Native C and C++ build configuration  
**Last official-page inspection:** 2026-11-16

## Why it matters

CMake configures native projects and generates build files for the chosen generator. Its official tutorial uses progressive exercises to introduce executables, libraries, target settings, cache variables, testing and installation. It is a useful starting point for a C or C++ project needing a reproducible build description.

## Good fit

- Learning how to define a library or executable target instead of relying on manual compilation commands.
- Understanding separate configure and build steps before moving a native application into CI.
- Comparing build generators, target settings, CTest and presets against a project's requirements.

## Strength and trade-off

- **Strength:** The upstream tutorial organizes common build-system concepts as small exercises.
- **Limitation:** CMake is not a compiler. You still need a suitable compiler and generator/build tool; single-configuration and multi-configuration generators differ. The live `latest` tutorial can change between revisions.

These are selection notes, not a build-performance benchmark or a compatibility guarantee.

## Try it

Read [the official tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) from the introductory step. With CMake and a compatible C++ toolchain **already installed**, create a disposable `CMakeLists.txt`:

~~~cmake
cmake_minimum_required(VERSION 3.15)
project(AtlasHello LANGUAGES CXX)
add_executable(atlas_hello main.cpp)
~~~

Add a tiny original `main.cpp` that prints a message. From the project directory, try `cmake -S . -B build` and `cmake --build build`. Consult the tutorial for generator/toolchain configuration if a required compiler is absent. **This example was not executed during the source review.**

## Where to go next

- Continue through the [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) sections on libraries, target properties, tests and installation.
- **Alternative:** [GNU GDB](gdb.md) explains debugging a built native executable; [Git](git.md) covers version history. Neither is a replacement for build configuration.

**Verification scope:** The official CMake tutorial index and exercise outline were inspected on 2026-11-16. No executable build, platform-specific generator, or compiler installation was independently tested.
