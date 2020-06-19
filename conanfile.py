import os
from conans import ConanFile, CMake, tools


class CppAdConan(ConanFile):
    name = "cppad"
    description = "A C++ Algorithmic Differentiation Package."
    url = "https://github.com/coin-or/CppAD"
    homepage = "https://coin-or.github.io/CppAD/doc"
    topics = ("math", "algorithm")
    license = "EPL-2.0,GPL-2.0-or-later"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               }
    default_options = {"shared": True,
                       "fPIC": True,
                       }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        archive_name = f'CppAD-{self.version}'
        os.rename(archive_name, self._source_subfolder)
        if tools.Version(str(self.version)) > '20150000.9':
            tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'), 
                'DIRECTORY "${CMAKE_SOURCE_DIR}/include/cppad/"', 'DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include/cppad/"')
            for example in ['bthread', 'openmp', 'pthread']:
                tools.replace_in_file(os.path.join(self._source_subfolder, 'example', 'multi_thread', example, 'CMakeLists.txt'), 
                    '${CMAKE_SOURCE_DIR}/speed/src/microsoft_timer.cpp', '${CMAKE_CURRENT_SOURCE_DIR}/../../../speed/src/microsoft_timer.cpp')

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["cppad_tape_id_type"] = 'size_t'
        self._cmake.definitions["cppad_tape_addr_type"] = 'size_t'
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
